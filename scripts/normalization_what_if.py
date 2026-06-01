#!/usr/bin/env python3
"""Run normalization what-if analyses on BORDER/NOBORDER predictions.

Common scenarios:
1) none (no post-processing; alias: baseline)
2) min_scene_len_3 (enforce >=3 sentence distance between BORDERs)
3) min_scene_len_5 (enforce >=5 sentence distance between BORDERs)

Additional optional scenarios remain available for diagnostics.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def as_label(value: Any) -> str:
    token = clean(value).upper()
    if token in {"BORDER", "TRUE", "YES", "1"}:
        return "BORDER"
    return "NOBORDER"


def read_gold_csv(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_review_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def build_aligned_sequences(gold_rows: list[dict[str, Any]], pred_rows: list[dict[str, Any]]) -> tuple[list[str], list[str]]:
    pred_by_idx: dict[int, str] = {}
    for row in pred_rows:
        idx_raw = clean(row.get("sentence_index"))
        if not idx_raw:
            continue
        try:
            idx = int(float(idx_raw))
        except Exception:
            continue
        pred_by_idx[idx] = as_label(row.get("prediction_label"))

    gold_labels: list[str] = []
    pred_labels: list[str] = []
    for i, row in enumerate(gold_rows):
        idx_raw = clean(row.get("sentence_index"))
        try:
            idx = int(float(idx_raw)) if idx_raw else i
        except Exception:
            idx = i
        gold_labels.append(as_label(row.get("ground_truth_label")))
        pred_labels.append(pred_by_idx.get(idx, "NOBORDER"))
    return gold_labels, pred_labels


def apply_burst_collapse(pred_labels: list[str]) -> list[str]:
    out: list[str] = []
    prev = "NOBORDER"
    for label in pred_labels:
        if label == "BORDER" and prev == "BORDER":
            out.append("NOBORDER")
        else:
            out.append(label)
        prev = out[-1]
    return out


def apply_min_scene_len(pred_labels: list[str], min_gap: int) -> list[str]:
    out = pred_labels[:]
    last_kept_border = -10**9
    for i, label in enumerate(out):
        if label != "BORDER":
            continue
        if i - last_kept_border < min_gap:
            out[i] = "NOBORDER"
        else:
            last_kept_border = i
    return out


def scenario_predictions(pred_labels: list[str], scenario: str) -> list[str]:
    if scenario in {"none", "baseline"}:
        return pred_labels
    if scenario == "burst_collapse":
        return apply_burst_collapse(pred_labels)
    if scenario == "min_scene_len_3":
        return apply_min_scene_len(pred_labels, min_gap=3)
    if scenario == "min_scene_len_5":
        return apply_min_scene_len(pred_labels, min_gap=5)
    if scenario == "burst_collapse_plus_min_scene_len_3":
        return apply_min_scene_len(apply_burst_collapse(pred_labels), min_gap=3)
    raise ValueError(f"Unsupported scenario: {scenario}")


def confusion(pred_labels: list[str], gold_labels: list[str]) -> dict[str, int]:
    tp = fp = fn = tn = 0
    for p, g in zip(pred_labels, gold_labels):
        if p == "BORDER" and g == "BORDER":
            tp += 1
        elif p == "BORDER" and g == "NOBORDER":
            fp += 1
        elif p == "NOBORDER" and g == "BORDER":
            fn += 1
        else:
            tn += 1
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn}


def score_tolerant(pred_labels: list[str], gold_labels: list[str], tolerance: int) -> dict[str, float]:
    tp = fp = fn = 0
    n = len(gold_labels)

    for i in range(n):
        if gold_labels[i] != "BORDER":
            continue
        lo = max(0, i - tolerance)
        hi = min(n, i + tolerance + 1)
        if any(pred_labels[j] == "BORDER" for j in range(lo, hi)):
            tp += 1
        else:
            fn += 1

    for i in range(n):
        if pred_labels[i] != "BORDER":
            continue
        lo = max(0, i - tolerance)
        hi = min(n, i + tolerance + 1)
        if not any(gold_labels[j] == "BORDER" for j in range(lo, hi)):
            fp += 1

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "tp": tp,
        "fp": fp,
        "fn": fn,
    }


def summarize_exact(pred_labels: list[str], gold_labels: list[str]) -> dict[str, Any]:
    c = confusion(pred_labels, gold_labels)
    tp, fp, fn, tn = c["tp"], c["fp"], c["fn"], c["tn"]
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    acc = (tp + tn) / len(gold_labels) if gold_labels else 0.0
    return {
        "n_rows": len(gold_labels),
        "predicted_borders": sum(1 for p in pred_labels if p == "BORDER"),
        "gold_borders": sum(1 for g in gold_labels if g == "BORDER"),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "accuracy": round(acc, 4),
        "confusion": c,
    }


def compute_scenarios(
    gold_labels: list[str],
    pred_labels: list[str],
    scenario_names: list[str],
) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for name in scenario_names:
        preds = scenario_predictions(pred_labels, name)
        out[name] = {
            "exact": summarize_exact(preds, gold_labels),
            "tolerance": {
                "tol_0": score_tolerant(preds, gold_labels, tolerance=0),
                "tol_1": score_tolerant(preds, gold_labels, tolerance=1),
                "tol_3": score_tolerant(preds, gold_labels, tolerance=3),
                "tol_5": score_tolerant(preds, gold_labels, tolerance=5),
            },
        }
    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gaensemagd_gold", type=Path, required=True)
    parser.add_argument("--gaensemagd_review", type=Path, required=True)
    parser.add_argument("--kleist_gold", type=Path, required=True)
    parser.add_argument("--kleist_review", type=Path, required=True)
    parser.add_argument("--out_json", type=Path, required=True)
    parser.add_argument("--out_csv", type=Path, required=True)
    parser.add_argument(
        "--scenarios",
        nargs="+",
        default=["none", "min_scene_len_3", "min_scene_len_5"],
        help=(
            "Scenario list in comparison order. Supported: "
            "none/baseline, min_scene_len_3, min_scene_len_5, "
            "burst_collapse, burst_collapse_plus_min_scene_len_3"
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    scenario_names = args.scenarios
    dataset_specs = [
        ("gaensemagd", args.gaensemagd_gold, args.gaensemagd_review),
        ("kleist", args.kleist_gold, args.kleist_review),
    ]

    per_text: dict[str, Any] = {}
    table_rows: list[dict[str, Any]] = []
    aggregate_pool: dict[str, dict[str, list[str]]] = {}

    for name, gold_path, review_path in dataset_specs:
        gold_labels, pred_labels = build_aligned_sequences(
            read_gold_csv(gold_path),
            read_review_jsonl(review_path),
        )
        per_text[name] = compute_scenarios(gold_labels, pred_labels, scenario_names=scenario_names)

        for scenario in scenario_names:
            aggregate_pool.setdefault(scenario, {"gold": [], "pred": []})
            aggregate_pool[scenario]["gold"].extend(gold_labels)
            scenario_preds = scenario_predictions(pred_labels, scenario)
            aggregate_pool[scenario]["pred"].extend(scenario_preds)

            exact = per_text[name][scenario]["exact"]
            table_rows.append(
                {
                    "scope": name,
                    "scenario": scenario,
                    "n_rows": exact["n_rows"],
                    "predicted_borders": exact["predicted_borders"],
                    "gold_borders": exact["gold_borders"],
                    "precision": exact["precision"],
                    "recall": exact["recall"],
                    "f1": exact["f1"],
                    "accuracy": exact["accuracy"],
                    "tol3_f1": per_text[name][scenario]["tolerance"]["tol_3"]["f1"],
                    "tol5_f1": per_text[name][scenario]["tolerance"]["tol_5"]["f1"],
                }
            )

    aggregate: dict[str, Any] = {}
    for scenario, seqs in aggregate_pool.items():
        aggregate[scenario] = {
            "exact": summarize_exact(seqs["pred"], seqs["gold"]),
            "tolerance": {
                "tol_0": score_tolerant(seqs["pred"], seqs["gold"], tolerance=0),
                "tol_1": score_tolerant(seqs["pred"], seqs["gold"], tolerance=1),
                "tol_3": score_tolerant(seqs["pred"], seqs["gold"], tolerance=3),
                "tol_5": score_tolerant(seqs["pred"], seqs["gold"], tolerance=5),
            },
        }
        exact = aggregate[scenario]["exact"]
        table_rows.append(
            {
                "scope": "aggregate",
                "scenario": scenario,
                "n_rows": exact["n_rows"],
                "predicted_borders": exact["predicted_borders"],
                "gold_borders": exact["gold_borders"],
                "precision": exact["precision"],
                "recall": exact["recall"],
                "f1": exact["f1"],
                "accuracy": exact["accuracy"],
                "tol3_f1": aggregate[scenario]["tolerance"]["tol_3"]["f1"],
                "tol5_f1": aggregate[scenario]["tolerance"]["tol_5"]["f1"],
            }
        )

    payload = {
        "inputs": {
            "gaensemagd_gold": str(args.gaensemagd_gold),
            "gaensemagd_review": str(args.gaensemagd_review),
            "kleist_gold": str(args.kleist_gold),
            "kleist_review": str(args.kleist_review),
        },
        "per_text": per_text,
        "aggregate": aggregate,
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    with args.out_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(table_rows[0].keys()))
        writer.writeheader()
        writer.writerows(table_rows)

    print(f"Wrote JSON: {args.out_json}")
    print(f"Wrote CSV: {args.out_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
