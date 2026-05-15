---
note_type: run
run_id: run_20260515_txt4_de_prompt_families_a_g_j_smoke
title: "TXT DE 4-sentence smoke across prompt families A-G,J"
date: 2026-05-15
track: prompting
run_type: smoke
status: partial
goal: "Quickly verify DE TXT execution stability on the first 4 sentences across prompt families under current schema settings."
entrypoint: "src/run_prompting_baseline.py"
command: "OPENROUTER_API_KEY=<provided-in-session> for fam in A B C D E F G J; do if [ $fam = A ]; then .venv-gpu/bin/python src/run_prompting_baseline.py --input_mode txt --txt_file 'data/raw/Das Erdbeben in Chili.txt' --model nvidia/nemotron-3-super-120b-a12b:free --prompt_family $fam --max_sentences 4 --reasoning low --response_format none --output_dir outputs/prompting/2026-05-15/txt4_de_all_families/family_$fam; else .venv-gpu/bin/python src/run_prompting_baseline.py --input_mode txt --txt_file 'data/raw/Das Erdbeben in Chili.txt' --model nvidia/nemotron-3-super-120b-a12b:free --prompt_family $fam --max_sentences 4 --reasoning low --response_format json_schema --schema_file src/prompts/json_schema_label_reason.json --output_dir outputs/prompting/2026-05-15/txt4_de_all_families/family_$fam; fi; done"
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
prompt_version: "registry A-G,J templates; A with response_format=none, others with strict json_schema"
model_name: "nvidia/nemotron-3-super-120b-a12b:free"
varying_factor: "prompt_family"
fixed_conditions:
  - "input_mode=txt"
  - "German file only"
  - "first 4 sentences"
  - "reasoning=low"
  - "temperature=0.0"
  - "top_p=1.0"
  - "max_tokens=256"
random_seed: 1337
output_dir: "outputs/prompting/2026-05-15/txt4_de_all_families/"
artifacts_expected:
  - "family_A/{command.txt,config.json,results.json,summary.json,review.jsonl,review_schema.json}"
  - "family_B/{command.txt,config.json,results.json,summary.json,review.jsonl,review_schema.json}"
  - "family_C/{command.txt,config.json,results.json,summary.json,review.jsonl,review_schema.json}"
  - "family_D/{command.txt,config.json,results.json,summary.json,review.jsonl,review_schema.json}"
  - "family_E/{command.txt,config.json,results.json,summary.json,review.jsonl,review_schema.json}"
  - "family_F/{command.txt,config.json,results.json,summary.json,review.jsonl,review_schema.json}"
  - "family_G/{command.txt,config.json,results.json,summary.json,review.jsonl,review_schema.json}"
  - "family_J/{command.txt,config.json,results.json,summary.json,review.jsonl,review_schema.json}"
artifacts_produced:
  - "outputs/prompting/2026-05-15/txt4_de_all_families/family_A/summary.json"
  - "outputs/prompting/2026-05-15/txt4_de_all_families/family_B/summary.json"
  - "outputs/prompting/2026-05-15/txt4_de_all_families/family_C/summary.json"
  - "outputs/prompting/2026-05-15/txt4_de_all_families/family_D/summary.json"
  - "outputs/prompting/2026-05-15/txt4_de_all_families/family_E/summary.json"
  - "outputs/prompting/2026-05-15/txt4_de_all_families/family_F/summary.json"
  - "outputs/prompting/2026-05-15/txt4_de_all_families/family_G/summary.json"
  - "outputs/prompting/2026-05-15/txt4_de_all_families/family_J/summary.json"
main_metric_name: "parse_failure_rate"
main_metric_value: 0.125
precision: ""
recall: ""
f1: ""
iou: ""
runtime: "895.4s total"
failure_category: "prompt_family_A_output_parse_instability"
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

Run a quick DE-only TXT smoke across prompt families to check parse stability and basic behavior after introducing strict json-schema decoding.

## What was held constant

- Same DE source file and first 4 sentences.
- Same model/provider and deterministic decode settings.
- Same baseline runner (`src/run_prompting_baseline.py`).

## What changed

Prompt family varied across A, B, C, D, E, F, G, J.

- A used `response_format=none` (label-only template contract).
- B/C/D/E/F/G/J used `response_format=json_schema` + `src/prompts/json_schema_label_reason.json`.
- H/I were not executed in this run because baseline TXT mode does not support chunk-only families.

## Outcome

Per-family summaries (4 sentences each):

- A: parse failures 4/4 (rate 1.0), predicted borders 0, avg latency 120.157s.
- B: parse failures 0/4, predicted borders 3, avg latency 13.377s.
- C: parse failures 0/4, predicted borders 1, avg latency 23.641s.
- D: parse failures 0/4, predicted borders 4, avg latency 6.414s.
- E: parse failures 0/4, predicted borders 4, avg latency 11.375s.
- F: parse failures 0/4, predicted borders 0, avg latency 7.075s.
- G: parse failures 0/4, predicted borders 2, avg latency 12.158s.
- J: parse failures 0/4, predicted borders 0, avg latency 17.106s.

## Interpretation

Strict schema decoding stabilized all JSON-oriented families (B/C/D/E/F/G/J) at 0 parse failures in this smoke. Family A remains unstable in TXT mode under current prompting/parsing assumptions and should be treated as failing for production comparisons.

## Next step

Either (a) exclude family A from follow-up multilingual sweeps, or (b) add a dedicated hard-output constraint path for A (e.g., final-line-only parser contract or separate schema-compatible A variant) before re-running A.
