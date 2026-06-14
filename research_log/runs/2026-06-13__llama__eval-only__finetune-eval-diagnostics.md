---
note_type: run
run_id: run_20260613_finetune_eval_diagnostics
title: "Finetune eval diagnostics — shared parser, spot-check, preflight"
date: 2026-06-13
track: llama
run_type: eval-only
status: success
goal: "Add parse/truncation diagnostics to finetune eval so zero-F1 runs are diagnosable as parse failure vs model collapse."
entrypoint: "src/finetune/label_parse.py, src/finetune/eval_finetuned.py, src/finetune/diagnose_eval.py"
command: "python3 -m unittest tests.test_finetune_gaps -v"
working_directory: "."
git_commit: ""
environment: "local dev"
os: "Linux"
hardware: "CPU"
gpu: ""
cuda_notes: ""
api_provider: ""
api_model: ""
api_cost_estimate: ""
dataset_assets: []
label_schema: "binary BORDER/NOBORDER"
prompt_version: "family L"
model_name: ""
varying_factor: "none (infrastructure)"
fixed_conditions:
  - "No training run; code-only change"
random_seed: ""
output_dir: ""
artifacts_expected:
  - "src/finetune/label_parse.py"
  - "src/finetune/diagnose_eval.py"
artifacts_produced:
  - "src/finetune/label_parse.py"
  - "src/finetune/diagnose_eval.py"
  - "updated eval_finetuned.py, train_job.py, submit_job.sh"
main_metric_name: "unit_tests"
main_metric_value: "9/9 pass"
precision: ""
recall: ""
f1: ""
iou: ""
runtime: ""
failure_category: ""
related_experiment: ""
related_issue: ""
decision_relevance: false
notion_targets:
  roadmap: ""
  runs: true
  experiments: ""
  artifacts: true
  issues: false
  decisions: false
---

## Objective

Implement debugging checks for finetune eval: tolerant label parsing aligned with
`train_job.py`, parse-failure metrics, truncation heuristics, spot-check mode,
preflight eval in training, and offline `diagnose_eval.py`.

## What was held constant

- No change to training data or model weights.
- Family L prompt contract unchanged; strict parsing still available via `--parse_mode strict`.

## What changed

- New `src/finetune/label_parse.py`: shared tolerant parser, generation diagnostics, warning builder.
- `eval_finetuned.py`: tolerant default, `parse_ok` in partial cache, `--spot_check`, meta-aware `max_new_tokens`.
- `train_job.py`: uses shared parser; preflight eval (`eval_preflight_rows`); val callback logs parse rate.
- `diagnose_eval.py`: GPU-free partial/eval JSONL inspection.
- HF job bundle includes `label_parse.py`.

## Outcome

- All 9 unit tests in `tests/test_finetune_gaps.py` pass.
- Zero-F1 runs can now be classified via `parse_failure_rate`, `truncation_suspect_rate`, and `sample_parse_failures`.

## Interpretation

Infrastructure change only. Next eval runs should check `n_pred_border` vs `parse_failure_rate` before trusting F1.

## Next step

- Spot-check an existing adapter: `--spot_check 20 --spot_check_only`.
- If `parse_failure_rate` high with `cot_list`, confirm `max_new_tokens=256` or retrain with `E3_json` + `--target_format json`.
