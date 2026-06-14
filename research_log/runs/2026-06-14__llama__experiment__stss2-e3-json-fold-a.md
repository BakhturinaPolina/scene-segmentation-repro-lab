---
note_type: run
run_id: run_20260614_finetune_stss2_e3_json_fold_a
title: "STSS-Test-2 E3 json — fold_A train (HF Job)"
date: 2026-06-14
track: llama
run_type: experiment
status: partial
goal: "Test whether JSON-only target format produces any BORDER predictions on 2-text LOO fold_A (vs E0 cot_list collapse)."
entrypoint: "src/finetune/hf_jobs/submit_job.sh"
command: "HF_USER=RuthonField DATA_SCOPE=stss_test_2 BUILD_ARGS='--stss_only --target_format json --negative_mode paper10pct --context_mode tokens512' RUN_CONFIG=src/finetune/hf_jobs/configs/stss_test_2/E3_json.json JOBS=fold_A FLAVOR=t4-small TIMEOUT=6h RESUME=0 bash src/finetune/hf_jobs/submit_job.sh"
working_directory: "."
git_commit: ""
environment: "HF Jobs t4-small"
os: "Linux"
hardware: "HF Jobs GPU"
gpu: "t4-small"
cuda_notes: ""
api_provider: ""
api_model: ""
api_cost_estimate: "~$1.20–1.80 (est. 3–4.5h)"
dataset_assets:
  - "RuthonField/scene-seg-sft (fold_A json build)"
label_schema: "binary BORDER/NOBORDER"
prompt_version: "family L, json target"
model_name: "unsloth/Llama-3.2-3B-Instruct"
varying_factor: "target_format=json (E3)"
fixed_conditions:
  - "stss_test_2 LOO fold_A only"
  - "1 epoch, completion_only_loss=false"
  - "633 train rows, full eval 5906"
random_seed: "1337"
output_dir: "https://huggingface.co/RuthonField"
artifacts_expected:
  - "scene-seg-llama-3-2-3b-instruct-fold_A (overwritten)"
  - "metrics_llama-3-2-3b-instruct_fold_A.json"
artifacts_produced:
  - "HF Job 6a2e0eef234ca64b601226ba"
main_metric_name: "n_pred_border / scenarios.none.tol_3.macro_f1"
main_metric_value: ""
precision: ""
recall: ""
f1: ""
iou: ""
runtime: "est. 3–4.5h"
failure_category: ""
related_experiment: "experiment__finetune__hf-jobs-qlora-campaign"
related_issue: ""
decision_relevance: false
notion_targets:
  roadmap: ""
  runs: true
  experiments: "experiment__finetune__hf-jobs-qlora-campaign"
  artifacts: true
  issues: false
  decisions: false
---

## Objective

Answer on 2-text scope: does E3 json produce any BORDER predictions (`n_pred_border > 0`)?

## What was held constant

- LOO fold_A (train Aus guter Familie → eval Effi Briest).
- Llama-3.2-3B QLoRA, 1 epoch, paper-like negatives/context.

## What changed

- Rebuilt SFT with `--target_format json` (assistant = JSON label only).
- `completion_only_loss: false` (E3 setting).
- `eval_preflight_rows: 20` for early parse/pred diagnostics in train_job.

## Outcome

- Data built: train=633 (145 B / 488 NB), eval=5906 (172 B), `target_format=json`, stss_only.
- Dataset uploaded: RuthonField/scene-seg-sft.
- HF Job: https://huggingface.co/jobs/RuthonField/6a2e0eef234ca64b601226ba
  (first submission cancelled — missing `--stss_only` in BUILD_ARGS)

## Interpretation

Pending job completion. Pass criterion: `n_pred_border > 0` on preflight or full eval; F1 not required on debug scope.

## Next step

- Monitor job logs; spot-check metrics when complete.
- If still collapse: submit E0_anchor (2 epochs, cot_list) on fold_A.
