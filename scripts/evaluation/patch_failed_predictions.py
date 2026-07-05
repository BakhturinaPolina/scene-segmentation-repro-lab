#!/usr/bin/env python3
"""Patch parse-failed dProse predictions using neighbor consensus and optional overrides.

Tier-3 remediation when API retries cannot recover keys (typically safety blocks).
Assigns BORDER/NOBORDER from parsed neighbors or thinking-prose tail; sets
``manual_fix`` / ``manual_fix_confidence`` on patched rows.

Export: ``--export_json`` / ``--export_csv`` for human review.
Apply: ``--apply --min_confidence medium`` (refreshes ``book_review.json``).

See docs/corpora/DPROSE_CORPUS_SPOT_CHECKS.md § Parse failure remediation.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.runners.run_dprose_batch_corpus import (  # noqa: E402
    DEFAULT_OUTPUT_ROOT,
    merge_predictions,
    predictions_path,
    run_book_review,
)

Confidence = Literal["high", "medium", "low"]
Label = Literal["BORDER", "NOBORDER"]


@dataclass
class PatchPlan:
    key: str
    slug: str
    sentence_index: int
    sentence_text: str
    suggested_label: Label | None
    confidence: Confidence
    method: str
    prev_label: str | None
    next_label: str | None
    parse_error: str | None
    reason: str


def load_predictions_by_index(path: Path) -> dict[int, dict[str, Any]]:
    by_idx: dict[int, dict[str, Any]] = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            idx = row.get("sentence_index")
            if idx is not None:
                by_idx[int(idx)] = row
    return by_idx


def discover_failed_keys(output_root: Path) -> list[str]:
    keys: list[str] = []
    books_dir = output_root / "books"
    for review_path in sorted(books_dir.glob("*/book_review.json")):
        review = json.loads(review_path.read_text(encoding="utf-8"))
        keys.extend(review.get("failed_keys") or [])
    return sorted(keys, key=lambda k: (k.split(":")[0], int(k.split(":")[1])))


def neighbor_label(
    by_idx: dict[int, dict[str, Any]],
    idx: int,
    offset: int,
) -> str | None:
    row = by_idx.get(idx + offset)
    if not row or not row.get("parse_ok"):
        return None
    label = row.get("prediction_label")
    return str(label) if label in {"BORDER", "NOBORDER"} else None


def nearest_labels(
    by_idx: dict[int, dict[str, Any]],
    idx: int,
    *,
    max_distance: int = 5,
) -> tuple[str | None, str | None, int | None, int | None]:
    prev_label = next_label = None
    prev_dist = next_dist = None
    for dist in range(1, max_distance + 1):
        if prev_label is None:
            lab = neighbor_label(by_idx, idx, -dist)
            if lab:
                prev_label = lab
                prev_dist = dist
        if next_label is None:
            lab = neighbor_label(by_idx, idx, dist)
            if lab:
                next_label = lab
                next_dist = dist
        if prev_label and next_label:
            break
    return prev_label, next_label, prev_dist, next_dist


def label_from_prose_tail(raw: str | None) -> Label | None:
    if not raw:
        return None
    tail = raw[-500:]
    if "NOBORDER" in tail and "BORDER" not in tail.replace("NOBORDER", ""):
        return "NOBORDER"
    if tail.rstrip().endswith("NOBORDER") or 'answer NOBORDER' in tail or 'I will answer NOBORDER' in tail:
        return "NOBORDER"
    if "BORDER" in tail[-120:]:
        return "BORDER"
    return None


def suggest_patch(
    row: dict[str, Any],
    by_idx: dict[int, dict[str, Any]],
) -> PatchPlan:
    key = str(row["key"])
    slug, idx_s = key.split(":")
    idx = int(idx_s)
    parse_error = row.get("parse_error")
    prev1 = neighbor_label(by_idx, idx, -1)
    next1 = neighbor_label(by_idx, idx, 1)
    prev_wide, next_wide, prev_dist, next_dist = nearest_labels(by_idx, idx)

    prose_label = label_from_prose_tail(row.get("raw_model_response"))
    if prose_label:
        return PatchPlan(
            key=key,
            slug=slug,
            sentence_index=idx,
            sentence_text=str(row.get("sentence_text_full") or ""),
            suggested_label=prose_label,
            confidence="high",
            method="thinking_prose_tail",
            prev_label=prev1,
            next_label=next1,
            parse_error=parse_error,
            reason="Recovered label from leaked thinking prose in raw_model_response.",
        )

    if prev1 and next1 and prev1 == next1:
        return PatchPlan(
            key=key,
            slug=slug,
            sentence_index=idx,
            sentence_text=str(row.get("sentence_text_full") or ""),
            suggested_label=prev1,  # type: ignore[arg-type]
            confidence="high",
            method="neighbor_agreement",
            prev_label=prev1,
            next_label=next1,
            parse_error=parse_error,
            reason=f"Immediate neighbors agree on {prev1}.",
        )

    if prev_wide and next_wide and prev_wide == next_wide:
        return PatchPlan(
            key=key,
            slug=slug,
            sentence_index=idx,
            sentence_text=str(row.get("sentence_text_full") or ""),
            suggested_label=prev_wide,  # type: ignore[arg-type]
            confidence="medium",
            method="wide_neighbor_agreement",
            prev_label=prev_wide,
            next_label=next_wide,
            parse_error=parse_error,
            reason=(
                f"Nearest parsed neighbors within ±5 agree on {prev_wide} "
                f"(distances {prev_dist}, {next_dist})."
            ),
        )

    if prev1 == "BORDER" and next1 != "BORDER":
        return PatchPlan(
            key=key,
            slug=slug,
            sentence_index=idx,
            sentence_text=str(row.get("sentence_text_full") or ""),
            suggested_label="NOBORDER",
            confidence="medium",
            method="after_border_continuation",
            prev_label=prev1,
            next_label=next1,
            parse_error=parse_error,
            reason="Sentence follows a BORDER; default to scene continuation (NOBORDER).",
        )

    if next1 == "BORDER" and prev1 != "BORDER":
        return PatchPlan(
            key=key,
            slug=slug,
            sentence_index=idx,
            sentence_text=str(row.get("sentence_text_full") or ""),
            suggested_label="NOBORDER",
            confidence="medium",
            method="before_border_continuation",
            prev_label=prev1,
            next_label=next1,
            parse_error=parse_error,
            reason="Sentence precedes a BORDER; likely still same scene (NOBORDER).",
        )

    if prev1 and not next1:
        return PatchPlan(
            key=key,
            slug=slug,
            sentence_index=idx,
            sentence_text=str(row.get("sentence_text_full") or ""),
            suggested_label=prev1,  # type: ignore[arg-type]
            confidence="medium",
            method="prev_only",
            prev_label=prev1,
            next_label=next1,
            parse_error=parse_error,
            reason=f"Only previous parsed neighbor available ({prev1}).",
        )

    if next1 and not prev1:
        return PatchPlan(
            key=key,
            slug=slug,
            sentence_index=idx,
            sentence_text=str(row.get("sentence_text_full") or ""),
            suggested_label=next1,  # type: ignore[arg-type]
            confidence="medium",
            method="next_only",
            prev_label=prev1,
            next_label=next1,
            parse_error=parse_error,
            reason=f"Only next parsed neighbor available ({next1}).",
        )

    fallback: Label = "NOBORDER"
    return PatchPlan(
        key=key,
        slug=slug,
        sentence_index=idx,
        sentence_text=str(row.get("sentence_text_full") or ""),
        suggested_label=fallback,
        confidence="low",
        method="default_noborder",
        prev_label=prev1,
        next_label=next1,
        parse_error=parse_error,
        reason="No reliable parsed neighbors; conservative NOBORDER fallback.",
    )


def load_overrides(path: Path) -> dict[str, dict[str, str]]:
    """Load manual labels from CSV (key,label,reason) or JSON ({\"patches\": [...]})."""
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = payload.get("patches") or payload.get("overrides") or payload
        out: dict[str, dict[str, str]] = {}
        for row in rows:
            key = str(row["key"])
            out[key] = {
                "label": str(row["label"]).upper(),
                "reason": str(row.get("reason") or "Manual override."),
            }
        return out

    out = {}
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            key = str(row["key"]).strip()
            label = str(row["label"]).strip().upper()
            reason = str(row.get("reason") or "Manual override.").strip()
            out[key] = {"label": label, "reason": reason}
    return out


def build_patched_row(
    existing: dict[str, Any],
    *,
    label: Label,
    reason: str,
    method: str,
    confidence: Confidence,
) -> dict[str, Any]:
    patched = dict(existing)
    patched["parse_ok"] = True
    patched["prediction_label"] = label
    patched["prediction_bool"] = label == "BORDER"
    patched["parse_error"] = None
    patched["error"] = None
    patched["raw_model_response"] = json.dumps(
        {"label": label, "reason": reason},
        ensure_ascii=False,
    )
    patched["manual_fix"] = method
    patched["manual_fix_confidence"] = confidence
    if patched.get("usage") is None:
        patched["usage"] = {"prompt_tokens": 0, "output_tokens": 0, "thought_tokens": 0}
    return patched


def confidence_rank(conf: Confidence) -> int:
    return {"high": 3, "medium": 2, "low": 1}[conf]


def collect_plans(
    output_root: Path,
    *,
    keys: list[str] | None,
    overrides: dict[str, dict[str, str]],
) -> list[PatchPlan]:
    plans: list[PatchPlan] = []
    target_keys = keys or discover_failed_keys(output_root)
    by_slug: dict[str, list[str]] = {}
    for key in target_keys:
        by_slug.setdefault(key.split(":")[0], []).append(key)

    for slug, slug_keys in sorted(by_slug.items(), key=lambda x: int(x[0].split("_")[1])):
        pred_path = predictions_path(output_root, slug)
        by_idx = load_predictions_by_index(pred_path)
        for key in sorted(slug_keys, key=lambda k: int(k.split(":")[1])):
            row = by_idx.get(int(key.split(":")[1]))
            if row is None:
                continue
            if row.get("parse_ok"):
                continue
            if key in overrides:
                ov = overrides[key]
                label = ov["label"]
                if label not in {"BORDER", "NOBORDER"}:
                    raise ValueError(f"Invalid override label for {key}: {label}")
                plans.append(
                    PatchPlan(
                        key=key,
                        slug=slug,
                        sentence_index=int(key.split(":")[1]),
                        sentence_text=str(row.get("sentence_text_full") or ""),
                        suggested_label=label,  # type: ignore[arg-type]
                        confidence="high",
                        method="manual_override",
                        prev_label=neighbor_label(by_idx, int(key.split(":")[1]), -1),
                        next_label=neighbor_label(by_idx, int(key.split(":")[1]), 1),
                        parse_error=row.get("parse_error"),
                        reason=ov["reason"],
                    )
                )
            else:
                plans.append(suggest_patch(row, by_idx))
    return plans


def write_export(path: Path, plans: list[PatchPlan]) -> None:
    payload = {
        "count": len(plans),
        "patches": [
            {
                "key": p.key,
                "slug": p.slug,
                "sentence_index": p.sentence_index,
                "sentence_text": p.sentence_text,
                "suggested_label": p.suggested_label,
                "confidence": p.confidence,
                "method": p.method,
                "prev_label": p.prev_label,
                "next_label": p.next_label,
                "parse_error": p.parse_error,
                "reason": p.reason,
            }
            for p in plans
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_export_csv(path: Path, plans: list[PatchPlan]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "key",
                "suggested_label",
                "confidence",
                "method",
                "prev_label",
                "next_label",
                "parse_error",
                "reason",
                "sentence_text",
            ],
        )
        writer.writeheader()
        for p in plans:
            writer.writerow(
                {
                    "key": p.key,
                    "suggested_label": p.suggested_label,
                    "confidence": p.confidence,
                    "method": p.method,
                    "prev_label": p.prev_label or "",
                    "next_label": p.next_label or "",
                    "parse_error": p.parse_error or "",
                    "reason": p.reason,
                    "sentence_text": p.sentence_text,
                }
            )


def apply_plans(
    output_root: Path,
    plans: list[PatchPlan],
    *,
    min_confidence: Confidence,
) -> dict[str, int]:
    min_rank = confidence_rank(min_confidence)
    stats = {"applied": 0, "skipped_confidence": 0, "skipped_no_label": 0, "books": 0}
    by_slug: dict[str, list[PatchPlan]] = {}
    for plan in plans:
        if plan.suggested_label is None:
            stats["skipped_no_label"] += 1
            continue
        if confidence_rank(plan.confidence) < min_rank:
            stats["skipped_confidence"] += 1
            continue
        by_slug.setdefault(plan.slug, []).append(plan)

    for slug, slug_plans in sorted(by_slug.items(), key=lambda x: int(x[0].split("_")[1])):
        pred_path = predictions_path(output_root, slug)
        by_idx = load_predictions_by_index(pred_path)
        patched_rows: list[dict[str, Any]] = []
        for plan in slug_plans:
            row = by_idx[plan.sentence_index]
            patched_rows.append(
                build_patched_row(
                    row,
                    label=plan.suggested_label,
                    reason=plan.reason,
                    method=plan.method,
                    confidence=plan.confidence,
                )
            )
        merged = merge_predictions(pred_path, patched_rows)
        tmp = pred_path.with_suffix(pred_path.suffix + ".tmp")
        with tmp.open("w", encoding="utf-8") as handle:
            for row in merged:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        tmp.replace(pred_path)

        source_file = str(by_idx[slug_plans[0].sentence_index].get("source_file") or f"{slug}.csv")
        run_book_review(
            predictions=pred_path,
            book_out=pred_path.parent,
            source_file=source_file,
        )
        stats["applied"] += len(slug_plans)
        stats["books"] += 1
    return stats


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output_root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument(
        "--keys_file",
        type=Path,
        default=None,
        help="Optional JSON file with {\"keys\": [...]} limit.",
    )
    parser.add_argument(
        "--overrides",
        type=Path,
        default=None,
        help="CSV/JSON manual labels. CSV columns: key,label,reason.",
    )
    parser.add_argument(
        "--export_json",
        type=Path,
        default=None,
        help="Write patch suggestions to JSON.",
    )
    parser.add_argument(
        "--export_csv",
        type=Path,
        default=None,
        help="Write patch suggestions to CSV for human edit/re-import as overrides.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write patches to predictions.jsonl and refresh book_review.json.",
    )
    parser.add_argument(
        "--min_confidence",
        choices=["high", "medium", "low"],
        default="medium",
        help="Only apply suggestions at or above this confidence (default: medium).",
    )
    parser.add_argument(
        "--dry_run",
        action="store_true",
        help="Print summary only; no files written unless --export_* is set.",
    )
    return parser.parse_args()


def print_summary(plans: list[PatchPlan]) -> None:
    from collections import Counter

    print(f"Failed keys: {len(plans)}")
    print("Confidence:")
    for conf, count in Counter(p.confidence for p in plans).most_common():
        print(f"  {conf}: {count}")
    print("Suggested labels:")
    for label, count in Counter(p.suggested_label for p in plans).most_common():
        print(f"  {label}: {count}")
    print("Methods:")
    for method, count in Counter(p.method for p in plans).most_common():
        print(f"  {method}: {count}")
    print("\nReview (low confidence):")
    for p in plans:
        if p.confidence == "low":
            preview = p.sentence_text[:90].replace("\n", " ")
            print(
                f"  {p.key} -> {p.suggested_label} ({p.method}) "
                f"prev={p.prev_label} next={p.next_label} | {preview}"
            )


def main() -> int:
    args = parse_args()
    keys = None
    if args.keys_file:
        payload = json.loads(args.keys_file.read_text(encoding="utf-8"))
        keys = list(payload.get("keys") or [])

    overrides = load_overrides(args.overrides) if args.overrides else {}
    plans = collect_plans(args.output_root, keys=keys, overrides=overrides)

    if not plans:
        print("No failed keys to patch.")
        return 0

    print_summary(plans)

    if args.export_json:
        write_export(args.export_json, plans)
        print(f"\nWrote {args.export_json}")
    if args.export_csv:
        write_export_csv(args.export_csv, plans)
        print(f"Wrote {args.export_csv}")

    if args.apply:
        if args.dry_run:
            print("\n--apply ignored because --dry_run is set.")
            return 0
        stats = apply_plans(args.output_root, plans, min_confidence=args.min_confidence)
        print(
            f"\nApplied {stats['applied']} patches across {stats['books']} books. "
            f"Skipped confidence={stats['skipped_confidence']} "
            f"skipped_no_label={stats['skipped_no_label']}"
        )
        remaining = len(discover_failed_keys(args.output_root))
        print(f"Remaining failed keys: {remaining}")
        return 0 if remaining == 0 else 1

    if args.dry_run:
        print("\nDry run only; no predictions modified.")
    else:
        print("\nNo --apply; export suggestions or re-run with --apply.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
