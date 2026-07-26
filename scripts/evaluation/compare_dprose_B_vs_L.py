#!/usr/bin/env python3
"""Compare Family L spot-rerun predictions vs production Family B book reviews.

Usage:
  .venv/bin/python scripts/evaluation/compare_dprose_B_vs_L.py \
    --l_predictions outputs/runs/dprose_batch/2026-07-22-dprose-familyL-spot-rerun/predictions.jsonl \
    --b_root outputs/runs/dprose_batch/dprose-full-corpus/books \
    --slugs dprose_52,dprose_119,dprose_137,dprose_100 \
    --out outputs/runs/dprose_batch/2026-07-22-dprose-familyL-spot-rerun/B_vs_L_comparison.json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

_review_path = Path(__file__).resolve().parent / "review_dprose_book.py"
_spec = importlib.util.spec_from_file_location("review_dprose_book", _review_path)
_review = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_review)
border_indices = _review.border_indices
consecutive_border_pairs = _review.consecutive_border_pairs
gaps_ge_n = _review.gaps_ge_n
max_consecutive_border_run = _review.max_consecutive_border_run
scene_lengths = _review.scene_lengths


def review_from_rows(rows: list[dict[str, Any]], slug: str) -> dict[str, Any]:
    n = len(rows)
    parse_ok = sum(1 for r in rows if r.get("parse_ok"))
    borders = border_indices(rows)
    lengths = scene_lengths(borders, n)
    max_run, max_run_idx = max_consecutive_border_run(borders)
    short = sum(1 for x in lengths if x <= 2) / len(lengths) if lengths else 0.0

    return {
        "slug": slug,
        "sentence_count": n,
        "parse_ok_rate": parse_ok / n if n else 0.0,
        "border_count": len(borders),
        "border_rate": len(borders) / n if n else 0.0,
        "scene_length_median": statistics.median(lengths) if lengths else None,
        "scene_length_mean": statistics.mean(lengths) if lengths else None,
        "short_scene_rate": short,
        "max_consecutive_border_run": max_run,
        "max_consecutive_border_indices": max_run_idx,
        "consecutive_border_pairs": len(consecutive_border_pairs(borders)),
        "gaps_ge_10": gaps_ge_n(borders, 10),
        "border_indices": borders,
    }


def load_l_by_slug(path: Path) -> dict[str, list[dict[str, Any]]]:
    by: dict[str, list[dict[str, Any]]] = defaultdict(list)
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            key = row.get("key") or ""
            slug = key.split(":", 1)[0]
            by[slug].append(row)
    for slug in by:
        by[slug].sort(key=lambda r: int(r.get("sentence_index") or 0))
    return by


def agreement(b_borders: set[int], l_borders: set[int], n: int) -> dict[str, Any]:
    both = b_borders & l_borders
    only_b = b_borders - l_borders
    only_l = l_borders - b_borders
    # treat as binary labels; B as reference for precision/recall of L
    tp = len(both)
    fp = len(only_l)
    fn = len(only_b)
    p = tp / (tp + fp) if (tp + fp) else 0.0
    r = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) else 0.0
    return {
        "shared_borders": tp,
        "only_B": len(only_b),
        "only_L": len(only_l),
        "L_vs_B_precision": round(p, 4),
        "L_vs_B_recall": round(r, 4),
        "L_vs_B_f1": round(f1, 4),
        "border_rate_delta": None,  # filled by caller
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--l_predictions", type=Path, required=True)
    p.add_argument("--b_root", type=Path, default=Path("outputs/runs/dprose_batch/dprose-full-corpus/books"))
    p.add_argument("--slugs", default="dprose_52,dprose_119,dprose_137,dprose_100")
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()

    slugs = [s.strip() for s in args.slugs.split(",") if s.strip()]
    l_by = load_l_by_slug(args.l_predictions)

    rows_out: list[dict[str, Any]] = []
    for slug in slugs:
        b_rev = json.loads((args.b_root / slug / "book_review.json").read_text(encoding="utf-8"))
        # production border indices from sample + reconstruct via predictions if available
        b_pred_path = args.b_root / slug / "predictions.jsonl"
        if b_pred_path.is_file():
            b_rows = [json.loads(l) for l in b_pred_path.read_text(encoding="utf-8").splitlines() if l.strip()]
            b_rev_full = review_from_rows(b_rows, slug)
            b_borders = set(b_rev_full["border_indices"])
        else:
            b_rev_full = dict(b_rev)
            b_borders = set(b_rev.get("sample_border_indices") or [])

        l_rows = l_by.get(slug, [])
        if not l_rows:
            rows_out.append({"slug": slug, "error": "missing L predictions"})
            continue
        l_rev = review_from_rows(l_rows, slug)
        l_borders = set(l_rev["border_indices"])
        agr = agreement(b_borders, l_borders, l_rev["sentence_count"])
        agr["border_rate_delta"] = round(l_rev["border_rate"] - b_rev_full["border_rate"], 4)
        agr["border_count_delta"] = l_rev["border_count"] - b_rev_full["border_count"]
        agr["max_run_delta"] = l_rev["max_consecutive_border_run"] - b_rev_full["max_consecutive_border_run"]

        # drop full indices from nested review copies for readability
        b_clean = {k: v for k, v in b_rev_full.items() if k != "border_indices"}
        l_clean = {k: v for k, v in l_rev.items() if k != "border_indices"}

        rows_out.append({
            "slug": slug,
            "production_B": b_clean,
            "family_L": l_clean,
            "agreement_L_vs_B": agr,
            "only_B_indices_sample": sorted(list(b_borders - l_borders))[:15],
            "only_L_indices_sample": sorted(list(l_borders - b_borders))[:15],
            "shared_indices_sample": sorted(list(b_borders & l_borders))[:15],
        })

    payload = {
        "slugs": slugs,
        "n_books": len(rows_out),
        "books": rows_out,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    # also write a compact CSV-like markdown table to stdout
    print("| slug | B rate | L rate | Δ rate | B bord | L bord | B maxRun | L maxRun | L∩B F1 | onlyB | onlyL |")
    print("|------|--------|--------|--------|--------|--------|----------|----------|--------|-------|-------|")
    for row in rows_out:
        if "error" in row:
            print(f"| {row['slug']} | ERROR |")
            continue
        b, l, a = row["production_B"], row["family_L"], row["agreement_L_vs_B"]
        print(
            f"| {row['slug']} | {100*b['border_rate']:.1f}% | {100*l['border_rate']:.1f}% | "
            f"{100*a['border_rate_delta']:+.1f}pp | {b['border_count']} | {l['border_count']} | "
            f"{b['max_consecutive_border_run']} | {l['max_consecutive_border_run']} | "
            f"{a['L_vs_B_f1']:.3f} | {a['only_B']} | {a['only_L']} |"
        )
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
