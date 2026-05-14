---
note_type: run
run_id: run_20260514_phase4_phase_a_family_a_live
title: "Phase 4 live smoke - Phase A family A orchestrator"
date: 2026-05-14
track: prompting
run_type: smoke
status: success
goal: "Validate Phase A orchestrator execution and manifest creation with live API calls."
entrypoint: "src/run_prompting_phase_a.py"
command: "OPENROUTER_API_KEY=*** python src/run_prompting_phase_a.py --families A --model qwen/qwen3.6-plus --dry_run 1 --max_per_class 1 --reasoning low"
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
prompt_version: "Phase A family A template"
model_name: "qwen/qwen3.6-plus"
varying_factor: "prompt_family=A"
fixed_conditions:
  - "dry_run=1"
  - "max_per_class=1"
  - "reasoning=low"
  - "temperature=0.0"
random_seed: 1337
output_dir: "outputs/prompting/2026-05-14/"
artifacts_expected:
  - "command.txt"
  - "config.json"
  - "phase_a_manifest.json"
artifacts_produced:
  - "outputs/prompting/2026-05-14/command.txt"
  - "outputs/prompting/2026-05-14/config.json"
  - "outputs/prompting/2026-05-14/phase_a_manifest.json"
  - "outputs/prompting/2026-05-14/strat_qwen_qwen3.6-plus_familyA_reasoning-low/summary.json"
main_metric_name: "phase_a_exit_code"
main_metric_value: 0
precision: ""
recall: ""
f1: 0.0
iou: ""
runtime: "about 236s"
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

Confirm the Phase A orchestrator can launch and complete an end-to-end family sweep job (single-family smoke case).

## What was held constant

- Model: `qwen/qwen3.6-plus`
- Reasoning: `low`
- Decode defaults
- `dry_run=1` and `max_per_class=1`

## What changed

Prompt family set to `A` via orchestrator flow.

## Outcome

Run succeeded (`exit_code=0`) and produced the expected `phase_a_manifest.json` plus nested stratified outputs.

## Interpretation

Phase A orchestration and artifact persistence are operational under live API execution.

## Next step

Run a broader smoke (`families A,B`) and then a standard Phase A sweep when budget/time allows.
