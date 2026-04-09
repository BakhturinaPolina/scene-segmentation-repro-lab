---
note_type: run
run_id: run_20260408_prompting_nemotron_stratified
title: "Stratified prompting: nvidia/nemotron-3-super-120b-a12b:free on 2 novels (full stratified)"
date: 2026-04-08
track: prompting
run_type: baseline
status: success
goal: "Evaluate Nemotron-3-Super-120b on full stratified scene boundary sample (all BORDERs + matched NOBORDERs)"
entrypoint: "python src/run_prompting_stratified.py"
command: >
  OPENROUTER_API_KEY=... .venv/bin/python src/run_prompting_stratified.py
    --model "nvidia/nemotron-3-super-120b-a12b:free"
    --date 2026-04-08-stratified-nemotron
working_directory: "."
git_commit: "80d4233"
environment: ".venv (CPU)"
os: "Linux 6.17.0-111019-tuxedo"
hardware: "CPU only (API inference)"
gpu: ""
cuda_notes: ""
api_provider: "OpenRouter"
api_model: "nvidia/nemotron-3-super-120b-a12b:free"
api_cost_estimate: "$0.00 (free tier)"
dataset_assets:
  - "data/full/stss_test_2/Aus guter Familie.xmi.zip"
  - "data/full/stss_test_2/Effi Briest.xmi.zip"
label_schema: "Coarse (BORDER / NOBORDER)"
prompt_version: "prompt_classify (upstream default)"
model_name: "nvidia/nemotron-3-super-120b-a12b:free"
varying_factor: "none"
fixed_conditions:
  - "context_size=409 tokens (512 * 0.8)"
  - "max_per_class=0 (all borders + matched noborders)"
  - "seed=1337"
  - "stratified sampling: all BORDERs + evenly-spaced NOBORDERs"
random_seed: "1337"
output_dir: "outputs/prompting/2026-04-08-stratified-nemotron/stratified_nvidia_nemotron-3-super-120b-a12b_free"
artifacts_expected:
  - "cache_Aus_guter_Familie.json"
  - "cache_Effi_Briest.json"
  - "results_Aus_guter_Familie.json"
  - "results_Effi_Briest.json"
  - "summary.json"
artifacts_produced:
  - "cache_Aus_guter_Familie.json (438 entries)"
  - "cache_Effi_Briest.json (454 entries)"
  - "results_Aus_guter_Familie.json"
  - "results_Effi_Briest.json"
  - "summary.json"
main_metric_name: "macro_avg F1 (tol=0)"
main_metric_value: "0.753"
precision: "0.890"
recall: "0.652"
f1: "0.753"
iou: ""
runtime: "~3h (892 sentences total, ~12s/sentence avg including rate limits)"
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

Evaluate the Nemotron-3-Super-120b model (free tier via OpenRouter) on the full stratified scene boundary sample — all gold BORDERs plus an equal number of evenly-spaced NOBORDERs per novel.

## What was held constant

- Upstream default scene classification prompt (`prompt_classify`)
- Context window ~409 tokens
- Stratified sampling with seed 1337
- LangChain chain with conversation memory (cleared after each response)
- Both novels in stss_test_2

## What changed

- Full stratified sample (max_per_class=0) vs. pilot run (max_per_class=15)

## Outcome

### Per-document results

| Document | Sentences | Accuracy | P (tol=0) | R (tol=0) | F1 (tol=0) | TP | FP | FN |
|---|---|---|---|---|---|---|---|---|
| Aus guter Familie | 438 | 76.5% | 0.858 | 0.635 | 0.730 | 139 | 23 | 80 |
| Effi Briest | 454 | 80.6% | 0.921 | 0.670 | 0.775 | 152 | 13 | 75 |
| **Macro Avg** | **892** | | **0.890** | **0.652** | **0.753** | | | |

### Multi-tolerance results (macro-averaged)

| Tolerance | P | R | F1 |
|---|---|---|---|
| tol=0 | 0.890 | 0.652 | 0.753 |
| tol=1 | 0.901 | 0.659 | 0.761 |
| tol=3 | 0.933 | 0.688 | 0.792 |

### Pilot vs. full comparison

| | Pilot (n=60, max_per_class=15) | Full (n=892, max_per_class=0) |
|---|---|---|
| F1 (tol=0) | 0.753 | 0.753 |
| Precision | 0.873 | 0.890 |
| Recall | 0.667 | 0.652 |

Macro F1 at tol=0 is identical, validating the pilot as a reliable estimator.

## Interpretation

- **Effi Briest outperforms Aus guter Familie**: F1=0.775 vs 0.730. Effi Briest has higher precision (0.921 vs 0.858) suggesting its scene transitions are more structurally marked.
- **Recall is the bottleneck**: the model misses ~35% of borders. Most misses are subtle narrative transitions without explicit time/location/character markers.
- **Tolerance helps moderately**: F1 improves from 0.753 (tol=0) to 0.792 (tol=3), meaning some predictions are close but not exact.
- **36 total false positives** across 892 sentences (4.0% FP rate) — the model is fairly precise.

## Next step

Compare these results with the fine-tuned BERT baseline to assess the gap between zero-shot prompting and supervised approaches.
