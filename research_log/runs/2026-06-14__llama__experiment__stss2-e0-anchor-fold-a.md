---
note_type: run
run_id: run_20260614_finetune_stss2_e0_anchor_fold_a
title: "STSS-Test-2 E0 anchor — fold_A, 2 epochs (HF Job)"
date: 2026-06-14
track: llama
run_type: experiment
status: completed
goal: "After E3 json still collapsed (n_pred_border=0), test 2 epochs + cot_list + completion_only_loss on fold_A for any BORDER signal."
entrypoint: "src/finetune/hf_jobs/submit_job.sh"
command: "HF_USER=RuthonField DATA_SCOPE=stss_test_2 BUILD_ARGS='--stss_only --target_format cot_list --negative_mode paper10pct --context_mode tokens512' RUN_CONFIG=src/finetune/hf_jobs/configs/stss_test_2/E0_anchor.json JOBS=fold_A FLAVOR=t4-small TIMEOUT=8h RESUME=0 bash src/finetune/hf_jobs/submit_job.sh"
working_directory: "."
git_commit: ""
environment: "HF Jobs t4-small"
os: "Linux"
hardware: "HF Jobs GPU"
gpu: "t4-small"
cuda_notes: ""
api_provider: ""
api_model: ""
api_cost_estimate: "~$2.00–2.80 (est. 5–7h)"
dataset_assets:
  - "RuthonField/scene-seg-sft (fold_A cot_list rebuild)"
label_schema: "binary BORDER/NOBORDER"
prompt_version: "family L, cot_list target"
model_name: "unsloth/Llama-3.2-3B-Instruct"
varying_factor: "epochs=2, completion_only_loss=true (E0_anchor vs E3 json)"
fixed_conditions:
  - "stss_test_2 LOO fold_A only"
  - "paper10pct negatives, tokens512"
random_seed: "1337"
output_dir: "https://huggingface.co/RuthonField"
artifacts_expected:
  - "scene-seg-llama-3-2-3b-instruct-fold_A"
  - "metrics_llama-3-2-3b-instruct_fold_A.json"
artifacts_produced:
  - "HF Job 6a2f6f83871c005b5352cffc"
  - "RuthonField/scene-seg-llama-3-2-3b-instruct-fold_A"
  - "metrics_llama-3-2-3b-instruct_fold_A.json"
main_metric_name: "n_pred_border / scenarios.none.tol_3.macro_f1"
main_metric_value: "n_pred_border=0; macro_f1@3=0.0"
f1: "0.0"
runtime: "~4.5h (03:21–07:48 UTC)"
failure_category: ""
related_experiment: "experiment__finetune__hf-jobs-qlora-campaign"
related_issue: "issue__infra__hf-run-config-not-loaded-on-jobs"
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

Follow-up to E3 json (still `n_pred_border=0` with valid JSON-only outputs): test whether more epochs and completion-only loss on cot_list produce any BORDER predictions.

## What was held constant

- LOO fold_A (train Aus guter Familie → eval Effi Briest).
- Llama-3.2-3B QLoRA, paper-like build settings.

## What changed

- Rebuilt `cot_list` targets (from E3 json build).
- `epochs: 2`, `completion_only_loss: true` (E0_anchor config).

## HF Job

- **Job ID (active):** `6a2f6f83871c005b5352cffc` — https://huggingface.co/jobs/RuthonField/6a2f6f83871c005b5352cffc
- **Canceled:** `6a2f3c6d871c005b5352cc7d` (1-epoch smoke; config bug)
- **Failed first attempt:** `6a2f3b9a871c005b5352cc64` (missing `discourse_filters` in bundle)
- **Build:** fold_A train=633 (B=145), eval=5906 (B=172), cot_list, max_seq_len=1280
- **Config on Hub:** `epochs=2`, `jobs=[fold_A]`, `debug=true` (JOBS override applied)

## Progress (2026-06-15)

- Resubmitted with `hf_run_config.json` dataset-root loading fix + `JOBS=fold_A` override.
- Expect logs: `epochs=2`, `preflight=20`, `Num Epochs = 2`.

## Outcome

**COMPLETED** (job `6a2f6f83871c005b5352cffc`, ~4.5h).

| Metric | Value |
|--------|-------|
| Config loaded | `epochs=2`, `preflight=20`, `cot_list` ✓ |
| Preflight (20 rows) | `n_pred_border=0`, `macro_f1@3=0.0`, `parse_fail=0%` |
| Full eval (5906 rows) | `n_pred_border=0`, `macro_f1@3=0.0`, `parse_fail=0%` |
| `avg_output_chars` | **306** (CoT-length; vs E3 json **40**) |
| `run_phase` | `stss_test_2_anchor` |

**Pass criterion failed:** still zero BORDER predictions despite valid parsing.

## Interpretation

- Infra fix worked: true 2-epoch E0_anchor ran as specified.
- Model still **mode-collapses to NOBORDER** on cot_list (306-char outputs, 0 parse failures — same pattern as original E0 adapter, not E3's short JSON).
- E3 json and E0 cot_list (1 or 2 epochs, completion-only loss) both yield `n_pred_border=0` on fold_A eval.
- Problem is likely **task/data/capacity**, not output format or epoch count alone.

## Next step

- Try factors from finetune plan: more epochs, class weighting, hard negatives, or larger model before more format sweeps.
- Commit infra fixes (`train_job.py`, `submit_job.sh`, `discourse_filters` bundle).
