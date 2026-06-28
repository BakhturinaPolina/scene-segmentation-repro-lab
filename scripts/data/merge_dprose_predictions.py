#!/usr/bin/env python3
"""Merge per-book dProse predictions into a single corpus JSONL."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def dedupe_key(row: dict[str, Any]) -> str:
    source = row.get("source_file") or ""
    idx = row.get("sentence_index")
    if row.get("key"):
        return str(row["key"])
    return f"{source}:{idx}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input_root",
        type=Path,
        default=Path("outputs/runs/dprose_batch/dprose-full-corpus/books"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/runs/dprose_batch/dprose-full-corpus/predictions_full.jsonl"),
    )
    parser.add_argument(
        "--expected_count",
        type=int,
        default=120369,
        help="Expected total sentence count for validation.",
    )
    parser.add_argument(
        "--summary_out",
        type=Path,
        default=Path("outputs/runs/dprose_batch/dprose-full-corpus/corpus_summary.json"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    by_key: dict[str, dict[str, Any]] = {}
    book_stats: list[dict[str, Any]] = []

    for book_dir in sorted(args.input_root.glob("*/")):
        pred_path = book_dir / "predictions.jsonl"
        if not pred_path.is_file():
            continue
        rows = load_jsonl(pred_path)
        parse_ok = sum(1 for r in rows if r.get("parse_ok"))
        border = sum(1 for r in rows if r.get("parse_ok") and r.get("prediction_label") == "BORDER")
        cost = 0.0
        for row in rows:
            usage = row.get("usage") or {}
            cost += (int(usage.get("prompt_tokens", 0)) / 1_000_000) * 0.625
            cost += (
                (int(usage.get("output_tokens", 0)) + int(usage.get("thought_tokens", 0)))
                / 1_000_000
            ) * 5.0
            by_key[dedupe_key(row)] = row
        book_stats.append(
            {
                "slug": book_dir.name,
                "rows": len(rows),
                "parse_ok_rate": parse_ok / len(rows) if rows else 0,
                "border_rate": border / len(rows) if rows else 0,
                "estimated_cost_usd": round(cost, 4),
            }
        )

    merged = [by_key[k] for k in sorted(by_key.keys())]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for row in merged:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    parse_ok_total = sum(1 for r in merged if r.get("parse_ok"))
    border_total = sum(
        1 for r in merged if r.get("parse_ok") and r.get("prediction_label") == "BORDER"
    )
    total_cost = sum(float(b.get("estimated_cost_usd", 0)) for b in book_stats)
    summary = {
        "book_count": len(book_stats),
        "row_count": len(merged),
        "expected_count": args.expected_count,
        "count_match": len(merged) == args.expected_count,
        "parse_ok_rate": parse_ok_total / len(merged) if merged else 0,
        "border_rate": border_total / len(merged) if merged else 0,
        "estimated_cost_usd": round(total_cost, 4),
        "books": book_stats,
        "output": str(args.output),
    }
    args.summary_out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(f"Merged {len(merged)} predictions from {len(book_stats)} books")
    print(f"Expected: {args.expected_count}  Match: {summary['count_match']}")
    print(f"Parse OK: {summary['parse_ok_rate']:.1%}  Cost: ${summary['estimated_cost_usd']:.2f}")
    print(f"Wrote: {args.output}")
    print(f"Wrote: {args.summary_out}")
    return 0 if summary["count_match"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
