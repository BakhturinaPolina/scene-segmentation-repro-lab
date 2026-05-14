---
note_type: run
run_id: run_20260514_phase4_prompting_stratified_live
title: "Phase 4 live smoke - stratified prompting runner"
date: 2026-05-14
track: prompting
run_type: smoke
status: success
goal: "Validate end-to-end live stratified prompting run with reproducibility artifacts."
entrypoint: "src/run_prompting_stratified.py"
command: "OPENROUTER_API_KEY=*** python src/run_prompting_stratified.py --model qwen/qwen3.6-plus --dry_run 3 --max_per_class 2 --reasoning low"
working_directory: "."
git_commit: "dc1c3fb"
environment: ".venv"
os: "Linux"
hardware: "CPU"
gpu: ""
cuda_notes: ""
api_provider: "openrouter"
api_model: "qwen/qwen3.6-plus"
api_cost_estimate: ""
dataset_assets:
  - "upstream/scene-segmentation/data/full/stss_test_2/Aus guter Familie.xmi.zip"
  - "upstream/scene-segmentation/data/full/stss_test_2/Effi Briest.xmi.zip"
label_schema: "binary boundary"
prompt_version: "legacy no-cot baseline"
model_name: "qwen/qwen3.6-plus"
varying_factor: "model slug fix (non-free)"
fixed_conditions:
  - "max_per_class=2"
  - "dry_run=3"
  - "reasoning=low"
  - "temperature=0.0"
random_seed: 1337
output_dir: "outputs/prompting/2026-05-14/strat_qwen_qwen3.6-plus_nocot_reasoning-low/"
artifacts_expected:
  - "command.txt"
  - "config.json"
  - "cache_*.json"
  - "results_*.json"
  - "summary.json"
artifacts_produced:
  - "outputs/prompting/2026-05-14/strat_qwen_qwen3.6-plus_nocot_reasoning-low/command.txt"
  - "outputs/prompting/2026-05-14/strat_qwen_qwen3.6-plus_nocot_reasoning-low/config.json"
  - "outputs/prompting/2026-05-14/strat_qwen_qwen3.6-plus_nocot_reasoning-low/cache_Aus_guter_Familie.json"
  - "outputs/prompting/2026-05-14/strat_qwen_qwen3.6-plus_nocot_reasoning-low/cache_Effi_Briest.json"
  - "outputs/prompting/2026-05-14/strat_qwen_qwen3.6-plus_nocot_reasoning-low/results_Aus_guter_Familie.json"
  - "outputs/prompting/2026-05-14/strat_qwen_qwen3.6-plus_nocot_reasoning-low/results_Effi_Briest.json"
  - "outputs/prompting/2026-05-14/strat_qwen_qwen3.6-plus_nocot_reasoning-low/summary.json"
main_metric_name: "macro_avg_tol_0_f1"
main_metric_value: 1.0
precision: 1.0
recall: 1.0
f1: 1.0
iou: ""
runtime: "about 357s"
failure_category: ""
related_experiment: ""
related_issue: "issue_openrouter_free_model_deprecated"
decision_relevance: false
notion_targets:
  roadmap: "Phase 4 stabilization"
  runs: true
  experiments: ""
  artifacts: true
  issues: true
  decisions: false
---

## Objective

Run a live stratified smoke test using a valid OpenRouter model while validating automatic command/config artifact persistence.

## What was held constant

- Prompt mode (`no-cot`)
- Reasoning (`low`)
- Decode defaults
- Stratified sampling logic and seed

## What changed

Model slug overridden to `qwen/qwen3.6-plus` to bypass provider deprecation of the free alias.

## Outcome

Run succeeded across both novels with complete output bundle and zero parse failures on the sampled sentences.

## Interpretation

Phase 4 stabilization changes (path/config handling + artifact persistence) work under live API execution.

## Next step

Update default baseline model slug in code and rerun baseline smoke so both baseline and stratified commands pass without overrides.
