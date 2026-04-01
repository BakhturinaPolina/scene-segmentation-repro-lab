---
note_type: run
run_id: run_20260331_strict_upstream_install
title: "Smoke re-test after strict install from upstream requirements.txt"
date: 2026-03-31
track: cross-project
run_type: smoke
status: failed
goal: "Re-run the same 6 commands after installing upstream's own requirements.txt"
entrypoint: "python -c 'import ...'"
command: |
  pip install -r upstream/scene-segmentation/requirements.txt
  python -c "import ssc.model; print('OK ssc.model')"
  python -c "import ssc.dataset; print('OK ssc.dataset')"
  python -c "import prompting.classify; print('OK prompting.classify')"
  python -m ssc.main --help
  python -m ssc.train --help
  python prompting/classify.py
working_directory: "upstream/scene-segmentation"
git_commit: "42c0a92"
environment: "scene-seg-basic (.venv, full upstream requirements)"
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
  - "same .venv"
  - "same upstream code"
  - "transformers==5.4.0 unchanged by upstream reqs"
  - "langchain==1.2.13 unchanged by upstream reqs"
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
related_issue: "issue_torchvision_nms_mismatch, issue_langchain_adapters_missing"
decision_relevance: true
notion_targets:
  roadmap: ""
  runs: true
  experiments: ""
  artifacts: false
  issues: true
  decisions: true
---

## Objective

Test whether using the upstream repository's own `requirements.txt` resolves compatibility issues.

## What was held constant

- Same interpreter, working directory, upstream code
- Same 6 smoke test commands

## What changed

- Installed full upstream `requirements.txt` (~312s install)
- Added unsloth==2025.7.2, trl==1.0.0, bitsandbytes==0.49.2, xformers==0.0.35, cvxpy, pygamma-agreement
- transformers and langchain versions remained unchanged (upstream reqs did not pin them)

## Outcome

All 6 commands still failed.

| Command | Error | Category |
|---------|-------|----------|
| `import ssc.model` | `RuntimeError: operator torchvision::nms does not exist` then `Could not import module 'PreTrainedModel'` | binary compat |
| `import ssc.dataset` | same torchvision::nms chain | binary compat |
| `import prompting.classify` | `ModuleNotFoundError: No module named 'langchain.adapters'` | API layout |
| `python -m ssc.main --help` | same torchvision::nms | binary compat |
| `python -m ssc.train --help` | same torchvision::nms | binary compat |
| `python prompting/classify.py` | same langchain.adapters | API layout |

## Interpretation

The upstream `requirements.txt` does not pin `transformers`, `langchain`, `torch`, or `torchvision` tightly enough for the current Python 3.12 / pip resolver environment. The strict install introduced a new torch/torchvision binary mismatch (`nms` operator missing) while the langchain issue persisted.

Conclusion: upstream requirements are insufficient; manual version pinning is needed.

## Next step

Create `requirements-basic.txt` with explicit CPU-compatible pins for torch, torchvision, transformers, and langchain.
