---
note_type: run
run_id: run_20260514_phase4_prompting_baseline_live
title: "Phase 4 live smoke - prompting baseline runner"
date: 2026-05-14
track: prompting
run_type: smoke
status: failed
goal: "Validate live API baseline execution with Phase 4 reproducibility artifacts."
entrypoint: "src/run_prompting_baseline.py"
command: "OPENROUTER_API_KEY=*** python src/run_prompting_baseline.py --max_sentences 5 --reasoning low"
working_directory: "."
git_commit: "dc1c3fb"
environment: ".venv"
os: "Linux"
hardware: "CPU"
gpu: ""
cuda_notes: ""
api_provider: "openrouter"
api_model: "qwen/qwen3.6-plus:free"
api_cost_estimate: ""
dataset_assets:
  - "upstream/scene-segmentation/data/full/stss_test_2/Aus guter Familie.xmi.zip"
label_schema: "binary boundary"
prompt_version: "legacy no-cot baseline"
model_name: "qwen/qwen3.6-plus:free"
varying_factor: "none"
fixed_conditions:
  - "max_sentences=5"
  - "reasoning=low"
  - "temperature=0.0"
random_seed: 1337
output_dir: "outputs/prompting/2026-05-14/baseline_qwen3/"
artifacts_expected:
  - "command.txt"
  - "config.json"
  - "results.json"
  - "summary.json"
artifacts_produced:
  - "outputs/prompting/2026-05-14/baseline_qwen3/command.txt"
  - "outputs/prompting/2026-05-14/baseline_qwen3/config.json"
  - "outputs/prompting/2026-05-14/baseline_qwen3/results.json"
  - "outputs/prompting/2026-05-14/baseline_qwen3/summary.json"
main_metric_name: "parse_failure_rate"
main_metric_value: 1.0
precision: ""
recall: ""
f1: ""
iou: ""
runtime: "about 71s wall time"
failure_category: "api/auth issues"
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

Execute a live baseline smoke run and verify that reproducibility files are automatically saved.

## What was held constant

- Prompt mode (`no-cot`)
- Reasoning (`low`)
- Decode defaults
- Input document (`Aus guter Familie`)

## What changed

No intentional factor change; this was a direct smoke validation run.

## Outcome

Run completed with output files, but API calls failed due to repeated 404 errors from provider because the default free model slug is deprecated.

## Interpretation

Phase 4 artifact persistence works (`command.txt`, `config.json`, summary/results). The blocking issue is the stale default model slug, not path/config logic.

## Next step

Run with explicit `--model qwen/qwen3.6-plus` and update baseline default model in code.
