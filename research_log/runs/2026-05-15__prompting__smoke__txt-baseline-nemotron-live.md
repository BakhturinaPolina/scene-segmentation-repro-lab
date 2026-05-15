---
note_type: run
run_id: run_20260515_txt_prompting_baseline_nemotron_live
title: "TXT prompting baseline smoke (Nemotron free) live success"
date: 2026-05-15
track: prompting
run_type: smoke
status: success
goal: "Validate authenticated TXT-mode prompting baseline execution on OpenRouter free Nemotron."
entrypoint: "src/run_prompting_baseline.py"
command: "OPENROUTER_API_KEY=*** .venv-gpu/bin/python src/run_prompting_baseline.py --input_mode txt --txt_file 'data/raw/фон Клейст - Землетрясение в Чили.txt' --model nvidia/nemotron-3-super-120b-a12b:free --max_sentences 3 --reasoning low --output_dir outputs/prompting/2026-05-15/baseline_txt_nemotron_smoke_live"
working_directory: "."
git_commit: "3b0b863"
environment: ".venv-gpu"
os: "Linux"
hardware: "CPU"
gpu: ""
cuda_notes: ""
api_provider: "openrouter"
api_model: "nvidia/nemotron-3-super-120b-a12b:free"
api_cost_estimate: ""
dataset_assets:
  - "data/raw/фон Клейст - Землетрясение в Чили.txt"
  - "data/manifest_raw_txt.json"
label_schema: "none (inference-only)"
prompt_version: "no-cot baseline"
model_name: "nvidia/nemotron-3-super-120b-a12b:free"
varying_factor: "none"
fixed_conditions:
  - "input_mode=txt"
  - "max_sentences=3"
  - "reasoning=low"
  - "temperature=0.0"
  - "top_p=1.0"
random_seed: 1337
output_dir: "outputs/prompting/2026-05-15/baseline_txt_nemotron_smoke_live"
artifacts_expected:
  - "command.txt"
  - "config.json"
  - "results.json"
  - "summary.json"
artifacts_produced:
  - "outputs/prompting/2026-05-15/baseline_txt_nemotron_smoke_live/command.txt"
  - "outputs/prompting/2026-05-15/baseline_txt_nemotron_smoke_live/config.json"
  - "outputs/prompting/2026-05-15/baseline_txt_nemotron_smoke_live/results.json"
  - "outputs/prompting/2026-05-15/baseline_txt_nemotron_smoke_live/summary.json"
main_metric_name: "parse_failure_rate"
main_metric_value: 0.0
precision: ""
recall: ""
f1: ""
iou: ""
runtime: "26.3s"
failure_category: ""
related_experiment: ""
related_issue: ""
decision_relevance: false
notion_targets:
  roadmap: ""
  runs: true
  experiments: ""
  artifacts: true
  issues: false
  decisions: false
---

## Objective

Confirm that the new TXT inference-only baseline path performs authenticated live inference on OpenRouter with Nemotron free.

## What was held constant

- Model target `nvidia/nemotron-3-super-120b-a12b:free`.
- Prompting mode `no-cot` and decode configuration (`temperature=0.0`, `top_p=1.0`, `max_tokens=256`).
- TXT source file and sample size (`max_sentences=3`).

## What changed

Compared with the earlier auth-failure smoke run, this execution used a valid OpenRouter API key in the active shell environment.

## Outcome

Run succeeded with live model responses for all 3 sentences. `summary.json` reports `parse_failure_rate=0.0`, average output length `1025.33` characters, average latency `8.777s`, and total elapsed time `26.3s`.

## Interpretation

TXT-mode baseline implementation is operational end-to-end with OpenRouter authentication. Validation criterion for successful API calls and stable parsing is satisfied.

## Next step

Proceed to prompt-family experiments on top of this validated TXT baseline path, or increase smoke sample size to 10-20 sentences for additional runtime confidence.
