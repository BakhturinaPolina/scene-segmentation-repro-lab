"""Boundary post-processing rules and a self-contained tolerant scorer.

The rule functions operate on a positionally ordered list of labels
("BORDER"/"NOBORDER"). ``evaluate_sampled`` mirrors the semantics of
``src/runners/run_prompting_stratified.py::evaluate_sampled`` (lines 521-559) so
that re-scoring a post-processed prediction set yields numbers directly
comparable to the runner's own metrics.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence


# ---------------------------------------------------------------------------
# Rules
# ---------------------------------------------------------------------------

def apply_min_scene_len(pred_labels: Sequence[str], min_gap: int) -> List[str]:
    """Suppress any BORDER that occurs within ``min_gap`` positions of the
    previously kept BORDER. Mirrors the rule in
    ``scripts/evaluation/export_top_fp_review_table.py``.
    """
    out = list(pred_labels)
    last_kept_border = -10 ** 9
    for i, label in enumerate(out):
        if label != "BORDER":
            continue
        if i - last_kept_border < min_gap:
            out[i] = "NOBORDER"
        else:
            last_kept_border = i
    return out


def apply_burst_collapse(pred_labels: Sequence[str]) -> List[str]:
    """Collapse consecutive BORDER predictions, keeping only the first."""
    out: List[str] = []
    prev = "NOBORDER"
    for label in pred_labels:
        if label == "BORDER" and prev == "BORDER":
            out.append("NOBORDER")
        else:
            out.append(label)
        prev = out[-1]
    return out


def apply_confidence_threshold(
    pred_labels: Sequence[str],
    confidences: Sequence[Optional[float]],
    threshold: float,
) -> List[str]:
    """Demote BORDER -> NOBORDER when its confidence is below ``threshold``.

    Predictions with a missing confidence (None) are kept as-is, so the rule is
    conservative when the model did not emit a confidence value.
    """
    if len(pred_labels) != len(confidences):
        raise ValueError("pred_labels and confidences must be the same length")
    out = list(pred_labels)
    for i, label in enumerate(out):
        if label != "BORDER":
            continue
        conf = confidences[i]
        if conf is not None and conf < threshold:
            out[i] = "NOBORDER"
    return out


def apply_scenario(
    pred_labels: Sequence[str],
    scenario: str,
    confidences: Optional[Sequence[Optional[float]]] = None,
    confidence_threshold: float = 0.85,
) -> List[str]:
    """Dispatch a named scenario to the corresponding rule(s)."""
    if scenario in {"none", "baseline"}:
        return list(pred_labels)
    if scenario == "min_scene_len_3":
        return apply_min_scene_len(pred_labels, min_gap=3)
    if scenario == "min_scene_len_5":
        return apply_min_scene_len(pred_labels, min_gap=5)
    if scenario == "burst_collapse":
        return apply_burst_collapse(pred_labels)
    if scenario == "burst_collapse_plus_min_scene_len_3":
        return apply_min_scene_len(apply_burst_collapse(pred_labels), min_gap=3)
    if scenario == "confidence_threshold":
        if confidences is None:
            raise ValueError("confidence_threshold scenario requires confidences")
        return apply_confidence_threshold(pred_labels, confidences, confidence_threshold)
    if scenario == "confidence_threshold_plus_min_scene_len_3":
        if confidences is None:
            raise ValueError("scenario requires confidences")
        thr = apply_confidence_threshold(pred_labels, confidences, confidence_threshold)
        return apply_min_scene_len(thr, min_gap=3)
    raise ValueError(f"Unsupported scenario: {scenario}")


SCENARIOS = (
    "none",
    "min_scene_len_3",
    "min_scene_len_5",
    "burst_collapse",
    "burst_collapse_plus_min_scene_len_3",
    "confidence_threshold",
    "confidence_threshold_plus_min_scene_len_3",
)


# ---------------------------------------------------------------------------
# Scorer (mirror of run_prompting_stratified.evaluate_sampled)
# ---------------------------------------------------------------------------

def evaluate_sampled(
    sampled_indices: Sequence[int],
    sampled_preds: Sequence[str],
    full_gold_labels: Sequence[str],
    tolerance: int,
) -> Dict[str, float]:
    """Compute P/R/F1 for the BORDER class with positional tolerance.

    Identical semantics to the runner's evaluator: recall counts each sampled
    gold BORDER that has a predicted BORDER within +-tolerance among sampled
    positions; precision counts each predicted BORDER lacking a gold BORDER
    within +-tolerance.
    """
    pred_by_idx = dict(zip(sampled_indices, sampled_preds))
    sampled_set = set(sampled_indices)
    n = len(full_gold_labels)

    tp = fp = fn = 0
    for idx in sampled_indices:
        if full_gold_labels[idx] != "BORDER":
            continue
        window = range(max(0, idx - tolerance), min(n, idx + tolerance + 1))
        found = any(pred_by_idx.get(j) == "BORDER" for j in window if j in sampled_set)
        if found:
            tp += 1
        else:
            fn += 1

    for idx in sampled_indices:
        if pred_by_idx[idx] != "BORDER":
            continue
        window = range(max(0, idx - tolerance), min(n, idx + tolerance + 1))
        if not any(full_gold_labels[j] == "BORDER" for j in window):
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
