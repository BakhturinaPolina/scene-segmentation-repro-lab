---
note_type: run
run_id: run_20260515_txt_3lang_prompting_baseline_nemotron_live
title: "TXT prompting baseline smoke across DE/EN/RU (Nemotron free)"
date: 2026-05-15
track: prompting
run_type: smoke
status: success
goal: "Run authenticated TXT baseline smoke for German, English, and Russian files into separate output folders."
entrypoint: "src/run_prompting_baseline.py"
command: ".venv-gpu/bin/python src/run_prompting_baseline.py --input_mode txt --txt_file 'data/raw/Das Erdbeben in Chili.txt' --model nvidia/nemotron-3-super-120b-a12b:free --max_sentences 3 --reasoning low --output_dir outputs/prompting/2026-05-15/baseline_txt_nemotron_smoke_de && .venv-gpu/bin/python src/run_prompting_baseline.py --input_mode txt --txt_file 'data/raw/Kleist-Earthquake-in-Chile.txt' --model nvidia/nemotron-3-super-120b-a12b:free --max_sentences 3 --reasoning low --output_dir outputs/prompting/2026-05-15/baseline_txt_nemotron_smoke_en && .venv-gpu/bin/python src/run_prompting_baseline.py --input_mode txt --txt_file 'data/raw/фон Клейст - Землетрясение в Чили.txt' --model nvidia/nemotron-3-super-120b-a12b:free --max_sentences 3 --reasoning low --output_dir outputs/prompting/2026-05-15/baseline_txt_nemotron_smoke_ru"
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
  - "data/raw/Das Erdbeben in Chili.txt"
  - "data/raw/Kleist-Earthquake-in-Chile.txt"
  - "data/raw/фон Клейст - Землетрясение в Чили.txt"
label_schema: "none (inference-only)"
prompt_version: "no-cot baseline"
model_name: "nvidia/nemotron-3-super-120b-a12b:free"
varying_factor: "language/file"
fixed_conditions:
  - "input_mode=txt"
  - "max_sentences=3 per file"
  - "reasoning=low"
  - "temperature=0.0"
  - "top_p=1.0"
random_seed: 1337
output_dir: "outputs/prompting/2026-05-15/"
artifacts_expected:
  - "baseline_txt_nemotron_smoke_de/{command.txt,config.json,results.json,summary.json}"
  - "baseline_txt_nemotron_smoke_en/{command.txt,config.json,results.json,summary.json}"
  - "baseline_txt_nemotron_smoke_ru/{command.txt,config.json,results.json,summary.json}"
artifacts_produced:
  - "outputs/prompting/2026-05-15/baseline_txt_nemotron_smoke_de/summary.json"
  - "outputs/prompting/2026-05-15/baseline_txt_nemotron_smoke_en/summary.json"
  - "outputs/prompting/2026-05-15/baseline_txt_nemotron_smoke_ru/summary.json"
main_metric_name: "parse_failure_rate"
main_metric_value: 0.0
precision: ""
recall: ""
f1: ""
iou: ""
runtime: "136.3s total"
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

Re-run TXT inference-only smoke classification for three language versions of the same story and store outputs in three separate prompting folders.

## What was held constant

- Same model (`nvidia/nemotron-3-super-120b-a12b:free`).
- Same decode configuration and prompt mode.
- Same sample size (`max_sentences=3`) per file.

## What changed

Only the input TXT file/language changed:
- German (`Das Erdbeben in Chili.txt`)
- English (`Kleist-Earthquake-in-Chile.txt`)
- Russian (`фон Клейст - Землетрясение в Чили.txt`)

## Outcome

All three runs completed successfully with real API responses and zero parse failures:
- DE: `parse_failure_rate=0.0`, `avg_latency_seconds=12.706`, `elapsed_seconds=38.1`
- EN: `parse_failure_rate=0.0`, `avg_latency_seconds=8.047`, `elapsed_seconds=24.1`
- RU: `parse_failure_rate=0.0`, `avg_latency_seconds=24.697`, `elapsed_seconds=74.1`

## Interpretation

The TXT baseline path is stable across all three language files with the same model/config. Runtime cost differs by input language/content length, but parsing robustness remained stable.

## Next step

Scale to 20-sentence baseline on each language file or proceed to prompt-family experiments with this same three-folder output convention.
