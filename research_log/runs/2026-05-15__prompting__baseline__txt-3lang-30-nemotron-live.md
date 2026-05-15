---
note_type: run
run_id: run_20260515_txt_3lang_30_prompting_baseline_nemotron_live
title: "TXT prompting baseline 30-sentence run across DE/EN/RU"
date: 2026-05-15
track: prompting
run_type: baseline
status: success
goal: "Produce stronger deterministic baseline evidence by classifying first 30 sentences per language file with manual-review outputs."
entrypoint: "src/run_prompting_baseline.py"
command: ".venv-gpu/bin/python src/run_prompting_baseline.py --input_mode txt --txt_file 'data/raw/Das Erdbeben in Chili.txt' --model nvidia/nemotron-3-super-120b-a12b:free --max_sentences 30 --reasoning low --output_dir outputs/prompting/2026-05-15/baseline_txt_nemotron_30_de && .venv-gpu/bin/python src/run_prompting_baseline.py --input_mode txt --txt_file 'data/raw/Kleist-Earthquake-in-Chile.txt' --model nvidia/nemotron-3-super-120b-a12b:free --max_sentences 30 --reasoning low --output_dir outputs/prompting/2026-05-15/baseline_txt_nemotron_30_en && .venv-gpu/bin/python src/run_prompting_baseline.py --input_mode txt --txt_file 'data/raw/фон Клейст - Землетрясение в Чили.txt' --model nvidia/nemotron-3-super-120b-a12b:free --max_sentences 30 --reasoning low --output_dir outputs/prompting/2026-05-15/baseline_txt_nemotron_30_ru"
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
  - "first 30 sentences per file"
  - "input_mode=txt"
  - "reasoning=low"
  - "temperature=0.0"
  - "top_p=1.0"
  - "max_tokens=256"
random_seed: 1337
output_dir: "outputs/prompting/2026-05-15/"
artifacts_expected:
  - "baseline_txt_nemotron_30_de/{command.txt,config.json,results.json,summary.json,review.jsonl,review_schema.json}"
  - "baseline_txt_nemotron_30_en/{command.txt,config.json,results.json,summary.json,review.jsonl,review_schema.json}"
  - "baseline_txt_nemotron_30_ru/{command.txt,config.json,results.json,summary.json,review.jsonl,review_schema.json}"
artifacts_produced:
  - "outputs/prompting/2026-05-15/baseline_txt_nemotron_30_de/review.jsonl"
  - "outputs/prompting/2026-05-15/baseline_txt_nemotron_30_en/review.jsonl"
  - "outputs/prompting/2026-05-15/baseline_txt_nemotron_30_ru/review.jsonl"
main_metric_name: "parse_failure_rate"
main_metric_value: 0.0
precision: ""
recall: ""
f1: ""
iou: ""
runtime: "1158.2s total"
failure_category: ""
related_experiment: "experiment_prompting_model_free_120b_comparison"
related_issue: ""
decision_relevance: false
notion_targets:
  roadmap: ""
  runs: true
  experiments: true
  artifacts: true
  issues: false
  decisions: false
---

## Objective

Run a stronger deterministic multilingual baseline: first 30 sentences from each DE/EN/RU TXT file, with full-sentence reviewer outputs.

## What was held constant

- Model and provider: OpenRouter `nvidia/nemotron-3-super-120b-a12b:free`.
- Prompting setup: `no-cot`, `reasoning=low`.
- Decode config: `temperature=0.0`, `top_p=1.0`, `max_tokens=256`.
- Selection policy: first 30 sentences (non-random) per file.

## What changed

Language/file changed across three runs while keeping all other conditions fixed.

## Outcome

All three baseline runs succeeded and produced full review artifacts:

- DE (`baseline_txt_nemotron_30_de`): 30/30 classified, predicted borders=23, parse failures=0, avg latency=11.831s.
- EN (`baseline_txt_nemotron_30_en`): 30/30 classified, predicted borders=23, parse failures=0, avg latency=12.88s.
- RU (`baseline_txt_nemotron_30_ru`): 30/30 classified, predicted borders=27, parse failures=0, avg latency=13.896s.

Each output folder contains `review.jsonl` with full sentence text and both compact/raw model reasoning.

## Interpretation

The stronger 30-sentence baseline confirms stable inference behavior across all three language files and provides reviewer-ready artifacts for manual semantic evaluation.

## Next step

Reuse the same `review.jsonl` schema in prompt-family experiments so baseline vs prompt-family comparisons can be reviewed sentence-by-sentence with identical fields.
