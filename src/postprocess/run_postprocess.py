#!/usr/bin/env python3
"""Re-score a cached prompting run after applying a post-processing rule.

Loads a per-document cache JSON (as written by
``src/runners/run_prompting_stratified.py``) or a ``results_<stem>.json`` file,
applies one or more boundary post-processing scenarios, and reports tolerant
P/R/F1 for each, using the same scorer as the runner.

Examples
--------
    python src/postprocess/run_postprocess.py \\
        --cache outputs/runs/prompting/2026-06-06/full_.../cache_Aus_guter_Familie.json \\
        --scenario min_scene_len_3 --tolerances 0 1 3

    python src/postprocess/run_postprocess.py \\
        --results outputs/runs/prompting/.../results_Effi_Briest.json \\
        --scenario all --confidence_threshold 0.85 --out review/postproc.json

Note on partial caches: when a cache does not cover every sentence in the
document, the gold-label list is reconstructed from the cached indices only, so
tolerance windows near the boundary of the cached range are approximate. For a
completed ``--full_eval`` run the reconstruction is exact.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_FILE = Path(__file__).resolve()
_SRC_ROOT = _FILE.parents[1]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from postprocess.postprocess import SCENARIOS, apply_scenario, evaluate_sampled


def _parse_confidence(reason: Any) -> Optional[float]:
    if not isinstance(reason, str):
        return None
    try:
        payload = json.loads(reason)
    except Exception:  # noqa: BLE001
        return None
    if not isinstance(payload, dict):
        return None
    value = payload.get("confidence")
    if value is None:
        return None
    try:
        return float(value)
    except Exception:  # noqa: BLE001
        return None


def load_cache(path: Path) -> Dict[str, List[Any]]:
    """Return ordered indices, preds, golds, confidences, sentences from a cache JSON."""
    cache = json.loads(path.read_text(encoding="utf-8"))
    indices = sorted(int(k) for k in cache.keys())
    preds, golds, confs, sentences = [], [], [], []
    for i in indices:
        entry = cache[str(i)]
        preds.append(str(entry.get("pred", "NOBORDER")).upper())
        golds.append(str(entry.get("gold", "NOBORDER")).upper())
        confs.append(_parse_confidence(entry.get("reason")))
        sentences.append(str(entry.get("sentence", "")).strip())
    return {
        "indices": indices,
        "preds": preds,
        "golds": golds,
        "confidences": confs,
        "sentences": sentences,
    }


def load_results(path: Path) -> Dict[str, List[Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    indices = [int(x) for x in data["original_indices"]]
    preds = [str(x).upper() for x in data["predictions"]]
    golds = [str(x).upper() for x in data["ground_truth"]]
    reasons = data.get("reasons") or [None] * len(indices)
    confs = [_parse_confidence(r) for r in reasons]
    return {"indices": indices, "preds": preds, "golds": golds, "confidences": confs}


def build_full_gold(indices: List[int], golds: List[str]) -> List[str]:
    """Reconstruct a positional gold list spanning 0..max(index)."""
    if not indices:
        return []
    size = max(indices) + 1
    full = ["NOBORDER"] * size
    for idx, gold in zip(indices, golds):
        full[idx] = gold
    return full


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--cache", type=Path, help="Per-document cache JSON")
    src.add_argument("--results", type=Path, help="results_<stem>.json file")
    parser.add_argument(
        "--scenario",
        type=str,
        default="min_scene_len_3",
        help="Scenario name, or 'all' to sweep every scenario",
    )
    parser.add_argument(
        "--tolerances", type=int, nargs="+", default=[0, 1, 3],
        help="Tolerances at which to score (default: 0 1 3)",
    )
    parser.add_argument(
        "--confidence_threshold", type=float, default=0.85,
        help="Threshold for confidence_threshold scenarios (default: 0.85)",
    )
    parser.add_argument(
        "--min_gap", type=int, default=None,
        help="If set, run min_scene_len_<min_gap> scenario (in addition to --scenario)",
    )
    parser.add_argument(
        "--n_per_k", type=int, default=15,
        help="Block size k for n_per_k scenario (default: 15 ≈ 6.7%% border rate)",
    )
    parser.add_argument("--out", type=Path, default=None, help="Optional JSON output path")
    args = parser.parse_args()

    loaded = load_cache(args.cache) if args.cache else load_results(args.results)
    indices = loaded["indices"]
    preds = loaded["preds"]
    golds = loaded["golds"]
    confs = loaded["confidences"]
    sentences = loaded.get("sentences", [])
    full_gold = build_full_gold(indices, golds)

    scenarios = list(SCENARIOS) if args.scenario == "all" else [args.scenario]
    if args.min_gap is not None:
        scenarios.append(f"min_scene_len_{args.min_gap}")

    n_gold = sum(1 for g in golds if g == "BORDER")
    n_pred = sum(1 for p in preds if p == "BORDER")
    print(f"Loaded {len(indices)} cached sentences | gold BORDER={n_gold} | raw pred BORDER={n_pred}")

    report: Dict[str, Any] = {
        "source": str(args.cache or args.results),
        "n_sentences": len(indices),
        "n_gold_border": n_gold,
        "n_pred_border_raw": n_pred,
        "confidence_threshold": args.confidence_threshold,
        "n_per_k": args.n_per_k,
        "scenarios": {},
    }

    for scenario in scenarios:
        new_preds = apply_scenario(
            preds,
            scenario,
            confidences=confs,
            confidence_threshold=args.confidence_threshold,
            sentences=sentences if sentences else None,
            n_per_k=args.n_per_k,
        )
        kept = sum(1 for p in new_preds if p == "BORDER")
        metrics = {
            f"tol_{t}": evaluate_sampled(indices, new_preds, full_gold, t)
            for t in args.tolerances
        }
        report["scenarios"][scenario] = {"pred_border": kept, "metrics": metrics}
        head = " | ".join(
            f"tol{t}: P={metrics[f'tol_{t}']['precision']:.3f} "
            f"R={metrics[f'tol_{t}']['recall']:.3f} "
            f"F1={metrics[f'tol_{t}']['f1']:.3f}"
            for t in args.tolerances
        )
        print(f"  {scenario:<42} pred_border={kept:<5} {head}")

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
