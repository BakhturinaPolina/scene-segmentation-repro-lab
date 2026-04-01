---
note_type: run
run_id: run_20260331_initial_import_tests
title: "Phase 3 initial import and startup smoke tests"
date: 2026-03-31
track: cross-project
run_type: smoke
status: failed
goal: "Verify whether ssc, prompting, and llama modules can be imported and scripts can start"
entrypoint: "python -c 'import ...'"
command: |
  python -c "import ssc.model; print('OK ssc.model')"
  python -c "import ssc.dataset; print('OK ssc.dataset')"
  python -c "import prompting.classify; print('OK prompting.classify')"
  python -m ssc.main --help
  python -m ssc.train --help
  python prompting/classify.py
working_directory: "upstream/scene-segmentation"
git_commit: "42c0a92"
environment: "scene-seg-basic (.venv, no pinned deps yet)"
os: "Linux"
hardware: "CPU only"
gpu: ""
cuda_notes: ""
api_provider: ""
api_model: ""
api_cost_estimate: ""
dataset_assets: []
label_schema: ""
prompt_version: ""
model_name: ""
varying_factor: "none"
fixed_conditions:
  - "fresh .venv with minimal deps"
  - "no upstream requirements.txt installed yet"
random_seed: ""
output_dir: ""
artifacts_expected: []
artifacts_produced: []
main_metric_name: ""
main_metric_value: ""
precision: ""
recall: ""
f1: ""
iou: ""
runtime: ""
failure_category: "dependency"
related_experiment: ""
related_issue: "issue_transformers_dataclass_compat, issue_langchain_adapters_missing"
decision_relevance: false
notion_targets:
  roadmap: ""
  runs: true
  experiments: ""
  artifacts: false
  issues: true
  decisions: false
---

## Objective

Determine which parts of the upstream codebase can import and start on the local machine before any compatibility work.

## What was held constant

- Interpreter: `.venv/bin/python` (Python 3.12.3)
- Working directory: `upstream/scene-segmentation` (clone root)
- No code modifications to upstream

## What changed

Nothing — this was the first execution attempt.

## Outcome

All 6 commands failed at import time.

| Command | Error | Category |
|---------|-------|----------|
| `import ssc.model` | `ModuleNotFoundError: No module named 'peft'` | missing dep |
| `import ssc.dataset` | `ModuleNotFoundError: No module named 'wuenlp'` | missing dep |
| `import prompting.classify` | `ModuleNotFoundError: No module named 'langchain'` | missing dep |
| `python -m ssc.main --help` | same as ssc.model | missing dep |
| `python -m ssc.train --help` | same as ssc.dataset | missing dep |
| `python prompting/classify.py` | same as prompting.classify | missing dep |

Additionally confirmed: running from wrapper root instead of clone root causes `ModuleNotFoundError: No module named 'ssc'`.

## Interpretation

The minimal `.venv` was missing `peft`, `wuenlp`, and `langchain`. These are import-time hard dependencies. No script logic was reached. The errors are fully explained by missing packages.

## Next step

Install missing packages (`peft`, `langchain`, `wuenlp`) and re-run the same 6 commands.
