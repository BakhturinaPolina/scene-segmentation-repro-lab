#!/usr/bin/env python3
"""Plan budget-limited dProse prompting waves from a full manifest."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.runners.dprose_batch_core import PILOT_COST_PER_SENTENCE_USD, estimate_cost_usd

DEFAULT_PILOT_SLUGS = {"dprose_100", "dprose_806", "dprose_2158"}
DEFAULT_EUR_USD = 0.92
DEFAULT_SAFETY_MARGIN = 0.15


def numeric_id(source_file: str) -> int:
    stem = Path(source_file).stem
    return int(stem.replace("dprose_", ""))


def load_manifest(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_completed_slugs(progress_path: Path) -> set[str]:
    if not progress_path.is_file():
        return set()
    payload = json.loads(progress_path.read_text(encoding="utf-8"))
    completed: set[str] = set()
    for slug, entry in payload.get("books", {}).items():
        if entry.get("status") == "complete":
            completed.add(slug)
    return completed


def sort_entries(files: list[dict[str, Any]], order: str) -> list[dict[str, Any]]:
    if order == "numeric_id":
        return sorted(files, key=lambda f: numeric_id(f["source_file"]))
    if order == "slug":
        return sorted(files, key=lambda f: f.get("slug", ""))
    if order == "sentence_count":
        return sorted(files, key=lambda f: int(f.get("sentence_count", 0)))
    raise ValueError(f"Unknown order: {order}")


def plan_wave(
    files: list[dict[str, Any]],
    *,
    budget_eur: float,
    eur_usd: float,
    safety_margin: float,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    budget_usd = (budget_eur / eur_usd) * (1.0 - safety_margin)
    selected: list[dict[str, Any]] = []
    sentence_count = 0
    for entry in files:
        n = int(entry.get("sentence_count", 0))
        projected = estimate_cost_usd(sentence_count + n)
        if selected and projected > budget_usd:
            break
        if not selected and estimate_cost_usd(n) > budget_usd:
            selected.append(entry)
            sentence_count += n
            break
        selected.append(entry)
        sentence_count += n
    stats = {
        "budget_eur": budget_eur,
        "budget_usd_effective": round(budget_usd, 2),
        "book_count": len(selected),
        "sentence_count": sentence_count,
        "estimated_cost_usd": estimate_cost_usd(sentence_count),
        "cost_per_sentence_usd": PILOT_COST_PER_SENTENCE_USD,
        "safety_margin": safety_margin,
        "eur_usd": eur_usd,
    }
    return selected, stats


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--full_manifest",
        type=Path,
        default=Path("data/manifests/dprose_full.json"),
    )
    parser.add_argument("--budget_eur", type=float, required=True)
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Wave manifest JSON output path.",
    )
    parser.add_argument(
        "--wave_id",
        default=None,
        help="Wave identifier (default: derived from output filename stem).",
    )
    parser.add_argument(
        "--include_pilot",
        action="store_true",
        help="Include pilot books even if marked complete elsewhere.",
    )
    parser.add_argument(
        "--exclude_completed",
        type=Path,
        default=Path("outputs/runs/dprose_batch/dprose-full-corpus/corpus_progress.json"),
        help="Skip slugs marked complete in this progress file.",
    )
    parser.add_argument(
        "--order",
        choices=["numeric_id", "slug", "sentence_count"],
        default="numeric_id",
    )
    parser.add_argument("--eur_usd", type=float, default=DEFAULT_EUR_USD)
    parser.add_argument("--safety_margin", type=float, default=DEFAULT_SAFETY_MARGIN)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = load_manifest(args.full_manifest)
    files = list(manifest.get("files", []))

    exclude_slugs: set[str] = set()
    if not args.include_pilot:
        exclude_slugs |= DEFAULT_PILOT_SLUGS
    if args.exclude_completed:
        exclude_slugs |= load_completed_slugs(args.exclude_completed)

    candidates = [f for f in files if f.get("slug") not in exclude_slugs]
    candidates = sort_entries(candidates, args.order)

    selected, stats = plan_wave(
        candidates,
        budget_eur=args.budget_eur,
        eur_usd=args.eur_usd,
        safety_margin=args.safety_margin,
    )

    wave_id = args.wave_id or args.output.stem
    wave = {
        "wave_id": wave_id,
        "created_at": date.today().isoformat(),
        "budget_eur": args.budget_eur,
        "order": args.order,
        "stats": stats,
        "books": [
            {
                "slug": entry["slug"],
                "source_file": entry["source_file"],
                "sentence_count": entry.get("sentence_count", 0),
                "estimated_cost_usd": estimate_cost_usd(int(entry.get("sentence_count", 0))),
            }
            for entry in selected
        ],
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(wave, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Wave: {wave_id}")
    print(f"Books: {stats['book_count']}  Sentences: {stats['sentence_count']}")
    print(f"Estimated cost: ${stats['estimated_cost_usd']:.2f} (budget effective ${stats['budget_usd_effective']:.2f})")
    print(f"Wrote: {args.output}")
    for entry in selected[:5]:
        print(f"  - {entry['source_file']} ({entry.get('sentence_count', 0)} sentences)")
    if len(selected) > 5:
        print(f"  ... and {len(selected) - 5} more")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
