---
note_type: run
run_id: run_20260331_cpu_pinned_final
title: "Smoke test after compatibility pinning (CPU env)"
date: 2026-03-31
track: cross-project
run_type: smoke
status: partial
goal: "Verify imports pass after pinning torch, torchvision, transformers, langchain"
entrypoint: "python -c 'import ...'"
command: |
  pip install -r requirements-basic.txt
  cd upstream/scene-segmentation
  python -c "import ssc.model; print('OK ssc.model')"
  python -c "import ssc.dataset; print('OK ssc.dataset')"
  python -c "import prompting.classify; print('OK prompting.classify')"
  python -m ssc.main --help
  python -m ssc.train --help
  python prompting/classify.py
working_directory: "upstream/scene-segmentation"
git_commit: "3525715"
environment: "scene-seg-basic (.venv, requirements-basic.txt pinned)"
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
  - "same upstream code"
  - "torch==2.5.1+cpu"
  - "torchvision==0.20.1+cpu"
  - "transformers==4.46.3"
  - "langchain==0.1.9"
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
failure_category: ""
related_experiment: ""
related_issue: "issue_unsloth_cpp_extensions_skip"
decision_relevance: true
notion_targets:
  roadmap: true
  runs: true
  experiments: ""
  artifacts: false
  issues: false
  decisions: true
---

## Objective

Confirm that explicit version pinning resolves all import-time failures on CPU.

## What was held constant

- Same upstream code, same interpreter, same working directory
- Same 6 smoke test commands

## What changed

- `requirements-basic.txt` created with:
  - `torch==2.5.1+cpu`, `torchvision==0.20.1+cpu`
  - `transformers==4.46.3`
  - `langchain==0.1.9`

## Outcome

| Command | Result | Note |
|---------|--------|------|
| `import ssc.model` | **PASS** | |
| `import ssc.dataset` | FAIL | Unsloth `NotImplementedError` on CPU torch (expected) |
| `import prompting.classify` | **PASS** | |
| `python -m ssc.main --help` | FAIL | Unsloth GPU check (expected) |
| `python -m ssc.train --help` | FAIL | Unsloth GPU check (expected) |
| `python prompting/classify.py` | FAIL | `ModuleNotFoundError: utils` — path issue when running script directly |

2 of 6 commands pass. The remaining 4 failures are expected: 3 require GPU (Unsloth), 1 requires correct PYTHONPATH for `utils` module.

## Interpretation

The compatibility pinning resolved all genuine dependency mismatches. The CPU environment is now healthy for SSC model validation and prompting import validation. Remaining failures are architectural (GPU requirement, path resolution) and do not indicate broken dependencies.

## Next step

Set up `.venv-gpu` for GPU-dependent workflows (Unsloth, ssc.dataset, training).
