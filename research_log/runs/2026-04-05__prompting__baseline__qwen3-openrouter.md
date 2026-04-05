---
note_type: run
run_id: run_20260405_prompting_baseline_qwen3
title: "Prompting baseline: qwen3.6-plus via OpenRouter on 20 sentences"
date: 2026-04-05
track: prompting
run_type: baseline
status: success
goal: "Validate the prompting pipeline with OpenRouter API and qwen/qwen3.6-plus:free"
entrypoint: "python src/run_prompting_baseline.py"
command: >
  OPENROUTER_API_KEY=... python src/run_prompting_baseline.py
working_directory: "."
git_commit: "8649e50"
environment: ".venv (CPU)"
os: "Linux 6.17.0-111019-tuxedo"
hardware: "CPU only"
gpu: ""
cuda_notes: ""
api_provider: "OpenRouter"
api_model: "qwen/qwen3.6-plus:free"
api_cost_estimate: "$0.00 (free tier)"
dataset_assets:
  - "data/full/stss_test_2/Aus guter Familie.xmi.zip"
label_schema: "Coarse (BORDER / NOBORDER)"
prompt_version: "prompt_classify (upstream default)"
model_name: "qwen/qwen3.6-plus:free"
varying_factor: "none"
fixed_conditions:
  - "context_size=409 tokens (512 * 0.8)"
  - "First 20 sentences of document"
  - "no_cot prompt"
random_seed: ""
output_dir: "outputs/prompting/2026-04-05/baseline_qwen3"
artifacts_expected:
  - "results.json"
  - "summary.json"
artifacts_produced:
  - "results.json (20 classified sentences with reasons)"
  - "summary.json"
main_metric_name: "accuracy"
main_metric_value: "1.0"
precision: ""
recall: ""
f1: ""
iou: ""
runtime: "449s (rate-limited, ~22s/sentence average)"
failure_category: ""
related_experiment: ""
related_issue: "issue_openrouter_rate_limits"
decision_relevance: false
notion_targets:
  roadmap: "Phase 3.2"
  runs: true
  experiments: ""
  artifacts: true
  issues: true
  decisions: false
---

## Objective

Validate that the prompting-based classification pipeline works with the OpenRouter API and the `qwen/qwen3.6-plus:free` model. Classify a small sample to confirm API connectivity, prompt parsing, and response handling.

## What was held constant

- Default scene classification prompt from upstream
- Context window ~409 tokens
- LangChain chain with conversation memory (cleared after each response)

## What changed

- Added `ChatOpenRouter` integration with `OPENROUTER_API_KEY` env var
- Added `qwen3_plus` model definition in classify.py
- Created `src/run_prompting_baseline.py` wrapper with rate-limit retry logic
- Simplified label extraction (avoiding Unsloth import in CPU env)

## Outcome

- 20/20 sentences classified correctly (100% accuracy)
- 1 true border correctly predicted as BORDER
- 19 true non-borders correctly predicted as NOBORDER
- Several rate-limit retries (free tier), total runtime 449s

## Interpretation

The small sample size (20 sentences, only 1 border) makes the 100% accuracy statistically weak. The key result is that the pipeline works: API connection, prompt formatting, response parsing, and label extraction all function correctly.

Rate limiting on the free tier makes large-scale runs slow (~22s/sentence). A paid tier or local model would be needed for full evaluations.

## Next step

Run on a larger sample or full document. Consider rate-limit mitigation (paid tier, batching, or switching to Ollama for local inference).
