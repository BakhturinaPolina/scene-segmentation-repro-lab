"""Post-processing rules for scene-boundary predictions.

Reusable boundary-smoothing rules (min scene length, burst collapse, confidence
threshold) plus a self-contained scorer mirroring
``run_prompting_stratified.evaluate_sampled`` so cached runs can be re-scored
without importing the heavy GPU/LLM runner dependencies.
"""

from .postprocess import (
    apply_burst_collapse,
    apply_confidence_threshold,
    apply_min_scene_len,
    apply_scenario,
    evaluate_sampled,
)

__all__ = [
    "apply_burst_collapse",
    "apply_confidence_threshold",
    "apply_min_scene_len",
    "apply_scenario",
    "evaluate_sampled",
]
