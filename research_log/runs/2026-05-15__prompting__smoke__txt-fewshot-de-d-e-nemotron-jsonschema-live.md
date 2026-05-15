---
note_type: run
run_id: run_20260515_txt_fewshot_de_d_e_nemotron_jsonschema_live
title: "TXT few-shot D/E smoke run on DE with strict JSON schema"
date: 2026-05-15
track: prompting
run_type: smoke
status: success
goal: "Validate that inlined few-shot prompt families D and E run stably on DE first-30 sentences when strict structured output is enforced."
entrypoint: "src/run_prompting_baseline.py"
command: "OPENROUTER_API_KEY=<provided-in-session> .venv-gpu/bin/python src/run_prompting_baseline.py --input_mode txt --txt_file 'data/raw/Das Erdbeben in Chili.txt' --model nvidia/nemotron-3-super-120b-a12b:free --prompt_family D --max_sentences 30 --reasoning low --response_format json_schema --schema_file src/prompts/json_schema_label_reason.json --output_dir outputs/prompting/2026-05-15/fewshot_D_txt_nemotron_30_de_jsonschema && OPENROUTER_API_KEY=<provided-in-session> .venv-gpu/bin/python src/run_prompting_baseline.py --input_mode txt --txt_file 'data/raw/Das Erdbeben in Chili.txt' --model nvidia/nemotron-3-super-120b-a12b:free --prompt_family E --max_sentences 30 --reasoning low --response_format json_schema --schema_file src/prompts/json_schema_label_reason.json --output_dir outputs/prompting/2026-05-15/fewshot_E_txt_nemotron_30_de_jsonschema"
working_directory: "."
git_commit: "7c3cfb4"
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
prompt_version: "few-shot families D and E with strict json_schema output"
model_name: "nvidia/nemotron-3-super-120b-a12b:free"
varying_factor: "prompt_family (D vs E)"
fixed_conditions:
  - "first 30 sentences"
  - "input_mode=txt"
  - "reasoning=low"
  - "temperature=0.0"
  - "top_p=1.0"
  - "max_tokens=256"
  - "response_format=json_schema"
  - "schema_file=src/prompts/json_schema_label_reason.json"
random_seed: 1337
output_dir: "outputs/prompting/2026-05-15/"
artifacts_expected:
  - "fewshot_D_txt_nemotron_30_de_jsonschema/{command.txt,config.json,results.json,summary.json,review.jsonl,review_schema.json}"
  - "fewshot_E_txt_nemotron_30_de_jsonschema/{command.txt,config.json,results.json,summary.json,review.jsonl,review_schema.json}"
artifacts_produced:
  - "outputs/prompting/2026-05-15/fewshot_D_txt_nemotron_30_de_jsonschema/summary.json"
  - "outputs/prompting/2026-05-15/fewshot_E_txt_nemotron_30_de_jsonschema/summary.json"
  - "outputs/prompting/2026-05-15/fewshot_D_txt_nemotron_30_de_jsonschema/review.jsonl"
  - "outputs/prompting/2026-05-15/fewshot_E_txt_nemotron_30_de_jsonschema/review.jsonl"
main_metric_name: "parse_failure_rate"
main_metric_value: 0.0
precision: ""
recall: ""
f1: ""
iou: ""
runtime: "601.5s total (D=282.7s, E=306.8s)"
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

Run DE smoke checks for newly inlined few-shot prompt families D and E, and verify that strict schema-constrained decoding removes malformed-output parse drift.

## What was held constant

- Model/provider: OpenRouter `nvidia/nemotron-3-super-120b-a12b:free`.
- Input slice: first 30 sentences from `data/raw/Das Erdbeben in Chili.txt`.
- Prompt mode and reasoning: `no-cot`, `reasoning=low`.
- Decode core: `temperature=0.0`, `top_p=1.0`, `max_tokens=256`.
- Structured output enforcement: `response_format=json_schema` with `src/prompts/json_schema_label_reason.json`.

## What changed

Only prompt family varied between two runs:

- Family D (`fewshot_D_txt_nemotron_30_de_jsonschema`)
- Family E (`fewshot_E_txt_nemotron_30_de_jsonschema`)

## Outcome

Both runs succeeded and produced full review artifacts with zero parse failures:

- D: 30/30 classified, predicted borders=29, parse failures=0, avg latency=9.424s, elapsed=282.7s.
- E: 30/30 classified, predicted borders=24, parse failures=0, avg latency=10.227s, elapsed=306.8s.

## Interpretation

`json_schema` enforcement restored output stability for few-shot D/E smoke runs on DE. Compared with the immediately preceding `json_object` attempt, malformed payload drift was eliminated at the parse layer (0/30 failures for both families), while preserving deterministic execution settings.

## Next step

Replicate the same json-schema-constrained smoke setup for EN and RU files, then compare D/E border-rate behavior cross-lingually against the baseline review artifacts.
