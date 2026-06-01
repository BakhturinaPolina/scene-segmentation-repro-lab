---
note_type: experiment
experiment_id: exp_prompting_post_processing_excel_controlled_sweep
title: "Excel-manifest one-factor post-processing sweep after fresh full-eval rerun"
date_opened: 2026-05-30
track: prompting
status: concluded
factor_under_test: "post-processing rule (none vs min_scene_len_3 vs min_scene_len_5)"
baseline_run_id: "run_20260530_excel_controlled_postprocessing_sweep"
hypothesis: "Holding model/prompt/decode/full-eval fixed, increasing minimum scene length will suppress fragmentation-driven false positives and improve tolerant (`tol3`, `tol5`) metrics, with a potential exact-recall tradeoff."
fixed_conditions:
  - "model = nvidia/nemotron-3-super-120b-a12b"
  - "prompt family = B"
  - "eval mode = full_eval on data/processed/manifest_excel_prompting.json"
  - "decode = temperature=0, top_p=1.0, seed=1337, max_tokens=256"
  - "response_format = json_schema with src/prompts/json_schema_label_reason.json"
variants:
  - "none (baseline)"
  - "min_scene_len_3"
  - "min_scene_len_5"
success_metric: "aggregate tolerant F1 (tol5), while tracking aggregate exact F1"
comparison_rule: "Prefer highest tol5 F1 among variants; reject variant if exact F1 collapses beyond acceptable boundary-quality tradeoff."
related_runs:
  - "run_20260530_excel_controlled_postprocessing_sweep"
related_artifacts:
  - "artifact__excel-controlled-postprocessing-sweep__postprocessing-comparison-table"
  - "artifact__excel-controlled-postprocessing-sweep__scenario-fp-review-tables"
notion_targets:
  experiments: true
  runs: true
  artifacts: true
  decisions: false
---

## Research question

For Excel-manifest scene segmentation with fixed family-B prompting controls, which minimum-scene-length post-processing setting gives the best tolerance-aware boundary quality without unacceptable exact-metric regression?

## Baseline

`none` post-processing on the fresh full-eval run (`run_20260530_excel_controlled_postprocessing_sweep`) with aggregate exact F1 around `0.10`.

## Constants

See `fixed_conditions` in frontmatter.

## Variants

Single-factor sweep across:
- `none`
- `min_scene_len_3`
- `min_scene_len_5`

## Evaluation rule

Compare aggregate rows in `outputs/review/excel_controlled_sweep/comparison/normalization_what_if.csv`:
- exact metrics: precision/recall/F1
- tolerant metrics: tol3_F1, tol5_F1

Use FP tables per scenario for qualitative support.

## Interim conclusion

`min_scene_len_3` and `min_scene_len_5` both improve tolerant metrics over `none`; stronger filtering (`min_scene_len_5`) provides the highest tolerant gains.

## Final conclusion

Experiment supports the hypothesis that fragmentation suppression helps tolerant boundary quality:
- `tol5_F1`: `0.4242` (`none`) -> `0.5676` (`min_scene_len_3`) -> `0.6667` (`min_scene_len_5`).
- Tradeoff: exact F1 decreases modestly (`0.0993` -> `0.0909` -> `0.0896`).

For tolerance-oriented evaluation objectives on this Excel-manifest family, `min_scene_len_5` is the leading candidate.
