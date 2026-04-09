---
note_type: run
run_id: run_20260408_prompting_gptoss120b_stratified
title: "Stratified prompting: openai/gpt-oss-120b:free on 2 novels (max 15 per class)"
date: 2026-04-08
track: prompting
run_type: baseline
status: success
goal: "Evaluate GPT-OSS-120b on stratified scene boundary sample (15 BORDER + 15 NOBORDER per novel)"
entrypoint: "python src/run_prompting_stratified.py"
command: >
  OPENROUTER_API_KEY=... .venv/bin/python src/run_prompting_stratified.py
    --model "openai/gpt-oss-120b:free"
    --max_per_class 15
    --date 2026-04-08-stratified-gptoss
working_directory: "."
git_commit: "80d4233"
environment: ".venv (CPU)"
os: "Linux 6.17.0-111019-tuxedo"
hardware: "CPU only (API inference)"
gpu: ""
cuda_notes: ""
api_provider: "OpenRouter"
api_model: "openai/gpt-oss-120b:free"
api_cost_estimate: "$0.00 (free tier)"
dataset_assets:
  - "data/full/stss_test_2/Aus guter Familie.xmi.zip"
  - "data/full/stss_test_2/Effi Briest.xmi.zip"
label_schema: "Coarse (BORDER / NOBORDER)"
prompt_version: "prompt_classify (upstream default)"
model_name: "openai/gpt-oss-120b:free"
varying_factor: "none"
fixed_conditions:
  - "context_size=409 tokens (512 * 0.8)"
  - "max_per_class=15"
  - "seed=1337"
  - "stratified sampling: all BORDERs (capped) + evenly-spaced NOBORDERs"
random_seed: "1337"
output_dir: "outputs/prompting/2026-04-08-stratified-gptoss/stratified_openai_gpt-oss-120b_free"
artifacts_expected:
  - "cache_Aus_guter_Familie.json"
  - "cache_Effi_Briest.json"
  - "results_Aus_guter_Familie.json"
  - "results_Effi_Briest.json"
  - "summary.json"
artifacts_produced:
  - "cache_Aus_guter_Familie.json (30 entries)"
  - "cache_Effi_Briest.json (30 entries)"
  - "results_Aus_guter_Familie.json"
  - "results_Effi_Briest.json"
  - "summary.json"
main_metric_name: "macro_avg F1 (tol=0)"
main_metric_value: "0.696"
precision: "1.000"
recall: "0.533"
f1: "0.696"
iou: ""
runtime: "~4 min (60 sentences, ~4s/sentence avg)"
failure_category: ""
related_experiment: "experiment__prompting__model__free-120b-comparison"
related_issue: ""
decision_relevance: false
notion_targets:
  roadmap: "Phase 3"
  runs: true
  experiments: true
  artifacts: true
  issues: false
  decisions: false
---

## Objective

Evaluate the GPT-OSS-120b model (free tier via OpenRouter) on stratified scene boundary classification, using 15 BORDER + 15 NOBORDER sentences per novel.

## What was held constant

- Upstream default scene classification prompt (`prompt_classify`)
- Context window ~409 tokens
- Stratified sampling with seed 1337
- LangChain chain with conversation memory (cleared after each response)
- Both novels in stss_test_2

## What changed

- First use of `openai/gpt-oss-120b:free` model
- Stratified sampling (vs. sequential in prior baseline)

## Outcome

| Document | Accuracy | P (tol=0) | R (tol=0) | F1 (tol=0) | TP | FP | FN |
|---|---|---|---|---|---|---|---|
| Aus guter Familie | 76.7% | 1.000 | 0.533 | 0.696 | 8 | 0 | 7 |
| Effi Briest | 76.7% | 1.000 | 0.533 | 0.696 | 8 | 0 | 7 |
| **Macro Avg** | | **1.000** | **0.533** | **0.696** | | | |

- Tolerance had no effect (tol_0 = tol_1 = tol_3) because FP=0 everywhere.
- Identical per-document metrics is coincidental but reflects consistent model behavior.

## Interpretation

GPT-OSS-120b is extremely conservative: perfect precision (zero false positives) but misses ~47% of real borders. Every error is a false negative. The model only detects borders with very explicit signals (chapter markers, clear temporal jumps) and fails on subtle narrative transitions.

## Next step

Compare with Nemotron-3-Super-120b to see if a different free model can improve recall without destroying precision.
