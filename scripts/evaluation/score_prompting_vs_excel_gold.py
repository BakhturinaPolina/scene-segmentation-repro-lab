#!/usr/bin/env python3
"""Score prompting predictions against Excel-derived gold labels."""

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


def read_review_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def read_gold_csv(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def as_label(value: Any) -> str:
    token = clean(value).upper()
    if token in {"BORDER", "TRUE", "YES", "1"}:
        return "BORDER"
    return "NOBORDER"


def score_rows(gold_rows: list[dict[str, Any]], pred_rows: list[dict[str, Any]]) -> dict[str, Any]:
    pred_by_idx: dict[int, str] = {}
    pred_by_text: dict[str, str] = {}
    for row in pred_rows:
        idx_raw = clean(row.get("sentence_index"))
        if idx_raw:
            try:
                pred_by_idx[int(float(idx_raw))] = as_label(row.get("prediction_label"))
            except Exception:
                pass
        text_key = norm_text(row.get("sentence_text_full"))
        if text_key:
            pred_by_text[text_key] = as_label(row.get("prediction_label"))

    tp = fp = fn = tn = 0
    match_counts = {"index": 0, "text": 0, "default_noborder": 0}

    for pos, row in enumerate(gold_rows):
        g = as_label(row.get("ground_truth_label"))
        text_key = norm_text(row.get("sentence_text_full"))

        pred = None
        if pos in pred_by_idx:
            pred = pred_by_idx[pos]
            match_counts["index"] += 1
        elif text_key and text_key in pred_by_text:
            pred = pred_by_text[text_key]
            match_counts["text"] += 1
        else:
            pred = "NOBORDER"
            match_counts["default_noborder"] += 1

        if pred == "BORDER" and g == "BORDER":
            tp += 1
        elif pred == "BORDER" and g == "NOBORDER":
            fp += 1
        elif pred == "NOBORDER" and g == "BORDER":
            fn += 1
        else:
            tn += 1

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) else 0.0

    return {
        "n_rows": tp + tn + fp + fn,
        "confusion": {"tp": tp, "fp": fp, "fn": fn, "tn": tn},
        "match_counts": match_counts,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "accuracy": round(accuracy, 4),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gold_csv", type=Path, required=True, help="Gold labels CSV path.")
    parser.add_argument("--review_jsonl", type=Path, required=True, help="Model review JSONL path.")
    parser.add_argument("--out_json", type=Path, required=True, help="Output summary path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    gold_rows = read_gold_csv(args.gold_csv)
    pred_rows = read_review_jsonl(args.review_jsonl)
    summary = {
        "gold_csv": str(args.gold_csv),
        "review_jsonl": str(args.review_jsonl),
        "metrics": score_rows(gold_rows, pred_rows),
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    m = summary["metrics"]
    print(f"Wrote: {args.out_json}")
    print(
        "P={:.3f} R={:.3f} F1={:.3f} Acc={:.3f} (n={})".format(
            m["precision"], m["recall"], m["f1"], m["accuracy"], m["n_rows"]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
