---
note_type: run
run_id: run_20260514_phase4_runtime_tests
title: "Phase 4 runtime helper unit tests"
date: 2026-05-14
track: cross-project
run_type: smoke
status: success
goal: "Validate Phase 4 path/config reproducibility helpers with offline tests."
entrypoint: "tests/test_workflow_runtime.py"
command: "python3 -m unittest discover -s tests -v"
working_directory: "."
git_commit: "dc1c3fb"
environment: "system-python3"
os: "Linux"
hardware: "CPU"
gpu: ""
cuda_notes: ""
api_provider: ""
api_model: ""
api_cost_estimate: ""
dataset_assets:
  - "none"
label_schema: ""
prompt_version: ""
model_name: ""
varying_factor: "none"
fixed_conditions:
  - "No network/API dependencies"
  - "Single local repository checkout"
  - "Standard unittest runner"
random_seed: ""
output_dir: "n/a"
artifacts_expected:
  - "test stdout"
artifacts_produced:
  - "all 5 tests passed in terminal output"
main_metric_name: "tests_passed"
main_metric_value: 5
precision: ""
recall: ""
f1: ""
iou: ""
runtime: "0.009s (test runtime)"
failure_category: ""
related_experiment: ""
related_issue: ""
decision_relevance: false
notion_targets:
  roadmap: "Phase 4 stabilization"
  runs: true
  experiments: ""
  artifacts: true
  issues: false
  decisions: false
---

## Objective

Confirm that shared runtime helpers introduced for Phase 4 produce deterministic paths and reproducibility files (`command.txt`, `config.json`).

## What was held constant

- Same repository state and working directory.
- Local Python runtime only (no virtualenv requirement).
- Single test suite: `tests/test_workflow_runtime.py`.

## What changed

- Added `src/workflow_runtime.py`.
- Added/ran unit tests in `tests/test_workflow_runtime.py`.
- Updated prompting runners to use helper functions.

## Outcome

All 5 unit tests passed:

- project root resolution
- STSS-Test-2 data path resolution
- output directory builder
- reproducibility file writer
- command quoting behavior

## Interpretation

The Phase 4 runtime helper layer works for offline reproducibility guarantees and can be used as the base for script-level smoke runs.

## Next step

Run prompting smoke commands from `docs/PHASE4_STABILIZATION.md` with API key and log run/artifact notes for those executions.
