---
note_type: run
run_id: run_20260611_finetune_stss2_e0_full
title: "STSS-Test-2 E0 full folds — HF Job (fold_A + fold_B)"
date: 2026-06-11
track: llama
run_type: experiment
status: partial
goal: "Train LOO folds on STSS-Test-2 only (Aus guter Familie ↔ Effi Briest); validate finetune pipeline at paper-like build settings."
entrypoint: "src/finetune/hf_jobs/submit_job.sh"
command: "HF_USER=RuthonField DATA_SCOPE=stss_test_2 RUN_CONFIG=src/finetune/hf_jobs/configs/stss_test_2/E0_full.json COMPUTE=jobs FLAVOR=t4-small TIMEOUT=8h BUILD_MODE=skip bash src/finetune/hf_jobs/submit_job.sh"
working_directory: "."
git_commit: ""
environment: "HF Jobs t4-small"
os: "Linux"
hardware: "HF Jobs GPU"
gpu: "t4-small"
cuda_notes: ""
api_provider: ""
api_model: ""
api_cost_estimate: "~$3–4 (both folds, 8h timeout cap)"
dataset_assets:
  - "upstream/scene-segmentation/data/full/stss_test_2/Aus guter Familie.xmi.zip"
  - "upstream/scene-segmentation/data/full/stss_test_2/Effi Briest.xmi.zip"
  - "RuthonField/scene-seg-sft (fold_A, fold_B)"
label_schema: "binary BORDER/NOBORDER (scene-only parser)"
prompt_version: "family L, cot_list"
model_name: "unsloth/Llama-3.2-3B-Instruct"
varying_factor: "none (E0 pipeline validation)"
fixed_conditions:
  - "stss_only folds, tokens512 context, paper10pct negatives"
  - "LoRA r=16 alpha=16, 1 epoch, completion_only_loss=true"
  - "debug=true — not reportable performance"
random_seed: "1337"
output_dir: "https://huggingface.co/RuthonField"
artifacts_expected:
  - "scene-seg-llama-3-2-3b-instruct-fold_A + metrics"
  - "scene-seg-llama-3-2-3b-instruct-fold_B + metrics"
artifacts_produced:
  - "HF Job 6a2a38d6c4f53f9fc5aa4a91"
main_metric_name: "scenarios.none.tol_3.macro_f1"
main_metric_value: ""
precision: ""
recall: ""
f1: ""
iou: ""
runtime: ""
failure_category: ""
related_experiment: "experiment__finetune__hf-jobs-qlora-campaign"
related_issue: ""
decision_relevance: true
notion_targets:
  roadmap: ""
  runs: true
  experiments: "experiment__finetune__hf-jobs-qlora-campaign"
  artifacts: true
  issues: false
  decisions: "decision__finetune-stss-test-2-stage"
---

## Objective

Complete STSS-Test-2 stage E0: both LOO folds with `--stss_only`, paper-like build (`tokens512`,
`paper10pct`), full eval on held-out novel.

## What was held constant

- Two novels only; no Excel training texts.
- CoT-List target format, family L.
- QLoRA hyperparams per plan defaults.

## What changed

- Rebuilt SFT data: fold_A train=633 (145 B / 488 NB), fold_B train=745 (172 B / 573 NB).
- Default `DATA_SCOPE=stss_test_2` in submit pipeline.
- Prior fold_A adapter used Excel + sentences context; this run uses STSS-only + tokens512.

## Outcome

- Dataset uploaded: `RuthonField/scene-seg-sft`.
- HF Job submitted: https://huggingface.co/jobs/RuthonField/6a2a38d6c4f53f9fc5aa4a91
- Awaiting adapters + metrics on Hub.

## Interpretation

LOO fold metrics diagnose pipeline and learning signal only. Prior fold_A run showed mode collapse
(all NOBORDER); this rebuild removes Excel mix-in and aligns context with paper settings.

## Next step

- Monitor job; log artifact notes when metrics land.
- If still collapsed: try `E0_anchor.json` (2 epochs) or E3/E4 factor sweeps on stss_test_2 scope.
- When full corpus arrives: `DATA_SCOPE=corpus` for E1 anchor.
