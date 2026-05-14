---
note_type: run
run_id: run_20260514_stss2_prompting_baseline_skipped_no_api
title: "STSS-Test-2 prompting baseline smoke skipped (missing API key)"
date: 2026-05-14
track: prompting
run_type: smoke
status: failed
goal: "Execute STSS-Test-2 baseline smoke command with Nemotron free default."
entrypoint: "src/run_prompting_baseline.py"
command: "OPENROUTER_API_KEY=*** python3 src/run_prompting_baseline.py --model nvidia/nemotron-3-super-120b-a12b:free --max_sentences 5 --reasoning low"
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
label_schema: "binary boundary"
prompt_version: "no-cot baseline"
model_name: "nvidia/nemotron-3-super-120b-a12b:free"
varying_factor: "none"
fixed_conditions:
  - "max_sentences=5"
  - "reasoning=low"
random_seed: 1337
output_dir: "outputs/prompting/2026-05-14/baseline_qwen3/"
artifacts_expected:
  - "command.txt"
  - "config.json"
  - "results.json"
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

Run the baseline prompting smoke command under the new default free model for STSS-Test-2-only reproducibility.

## What was held constant

- Baseline command parameters (`max_sentences=5`, `reasoning=low`).
- STSS-Test-2 input document and baseline output structure.

## What changed

Model slug changed from deprecated Qwen free route to Nemotron free route.

## Outcome

Run was skipped because `OPENROUTER_API_KEY` is not configured in the active shell environment.

## Interpretation

The command is ready, but live API execution cannot proceed without credentials. This is an environment blocker, not a code blocker.

## Next step

Set `OPENROUTER_API_KEY` and rerun the exact command to generate live smoke artifacts.
