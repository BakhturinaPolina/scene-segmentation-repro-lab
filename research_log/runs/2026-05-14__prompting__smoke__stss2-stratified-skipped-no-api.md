---
note_type: run
run_id: run_20260514_stss2_prompting_stratified_skipped_no_api
title: "STSS-Test-2 prompting stratified smoke skipped (missing API key)"
date: 2026-05-14
track: prompting
run_type: smoke
status: failed
goal: "Execute STSS-Test-2 stratified smoke command with Nemotron free default."
entrypoint: "src/run_prompting_stratified.py"
command: "OPENROUTER_API_KEY=*** python3 src/run_prompting_stratified.py --model nvidia/nemotron-3-super-120b-a12b:free --dry_run 3 --max_per_class 2 --reasoning low"
working_directory: "."
git_commit: "unknown"
environment: "shell-python3"
os: "Linux"
hardware: "CPU"
gpu: ""
cuda_notes: ""
api_provider: "openrouter"
api_model: "nvidia/nemotron-3-super-120b-a12b:free"
api_cost_estimate: ""
dataset_assets:
  - "upstream/scene-segmentation/data/full/stss_test_2/Aus guter Familie.xmi.zip"
  - "upstream/scene-segmentation/data/full/stss_test_2/Effi Briest.xmi.zip"
label_schema: "binary boundary"
prompt_version: "no-cot baseline"
model_name: "nvidia/nemotron-3-super-120b-a12b:free"
varying_factor: "none"
fixed_conditions:
  - "dry_run=3"
  - "max_per_class=2"
  - "reasoning=low"
random_seed: 1337
output_dir: "outputs/prompting/2026-05-14/strat_nvidia_nemotron-3-super-120b-a12b_free_nocot_reasoning-low/"
artifacts_expected:
  - "command.txt"
  - "config.json"
  - "cache_*.json"
  - "results_*.json"
  - "summary.json"
artifacts_produced: []
main_metric_name: ""
main_metric_value: ""
precision: ""
recall: ""
f1: ""
iou: ""
runtime: "not executed"
failure_category: "api/auth issues"
related_experiment: ""
related_issue: "issue_openrouter_free_model_deprecated"
decision_relevance: false
notion_targets:
  roadmap: "STSS-Test-2 reproducibility"
  runs: true
  experiments: ""
  artifacts: false
  issues: true
  decisions: false
---

## Objective

Run the stratified prompting smoke command against both STSS-Test-2 novels with the pinned Nemotron free model.

## What was held constant

- Stratified smoke settings (`dry_run=3`, `max_per_class=2`, `reasoning=low`).
- Dataset scope: STSS-Test-2 only.

## What changed

Default model route updated from deprecated Qwen free slug to Nemotron free slug.

## Outcome

Run was skipped because `OPENROUTER_API_KEY` is missing in the active shell.

## Interpretation

The reproducibility command is defined and documented, but API authentication is a hard prerequisite for live execution.

## Next step

Configure `OPENROUTER_API_KEY` and rerun to produce cache/results/summary artifacts.
