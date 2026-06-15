#!/usr/bin/env python3
"""Aggregate Excel OFAT prompting runs into a comparison CSV.

Scans ``outputs/runs/prompting/<date>/full_*_familyB_*`` directories for
``summary.json`` and reports F1@0/1/3, over-prediction ratio, parse failures,
and cost class from model profiles.

Example:
    python scripts/evaluation/summarize_excel_ofat.py \\
        --run_root outputs/runs/prompting/2026-06-14-excel-ofat-s1 \\
        --out review/excel_ofat_stage1_summary.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from core.prompt_runtime import get_model_profile, load_model_profiles


def _find_summaries(run_root: Path, prompt_family: Optional[str] = None) -> List[Path]:
    if not run_root.exists():
        return []
    if prompt_family:
        return sorted(run_root.glob(f"full_*_family{prompt_family}_*/summary.json"))
    return sorted(run_root.glob("full_*_family*/summary.json"))


def _load_summary(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def summarize_one(summary_path: Path, profiles: Dict[str, Any]) -> Dict[str, Any]:
    data = _load_summary(summary_path)
    model = data.get("model", "")
    profile = get_model_profile(model, profiles)
    row = {
        "model": model,
        "run_dir": str(summary_path.parent.name),
        "cost_class": profile.get("cost_class", ""),
        "est_run_cost_usd": profile.get("est_run_cost_usd", ""),
        "f1_tol0": data.get("macro_avg_tol_0", {}).get("f1"),
        "f1_tol1": data.get("macro_avg_tol_1", {}).get("f1"),
        "f1_tol3": data.get("macro_avg_tol_3", {}).get("f1"),
        "precision_tol3": data.get("macro_avg_tol_3", {}).get("precision"),
        "recall_tol3": data.get("macro_avg_tol_3", {}).get("recall"),
        "run_complete": data.get("run_complete", False),
        "overprediction_ratio": data.get("overprediction_ratio"),
        "total_gold_borders": data.get("total_gold_borders"),
        "total_pred_borders": data.get("total_pred_borders"),
        "parse_failure_rate": data.get("avg_parse_failure_rate"),
        "avg_latency_s": data.get("avg_latency_seconds"),
    }
    return row


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run_root",
        type=Path,
        required=True,
        help="Date folder under outputs/runs/prompting/ (e.g. 2026-06-14-excel-ofat-s1)",
    )
    parser.add_argument("--out", type=Path, default=None, help="CSV output path")
    parser.add_argument(
        "--model_profile_file",
        type=Path,
        default=_ROOT / "src/core/openrouter_model_profiles.json",
    )
    parser.add_argument(
        "--prompt_family",
        type=str,
        default=None,
        help="Filter run dirs by prompt family id (e.g. B, Q). Default: all families.",
    )
    args = parser.parse_args()

    run_root = args.run_root
    if not run_root.is_absolute():
        run_root = _ROOT / "outputs/runs/prompting" / run_root

    profiles = load_model_profiles(args.model_profile_file)
    summaries = _find_summaries(run_root, args.prompt_family)
    if not summaries:
        print(f"No summary.json found under {run_root}/full_*_family{args.prompt_family or '*'}_*/")
        sys.exit(1)

    rows = [summarize_one(p, profiles) for p in summaries]
    rows.sort(key=lambda r: (r.get("f1_tol3") or 0, r.get("precision_tol3") or 0), reverse=True)

    fieldnames = list(rows[0].keys())
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Wrote {len(rows)} rows to {args.out}")

    print(f"{'model':<45} {'F3':>6} {'P@3':>6} {'R@3':>6} {'overpred':>9} {'parse_fail':>10}")
    for row in rows:
        print(
            f"{row['model']:<45} "
            f"{row['f1_tol3'] or 0:>6.3f} "
            f"{row['precision_tol3'] or 0:>6.3f} "
            f"{row['recall_tol3'] or 0:>6.3f} "
            f"{row['overprediction_ratio'] or 0:>9.2f} "
            f"{row['parse_failure_rate'] or 0:>10.3f}"
        )


if __name__ == "__main__":
    main()
