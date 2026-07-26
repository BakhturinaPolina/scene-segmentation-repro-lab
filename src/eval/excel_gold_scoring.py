"""Score batch predictions against Excel-derived close-reading gold labels.

Computes sentence-level precision/recall/F1 for the minority BORDER class at
tolerances 0, 1 and 3, matching Zehe et al.'s relaxed-F1 protocol and the
tolerance logic in ``src/runners/run_prompting_stratified.py::evaluate_sampled``.

Index convention: the Excel gold CSV and the ``predictions.jsonl`` both use
1-based ``sentence_index``; we convert to a dense 0-based array per document
before scoring, so both sides align on the same positions.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

DEFAULT_TOLERANCES = (0, 1, 3)


def normalize_label(value: Any) -> str:
    token = str(value).strip().upper() if value is not None else ""
    if token in {"BORDER", "TRUE", "YES", "1"}:
        return "BORDER"
    return "NOBORDER"


def load_gold_labels(gold_csv: Path, index_base: int = 1) -> list[str]:
    """Return a dense 0-based list of gold labels for one document."""
    rows: list[tuple[int, str]] = []
    with gold_csv.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            idx = int(float(row["sentence_index"])) - index_base
            rows.append((idx, normalize_label(row.get("ground_truth_label"))))
    if not rows:
        return []
    n = max(idx for idx, _ in rows) + 1
    labels = ["NOBORDER"] * n
    for idx, label in rows:
        if 0 <= idx < n:
            labels[idx] = label
    return labels


def load_predictions_by_slug(predictions_jsonl: Path) -> dict[str, dict[int, str]]:
    """Map slug -> {0-based position: predicted label} from predictions.jsonl."""
    by_slug: dict[str, dict[int, str]] = {}
    with predictions_jsonl.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            key = row.get("key") or ""
            slug = key.split(":", 1)[0] if ":" in key else (row.get("source_file") or "")
            idx_raw = row.get("sentence_index")
            if idx_raw is None:
                continue
            # jsonl sentence_index is 1-based -> 0-based position
            pos = int(float(idx_raw)) - 1
            label = row.get("prediction_label")
            by_slug.setdefault(slug, {})[pos] = normalize_label(label)
    return by_slug


def score_with_tolerance(
    pred_by_pos: dict[int, str],
    gold_labels: list[str],
    tolerance: int,
) -> dict[str, Any]:
    """P/R/F1 on the BORDER class with a symmetric tolerance window.

    Mirrors evaluate_sampled: a predicted BORDER counts as TP if any gold
    BORDER sits within +-tolerance; a gold BORDER is recalled if any predicted
    BORDER sits within +-tolerance.
    """
    n = len(gold_labels)
    tp = fp = fn = 0

    for idx in range(n):
        if gold_labels[idx] != "BORDER":
            continue
        window = range(max(0, idx - tolerance), min(n, idx + tolerance + 1))
        if any(pred_by_pos.get(j) == "BORDER" for j in window):
            tp += 1
        else:
            fn += 1

    for idx, label in pred_by_pos.items():
        if label != "BORDER":
            continue
        if idx < 0 or idx >= n:
            continue
        window = range(max(0, idx - tolerance), min(n, idx + tolerance + 1))
        if not any(gold_labels[j] == "BORDER" for j in window):
            fp += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def score_document(
    slug: str,
    pred_by_pos: dict[int, str],
    gold_labels: list[str],
    tolerances: tuple[int, ...] = DEFAULT_TOLERANCES,
) -> dict[str, Any]:
    n = len(gold_labels)
    gold_borders = sum(1 for x in gold_labels if x == "BORDER")
    pred_borders = sum(1 for p in pred_by_pos.values() if p == "BORDER")
    result: dict[str, Any] = {
        "slug": slug,
        "n_sentences": n,
        "gold_borders": gold_borders,
        "pred_borders": pred_borders,
        "over_prediction_ratio": round(pred_borders / gold_borders, 4) if gold_borders else None,
        "n_predicted": len(pred_by_pos),
    }
    for tol in tolerances:
        result[f"tol_{tol}"] = score_with_tolerance(pred_by_pos, gold_labels, tol)
    return result


def macro_average(per_doc: list[dict[str, Any]], tolerances: tuple[int, ...]) -> dict[str, Any]:
    macro: dict[str, Any] = {}
    for tol in tolerances:
        keys = ("precision", "recall", "f1")
        agg = {k: 0.0 for k in keys}
        for doc in per_doc:
            for k in keys:
                agg[k] += doc[f"tol_{tol}"][k]
        n = len(per_doc) or 1
        macro[f"macro_avg_tol_{tol}"] = {k: round(agg[k] / n, 4) for k in keys}
    return macro


def score_run(
    predictions_jsonl: Path,
    manifest: dict[str, Any],
    data_root: Path,
    tolerances: tuple[int, ...] = DEFAULT_TOLERANCES,
) -> dict[str, Any]:
    """Score one family's predictions.jsonl against all gold docs in the manifest."""
    index_base = int(manifest.get("index_base", 1))
    gold_by_slug: dict[str, list[str]] = {}
    for entry in manifest.get("files", []):
        slug = entry["slug"]
        gold_rel = entry.get("gold_csv")
        if not gold_rel:
            continue
        gold_by_slug[slug] = load_gold_labels(data_root / gold_rel, index_base=index_base)

    pred_by_slug = load_predictions_by_slug(predictions_jsonl)

    per_doc: list[dict[str, Any]] = []
    for slug, gold_labels in gold_by_slug.items():
        pred_by_pos = pred_by_slug.get(slug, {})
        per_doc.append(score_document(slug, pred_by_pos, gold_labels, tolerances))

    summary: dict[str, Any] = {
        "tolerances": list(tolerances),
        "per_document": per_doc,
    }
    summary.update(macro_average(per_doc, tolerances))
    total_gold = sum(d["gold_borders"] for d in per_doc)
    total_pred = sum(d["pred_borders"] for d in per_doc)
    summary["total_gold_borders"] = total_gold
    summary["total_pred_borders"] = total_pred
    summary["overall_over_prediction_ratio"] = (
        round(total_pred / total_gold, 4) if total_gold else None
    )
    return summary
