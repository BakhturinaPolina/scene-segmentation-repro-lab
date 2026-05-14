---
note_type: run
run_id: run_20260514_stss2_prompting_phase_a_skipped_no_api
title: "STSS-Test-2 Phase A family A smoke skipped (missing API key)"
date: 2026-05-14
track: prompting
run_type: smoke
status: failed
goal: "Execute Phase A family A smoke command with Nemotron free default."
entrypoint: "src/run_prompting_phase_a.py"
command: "OPENROUTER_API_KEY=*** python3 src/run_prompting_phase_a.py --families A --model nvidia/nemotron-3-super-120b-a12b:free --dry_run 1 --max_per_class 1 --reasoning low"
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
prompt_version: "Phase A family A"
model_name: "nvidia/nemotron-3-super-120b-a12b:free"
varying_factor: "prompt_family=A"
fixed_conditions:
  - "dry_run=1"
  - "max_per_class=1"
  - "reasoning=low"
random_seed: 1337
output_dir: "outputs/prompting/2026-05-14/"
artifacts_expected:
  - "command.txt"
  - "config.json"
  - "phase_a_manifest.json"
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

Run a Phase A family A orchestrator smoke command under the pinned Nemotron free baseline.

## What was held constant

- Family scope (`A`), dry-run size, class cap, and reasoning level.
- STSS-Test-2-only data scope.

## What changed

The default free-model route is now Nemotron free instead of deprecated Qwen free.

## Outcome

Run was skipped because no OpenRouter API key is available in the current shell environment.

## Interpretation

Phase A smoke cannot proceed without credentials. The blocker is environmental rather than script-level.

## Next step

Set `OPENROUTER_API_KEY` and rerun this exact command to generate the Phase A manifest and nested results.
