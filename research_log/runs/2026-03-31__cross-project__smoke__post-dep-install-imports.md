---
note_type: run
run_id: run_20260331_post_dep_install_imports
title: "Smoke re-test after installing peft, langchain, wuenlp"
date: 2026-03-31
track: cross-project
run_type: smoke
status: failed
goal: "Re-run the same 6 import/startup commands after installing previously missing packages"
entrypoint: "python -c 'import ...'"
command: |
  pip install peft langchain "git+https://wuenlp.professor-x.de"
  python -c "import ssc.model; print('OK ssc.model')"
  python -c "import ssc.dataset; print('OK ssc.dataset')"
  python -c "import prompting.classify; print('OK prompting.classify')"
  python -m ssc.main --help
  python -m ssc.train --help
  python prompting/classify.py
working_directory: "upstream/scene-segmentation"
git_commit: "42c0a92"
environment: "scene-seg-basic (.venv, peft+langchain+wuenlp added)"
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
  - "peft==0.18.1, langchain==1.2.13, WueNLP==0.6.9 now installed"
  - "transformers==5.4.0 (unpinned)"
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

Verify whether installing the three previously missing packages (peft, langchain, wuenlp) unblocks imports.

## What was held constant

- Same interpreter, working directory, upstream code
- No version pinning yet — installed latest available versions

## What changed

- Added `peft==0.18.1`, `langchain==1.2.13`, `WueNLP==0.6.9`
- `transformers==5.4.0` remained (unpinned)

## Outcome

All 6 commands still failed, but at deeper checkpoints.

| Command | Error | Category |
|---------|-------|----------|
| `import ssc.model` | `TypeError: non-default argument 'embedding_model_name' follows default argument` | framework compat |
| `import ssc.dataset` | same TypeError via ssc.model | framework compat |
| `import prompting.classify` | `ModuleNotFoundError: No module named 'langchain.adapters'` | API layout change |
| `python -m ssc.main --help` | same TypeError | framework compat |
| `python -m ssc.train --help` | same TypeError | framework compat |
| `python prompting/classify.py` | same langchain.adapters error | API layout change |

## Interpretation

Missing-package blockers are resolved, but two new blockers emerged:

1. **transformers 5.x** auto-converts `PretrainedConfig` subclasses to dataclasses, breaking upstream `SSCModelConfig` field ordering.
2. **langchain 1.x** removed `langchain.adapters` module that upstream prompting code expects.

Both are version-compatibility issues, not code bugs.

## Next step

Try strict install from upstream `requirements.txt` to see if the authors' pinned versions resolve these.
