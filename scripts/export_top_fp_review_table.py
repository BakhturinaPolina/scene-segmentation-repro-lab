#!/usr/bin/env python3
"""Export top false-positive rows with context and diagnostic tags."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any


def clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def norm_text(value: Any) -> str:
    return re.sub(r"\s+", " ", clean(value))


def as_label(value: Any) -> str:
    token = clean(value).upper()
    if token in {"BORDER", "TRUE", "YES", "1"}:
        return "BORDER"
    return "NOBORDER"


def parse_confidence(raw_model_response: Any) -> float | None:
    if not isinstance(raw_model_response, str):
        return None
    try:
        payload = json.loads(raw_model_response)
    except Exception:
        return None
    value = payload.get("confidence")
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


def parse_reason(raw_model_response: Any) -> str:
    if not isinstance(raw_model_response, str):
        return ""
    try:
        payload = json.loads(raw_model_response)
        reason = payload.get("reason")
        return clean(reason)
    except Exception:
        return ""


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def read_csv(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def nearest_distance(value: int, indices: list[int]) -> int:
    if not indices:
        return 10**9
    return min(abs(value - idx) for idx in indices)


def make_tag(*, dist_nearest_gold: int, confidence: float | None, reason: str) -> str:
    if dist_nearest_gold <= 1:
        return "near-boundary"
    if dist_nearest_gold <= 3:
        return "near-boundary-loose"
    if confidence is not None and confidence >= 0.85:
        return "likely true disagreement"
    if reason:
        return "micro-shift"
    return "micro-shift"


def build_fp_rows(
    *,
    text_name: str,
    gold_rows: list[dict[str, Any]],
    review_rows: list[dict[str, Any]],
    top_k: int,
) -> list[dict[str, Any]]:
    pred_by_idx: dict[int, dict[str, Any]] = {}
    pred_by_text: dict[str, dict[str, Any]] = {}
    for row in review_rows:
        idx_raw = clean(row.get("sentence_index"))
        if idx_raw:
            try:
                pred_by_idx[int(float(idx_raw))] = row
            except Exception:
                pass
        text_key = norm_text(row.get("sentence_text_full"))
        if text_key and text_key not in pred_by_text:
            pred_by_text[text_key] = row

    aligned: list[dict[str, Any]] = []
    for pos, row in enumerate(gold_rows):
        gold_label = as_label(row.get("ground_truth_label"))
        idx_raw = clean(row.get("sentence_index"))
        sentence_index = pos
        if idx_raw:
            try:
                sentence_index = int(float(idx_raw))
            except Exception:
                sentence_index = pos
        text = clean(row.get("sentence_text_full"))

        pred_row = pred_by_idx.get(sentence_index)
        matched_by = "index"
        if pred_row is None:
            pred_row = pred_by_text.get(norm_text(text))
            matched_by = "text"

        if pred_row is None:
            pred_label = "NOBORDER"
            confidence = None
            reason = ""
        else:
            pred_label = as_label(pred_row.get("prediction_label"))
            confidence = parse_confidence(pred_row.get("raw_model_response"))
            reason = parse_reason(pred_row.get("raw_model_response"))

        aligned.append(
            {
                "pos": pos,
                "sentence_index": sentence_index,
                "text": text,
                "gold_label": gold_label,
                "pred_label": pred_label,
                "matched_by": matched_by,
                "confidence": confidence,
                "reason": reason,
            }
        )

    gold_border_pos = [r["pos"] for r in aligned if r["gold_label"] == "BORDER"]

    fps = [r for r in aligned if r["gold_label"] == "NOBORDER" and r["pred_label"] == "BORDER"]
    fps.sort(key=lambda r: (r["confidence"] is None, -(r["confidence"] or -1), r["pos"]))

    out_rows: list[dict[str, Any]] = []
    for rank, row in enumerate(fps[:top_k], start=1):
        pos = row["pos"]
        prev_row = aligned[pos - 1] if pos > 0 else None
        next_row = aligned[pos + 1] if pos + 1 < len(aligned) else None
        dist_nearest_gold = nearest_distance(pos, gold_border_pos)
        tag = make_tag(
            dist_nearest_gold=dist_nearest_gold,
            confidence=row["confidence"],
            reason=row["reason"],
        )
        out_rows.append(
            {
                "text_name": text_name,
                "rank": rank,
                "sentence_index": row["sentence_index"],
                "distance_to_nearest_gold_boundary": dist_nearest_gold,
                "tag": tag,
                "confidence": row["confidence"],
                "matched_by": row["matched_by"],
                "gold_label": row["gold_label"],
                "pred_label": row["pred_label"],
                "sentence_text": row["text"],
                "model_reason": row["reason"],
                "prev_sentence_index": None if prev_row is None else prev_row["sentence_index"],
                "prev_gold_label": None if prev_row is None else prev_row["gold_label"],
                "prev_pred_label": None if prev_row is None else prev_row["pred_label"],
                "prev_text": None if prev_row is None else prev_row["text"],
                "next_sentence_index": None if next_row is None else next_row["sentence_index"],
                "next_gold_label": None if next_row is None else next_row["gold_label"],
                "next_pred_label": None if next_row is None else next_row["pred_label"],
                "next_text": None if next_row is None else next_row["text"],
            }
        )
    return out_rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base_dir",
        type=Path,
        default=Path("outputs/review/excel_prompting_familyB_reasoning-off"),
        help="Base output directory containing per-text review outputs.",
    )
    parser.add_argument(
        "--top_k",
        type=int,
        default=10,
        help="How many FP rows to export per text.",
    )
    parser.add_argument(
        "--out_csv",
        type=Path,
        default=Path("outputs/review/excel_prompting_familyB_reasoning-off/top_fp_review_table.csv"),
        help="Output CSV path.",
    )
    parser.add_argument(
        "--out_json",
        type=Path,
        default=Path("outputs/review/excel_prompting_familyB_reasoning-off/top_fp_review_table.json"),
        help="Output JSON path.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    specs = [
        (
            "gaensemagd",
            Path("data/processed/excel_prompting/gaensemagd_sentence_level/gaensemagd_sentence_level__gold_labels.csv"),
            args.base_dir / "gaensemagd" / "review.jsonl",
        ),
        (
            "kleist",
            Path("data/processed/excel_prompting/kleist_sentence_level/kleist_sentence_level__gold_labels.csv"),
            args.base_dir / "kleist" / "review.jsonl",
        ),
    ]

    all_rows: list[dict[str, Any]] = []
    for text_name, gold_path, review_path in specs:
        gold_rows = read_csv(gold_path)
        review_rows = read_jsonl(review_path)
        all_rows.extend(
            build_fp_rows(
                text_name=text_name,
                gold_rows=gold_rows,
                review_rows=review_rows,
                top_k=args.top_k,
            )
        )

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(all_rows[0].keys()) if all_rows else [])
        if all_rows:
            writer.writeheader()
            writer.writerows(all_rows)

    args.out_json.write_text(json.dumps(all_rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote CSV: {args.out_csv}")
    print(f"Wrote JSON: {args.out_json}")
    print(f"Rows: {len(all_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
