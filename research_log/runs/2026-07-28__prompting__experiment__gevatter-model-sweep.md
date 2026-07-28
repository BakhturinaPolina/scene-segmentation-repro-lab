---
note_type: run
run_id: run_20260728_gevatter_model_sweep
title: "Gevatter Excel gold: 4-model Family B sweep to complete three-text ranking"
date: 2026-07-28
track: prompting
run_type: experiment
status: success
goal: "Run the remaining Excel ranking models (Gemini reasoning-low, Opus 4, GPT-4.1, Sonnet 4) on Der Gevatter so the report model comparison can use three-text macro F1."
entrypoint: "src/runners/run_prompting_stratified.py"
command: "set -a && source .env && set +a; for each of google/gemini-2.5-pro (reasoning low), anthropic/claude-opus-4, openai/gpt-4.1, anthropic/claude-sonnet-4: .venv/bin/python -u src/runners/run_prompting_stratified.py --excel_manifest data/manifests/excel_prompting_gevatter.json --prompt_family B --full_eval --temperature 0 --top_p 1.0 --seed 1337 --max_tokens 256 --response_format json_schema --schema_file src/prompts/json_schema_label_reason.json --date 2026-07-28-excel-gevatter-model-sweep --model <model> --reasoning <on|low|off>"
working_directory: "."
git_commit: "4d37653"
environment: ".venv"
os: "Linux"
hardware: "CPU"
gpu: ""
cuda_notes: ""
api_provider: "openrouter"
api_model: "google/gemini-2.5-pro; anthropic/claude-opus-4; openai/gpt-4.1; anthropic/claude-sonnet-4"
api_cost_estimate: "~128 synchronous calls (4 models × 32 sentences); exact USD not captured"
dataset_assets:
  - "data/manifests/excel_prompting_gevatter.json"
  - "data/processed/excel_prompting/gevatter_sentences/gevatter_sentences__gold_labels.csv"
label_schema: "coarse BORDER/NOBORDER from Scene_Nr transitions"
prompt_version: "family B with json_schema_label_reason"
model_name: "multi-model sweep"
varying_factor: "model (+ Gemini reasoning low vs the already-run Gemini reasoning on)"
fixed_conditions:
  - "prompt family B"
  - "temperature=0, top_p=1.0, seed=1337, max_tokens=256"
  - "token-budget context (~409)"
  - "Gevatter only (32 sentences)"
random_seed: 1337
output_dir: "outputs/runs/prompting/2026-07-28-excel-gevatter-model-sweep/"
artifacts_expected:
  - "summary.json per model"
  - "review_gevatter_sentences.jsonl per model"
artifacts_produced:
  - "outputs/runs/prompting/2026-07-28-excel-gevatter-model-sweep/full_google_gemini-2.5-pro_familyB_reasoning-low/summary.json"
  - "outputs/runs/prompting/2026-07-28-excel-gevatter-model-sweep/full_anthropic_claude-opus-4_familyB_reasoning-off/summary.json"
  - "outputs/runs/prompting/2026-07-28-excel-gevatter-model-sweep/full_openai_gpt-4.1_familyB_reasoning-off/summary.json"
  - "outputs/runs/prompting/2026-07-28-excel-gevatter-model-sweep/full_anthropic_claude-sonnet-4_familyB_reasoning-off/summary.json"
  - "logs/excel_gevatter/2026-07-28-excel-gevatter-model-sweep__*.log"
main_metric_name: "Gevatter relaxed F1 (tol_3)"
main_metric_value: "0.80–0.91 depending on model"
precision: ""
recall: ""
f1: ""
iou: ""
runtime: "~6.3 min wall for all four models"
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

Complete the Excel model ranking on *Der Gevatter* for the four configs that previously ran only on Gaensemagd + Kleist, so three-text macro F1 can be reported alongside the two-text ranking.

## What was held constant

Same as the May Excel ranking and the earlier Gemini-on Gevatter run: Family B, temp 0, seed 1337, JSON schema, ~409-token context, full eval.

## What changed

Model/reasoning only (Gemini low; Opus 4 off; GPT-4.1 off; Sonnet 4 off). Gemini reasoning-on already existed under `2026-07-28-excel-gevatter-gemini-reasoning-on`.

## Outcome

| Model | Reasoning | Gevatter exact F1 | Gevatter relaxed F1 | Pred / gold |
| ----- | --------- | ----------------- | ------------------- | ----------- |
| Gemini 2.5 Pro | on (prior run) | 0.364 | 0.909 | 6/5 |
| Gemini 2.5 Pro | low | 0.462 | 0.800 | 8/5 |
| Claude Opus 4 | off | 0.667 | 0.909 | 10/5 |
| GPT-4.1 | off | 0.462 | 0.909 | 8/5 |
| Claude Sonnet 4 | off | 0.556 | 0.909 | 13/5 |

Three-text macro relaxed F1 ranking: Gemini on **0.811**, Gemini low 0.746, GPT-4.1 0.714, Opus 0.712, Sonnet 0.634. Gemini on remains the production choice on the headline metric.

## Interpretation

*The Godfather* is too short and easy under tol 3 to separate most models (four configs tie at 0.91). Ranking still depends on the longer texts. Opus gains on exact match via high Gevatter exact F1 but does not overtake Gemini on relaxed F1.

## Next step

Report draft updated with 2-text vs 3-text model ranking table.
