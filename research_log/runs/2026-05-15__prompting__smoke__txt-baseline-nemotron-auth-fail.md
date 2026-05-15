---
note_type: run
run_id: run_20260515_txt_prompting_baseline_nemotron_auth_fail
title: "TXT prompting baseline smoke (Nemotron free) with auth failure"
date: 2026-05-15
track: prompting
run_type: smoke
status: failed
goal: "Validate TXT-mode prompting baseline runtime and output artifacts on OpenRouter free Nemotron."
entrypoint: "src/run_prompting_baseline.py"
command: "OPENROUTER_API_KEY=*** .venv-gpu/bin/python src/run_prompting_baseline.py --input_mode txt --txt_file 'data/raw/фон Клейст - Землетрясение в Чили.txt' --model nvidia/nemotron-3-super-120b-a12b:free --max_sentences 3 --reasoning low --output_dir outputs/prompting/2026-05-15/baseline_txt_nemotron_smoke"
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
varying_factor: "input mode (txt inference-only)"
fixed_conditions:
  - "max_sentences=3"
  - "reasoning=low"
  - "temperature=0.0"
  - "top_p=1.0"
random_seed: 1337
output_dir: "outputs/prompting/2026-05-15/baseline_txt_nemotron_smoke"
artifacts_expected:
  - "command.txt"
  - "config.json"
  - "results.json"
  - "summary.json"
artifacts_produced:
  - "outputs/prompting/2026-05-15/baseline_txt_nemotron_smoke/command.txt"
  - "outputs/prompting/2026-05-15/baseline_txt_nemotron_smoke/config.json"
  - "outputs/prompting/2026-05-15/baseline_txt_nemotron_smoke/results.json"
  - "outputs/prompting/2026-05-15/baseline_txt_nemotron_smoke/summary.json"
main_metric_name: "parse_failure_rate"
main_metric_value: 1.0
precision: ""
recall: ""
f1: ""
iou: ""
runtime: "1.3s"
failure_category: "api/auth issues"
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

Run the new TXT input mode in the baseline runner and verify reproducible output artifacts under a free OpenRouter model target.

## What was held constant

- Baseline prompting path (`no-cot`, `reasoning=low`, deterministic decode params).
- Model target `nvidia/nemotron-3-super-120b-a12b:free`.
- Standard output artifact structure (`command.txt`, `config.json`, `results.json`, `summary.json`).

## What changed

- Input mode switched from XMI to TXT with `--input_mode txt`.
- Source text provided via `--txt_file data/raw/фон Клейст - Землетрясение в Чили.txt`.

## Outcome

Run completed and wrote all expected artifacts, but all API calls failed with `401 Missing Authentication header`. The summary reports inference-only output with `parse_failure_rate=1.0` and zero model text output.

## Interpretation

The TXT-mode code path is executable and artifact-writing is stable, but live model validation is blocked by missing OpenRouter authentication in the active shell.

## Next step

Set a valid `OPENROUTER_API_KEY` in the same shell and rerun the exact command to confirm successful live responses and non-error parse statistics.
