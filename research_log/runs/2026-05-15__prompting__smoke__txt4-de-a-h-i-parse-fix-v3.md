---
note_type: run
run_id: run_20260515_txt4_de_a_h_i_parse_fix_v3
title: "TXT DE 4-sentence A/H/I smoke after parser and chunk-family baseline fixes"
date: 2026-05-15
track: prompting
run_type: smoke
status: success
goal: "Verify that family A parsing and H/I chunk-family handling are stable in baseline TXT mode."
entrypoint: "src/run_prompting_baseline.py"
command: "OPENROUTER_API_KEY=<provided-in-session> .venv-gpu/bin/python src/run_prompting_baseline.py --input_mode txt --txt_file 'data/raw/Das Erdbeben in Chili.txt' --model nvidia/nemotron-3-super-120b-a12b:free --prompt_family A --max_sentences 4 --reasoning low --response_format none --max_retries 4 --output_dir outputs/prompting/2026-05-15/txt4_de_fix_ahi_v3/family_A && .venv-gpu/bin/python src/run_prompting_baseline.py --input_mode txt --txt_file 'data/raw/Das Erdbeben in Chili.txt' --model nvidia/nemotron-3-super-120b-a12b:free --prompt_family H --max_sentences 4 --reasoning low --response_format none --chunk_window 2 --max_retries 4 --output_dir outputs/prompting/2026-05-15/txt4_de_fix_ahi_v3/family_H && .venv-gpu/bin/python src/run_prompting_baseline.py --input_mode txt --txt_file 'data/raw/Das Erdbeben in Chili.txt' --model nvidia/nemotron-3-super-120b-a12b:free --prompt_family I --max_sentences 4 --reasoning low --response_format none --chunk_window 2 --score_threshold 50 --max_retries 4 --output_dir outputs/prompting/2026-05-15/txt4_de_fix_ahi_v3/family_I"
working_directory: "."
git_commit: "3728dae"
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
label_schema: "none (inference-only)"
prompt_version: "A/H/I with runtime parser upgrades and chunk-mode baseline support"
model_name: "nvidia/nemotron-3-super-120b-a12b:free"
varying_factor: "prompt_family (A,H,I)"
fixed_conditions:
  - "input_mode=txt"
  - "German file only"
  - "first 4 sentences"
  - "reasoning=low"
  - "temperature=0.0"
  - "top_p=1.0"
  - "max_tokens=256"
  - "max_retries=4"
random_seed: 1337
output_dir: "outputs/prompting/2026-05-15/txt4_de_fix_ahi_v3/"
artifacts_expected:
  - "family_A/{command.txt,config.json,results.json,summary.json,review.jsonl,review_schema.json}"
  - "family_H/{command.txt,config.json,results.json,summary.json,review.jsonl,review_schema.json}"
  - "family_I/{command.txt,config.json,results.json,summary.json,review.jsonl,review_schema.json}"
artifacts_produced:
  - "outputs/prompting/2026-05-15/txt4_de_fix_ahi_v3/family_A/summary.json"
  - "outputs/prompting/2026-05-15/txt4_de_fix_ahi_v3/family_H/summary.json"
  - "outputs/prompting/2026-05-15/txt4_de_fix_ahi_v3/family_I/summary.json"
main_metric_name: "parse_failure_rate"
main_metric_value: 0.0
precision: ""
recall: ""
f1: ""
iou: ""
runtime: "121.9s total"
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

Confirm that parser/runtime fixes remove family A parse drift and enable robust baseline execution for chunk families H/I.

## What was held constant

- Same DE TXT source (`Das Erdbeben in Chili.txt`), first 4 sentences.
- Same model/provider and deterministic decode settings.
- Same baseline runner with `reasoning=low` and `max_retries=4`.

## What changed

- Family A parser now accepts label tokens in noisy text and JSON `{label: ...}` fallbacks.
- Baseline runner now supports chunk-family execution for H/I.
- Retry strict suffix is family-aware (A/B... vs H vs I).
- Family I auto-upgrades to strict `json_schema` when user requests `response_format=none`.

## Outcome

All three families completed with zero parse failures:

- A: parse failures 0/4, predicted borders 3, avg latency 4.852s, elapsed 19.4s.
- H: parse failures 0/4, predicted borders 0, avg latency 11.699s, elapsed 46.8s.
- I: parse failures 0/4, predicted borders 1, avg latency 9.282s, elapsed 37.1s.

## Interpretation

The parser/runtime fixes resolve the previously observed A drift and baseline H/I parse instability in this smoke setup.

## Next step

Re-run the broader 4-sentence DE family sweep (A-G,J + H/I in baseline) using the updated runner, then extend to EN/RU smoke parity.
