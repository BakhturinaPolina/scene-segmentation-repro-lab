#!/usr/bin/env python3
"""Per-book review report for dProse batch predictions."""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from typing import Any


def load_predictions(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def border_indices(rows: list[dict[str, Any]]) -> list[int]:
    out: list[int] = []
    for row in rows:
        if row.get("parse_ok") and row.get("prediction_label") == "BORDER":
            idx = row.get("sentence_index")
            if idx is not None:
                out.append(int(idx))
    return sorted(out)


def scene_lengths(borders: list[int], total: int) -> list[int]:
    if not borders:
        return [total] if total else []
    lengths: list[int] = []
    prev = 0
    for b in borders:
        lengths.append(max(1, b - prev + 1))
        prev = b + 1
    if prev < total:
        lengths.append(total - prev)
    return lengths


def max_consecutive_border_run(borders: list[int]) -> tuple[int, list[int]]:
    if not borders:
        return 0, []
    best_run = 1
    best_start = borders[0]
    cur_run = 1
    cur_start = borders[0]
    for i in range(1, len(borders)):
        if borders[i] == borders[i - 1] + 1:
            cur_run += 1
        else:
            if cur_run > best_run:
                best_run = cur_run
                best_start = cur_start
            cur_run = 1
            cur_start = borders[i]
    if cur_run > best_run:
        best_run = cur_run
        best_start = cur_start
    run_indices = list(range(best_start, best_start + best_run))
    return best_run, run_indices


def consecutive_border_pairs(borders: list[int]) -> list[tuple[int, int]]:
    pairs: list[tuple[int, int]] = []
    for i in range(len(borders) - 1):
        if borders[i + 1] == borders[i] + 1:
            pairs.append((borders[i], borders[i + 1]))
    return pairs


def gaps_ge_n(borders: list[int], n: int) -> int:
    if len(borders) < 2:
        return 0
    count = 0
    for i in range(len(borders) - 1):
        if borders[i + 1] - borders[i] >= n:
            count += 1
    return count


def summarize_book(rows: list[dict[str, Any]], *, source_file: str | None = None) -> dict[str, Any]:
    if not rows:
        return {"source_file": source_file, "sentence_count": 0}

    source = source_file or rows[0].get("source_file") or "unknown"
    total = len(rows)
    parse_ok = sum(1 for r in rows if r.get("parse_ok"))
    borders = border_indices(rows)
    border_count = len(borders)
    lengths = scene_lengths(borders, total)
    short_scenes = sum(1 for ln in lengths if ln <= 2)
    max_run, max_run_indices = max_consecutive_border_run(borders)
    pairs = consecutive_border_pairs(borders)
    failed_keys = [r.get("key") for r in rows if not r.get("parse_ok")]

    cost = 0.0
    for row in rows:
        usage = row.get("usage") or {}
        prompt_tokens = int(usage.get("prompt_tokens", 0))
        output_tokens = int(usage.get("output_tokens", 0))
        thought_tokens = int(usage.get("thought_tokens", 0))
        cost += (prompt_tokens / 1_000_000) * 0.625 + ((output_tokens + thought_tokens) / 1_000_000) * 5.0

    first_text = ""
    for row in rows:
        text = row.get("sentence_text_full") or ""
        if text:
            first_text = text[:120]
            break

    return {
        "source_file": source,
        "sentence_count": total,
        "parse_ok_count": parse_ok,
        "parse_ok_rate": parse_ok / total if total else 0.0,
        "border_count": border_count,
        "border_rate": border_count / total if total else 0.0,
        "estimated_cost_usd": round(cost, 4),
        "scene_length_median": statistics.median(lengths) if lengths else 0,
        "scene_length_mean": statistics.mean(lengths) if lengths else 0,
        "scene_length_min": min(lengths) if lengths else 0,
        "scene_length_max": max(lengths) if lengths else 0,
        "short_scene_rate": short_scenes / len(lengths) if lengths else 0.0,
        "max_consecutive_border_run": max_run,
        "max_consecutive_border_indices": max_run_indices,
        "consecutive_border_pairs": len(pairs),
        "consecutive_border_pair_examples": pairs[:5],
        "gaps_ge_10": gaps_ge_n(borders, 10),
        "failed_keys": failed_keys,
        "sample_border_indices": borders[:5],
        "first_sentence_preview": first_text,
    }


def format_review(summary: dict[str, Any]) -> str:
    source = summary.get("source_file", "unknown")
    total = summary.get("sentence_count", 0)
    parse_ok = summary.get("parse_ok_count", 0)
    parse_rate = summary.get("parse_ok_rate", 0.0)
    border_count = summary.get("border_count", 0)
    border_rate = summary.get("border_rate", 0.0)
    cost = summary.get("estimated_cost_usd", 0.0)

    lines = [
        f"=== BOOK REVIEW: {source} ({total} sentences) ===",
        (
            f"Parse: {parse_ok}/{total} ({parse_rate:.1%})  |  "
            f"BORDER: {border_count} ({border_rate:.1%})  |  Cost: ${cost:.2f}"
        ),
        (
            f"Scene length: median={summary.get('scene_length_median', 0):.0f}, "
            f"mean={summary.get('scene_length_mean', 0):.1f}, "
            f"1-2 sent scenes={summary.get('short_scene_rate', 0.0):.1%}"
        ),
    ]

    alerts: list[str] = []
    if summary.get("consecutive_border_pairs", 0):
        examples = summary.get("consecutive_border_pair_examples") or []
        ex = ", ".join(f"idx {a}-{b}" for a, b in examples[:3])
        alerts.append(f"{summary['consecutive_border_pairs']} consecutive-BORDER pairs ({ex})")
    if summary.get("max_consecutive_border_run", 0) > 2:
        idxs = summary.get("max_consecutive_border_indices") or []
        alerts.append(f"max consecutive BORDER run={summary['max_consecutive_border_run']} (idx {idxs})")
    if parse_rate < 0.95:
        alerts.append(f"parse_ok_rate below 95% gate ({parse_rate:.1%})")
    if border_rate < 0.10 or border_rate > 0.40:
        alerts.append(f"BORDER rate outside 10-40% band ({border_rate:.1%})")

    if alerts:
        lines.append("Alerts: " + "; ".join(alerts))
    else:
        lines.append("Alerts: none")

    failed = summary.get("failed_keys") or []
    if failed:
        lines.append(f"Failed keys: {', '.join(str(k) for k in failed)}")
    else:
        lines.append("Failed keys: none")

    preview = summary.get("first_sentence_preview") or ""
    if preview:
        lines.append(f"Opening: {preview!r}")

    sample = summary.get("sample_border_indices") or []
    if sample:
        lines.append(f"Sample BORDER indices: {sample}")

    lines.append("=== END ===")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--source_file", default=None, help="Override source file label.")
    parser.add_argument("--write_txt", type=Path, default=None, help="Write review text to this path.")
    parser.add_argument("--write_json", type=Path, default=None, help="Write summary JSON to this path.")
    parser.add_argument("--quiet", action="store_true", help="Do not print review to stdout.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = load_predictions(args.predictions)
    summary = summarize_book(rows, source_file=args.source_file)
    text = format_review(summary)

    if not args.quiet:
        print(text, flush=True)

    if args.write_txt:
        args.write_txt.parent.mkdir(parents=True, exist_ok=True)
        args.write_txt.write_text(text + "\n", encoding="utf-8")

    if args.write_json:
        args.write_json.parent.mkdir(parents=True, exist_ok=True)
        args.write_json.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    return 0 if summary.get("parse_ok_rate", 0) >= 0.95 else 1


if __name__ == "__main__":
    raise SystemExit(main())
