---
note_type: run
run_id: run_20260728_gevatter_gemini_reasoning_on
title: "Gevatter Excel gold: Gemini 2.5 Pro Family B reasoning-on full eval via OpenRouter"
date: 2026-07-28
track: prompting
run_type: eval-only
status: success
goal: "Label Der Gevatter (32 sentences) with the production Prompt B / Gemini 2.5 Pro reasoning-on settings used for the Excel model ranking, score against Excel-derived gold, and document results for the Automatic Scene Segmentation report."
entrypoint: "scripts/data/prepare_excel_prompting_inputs.py + src/runners/run_prompting_stratified.py"
command: "set -a && source .env && set +a && .venv/bin/python -u src/runners/run_prompting_stratified.py --excel_manifest data/manifests/excel_prompting_gevatter.json --model google/gemini-2.5-pro --prompt_family B --full_eval --reasoning on --temperature 0 --top_p 1.0 --seed 1337 --max_tokens 256 --response_format json_schema --schema_file src/prompts/json_schema_label_reason.json --date 2026-07-28-excel-gevatter-gemini-reasoning-on"
working_directory: "."
git_commit: "7ee3626"
environment: ".venv"
os: "Linux"
hardware: "CPU"
gpu: ""
cuda_notes: ""
api_provider: "openrouter"
api_model: "google/gemini-2.5-pro"
api_cost_estimate: "~32 synchronous calls; exact USD not captured in run artifacts"
dataset_assets:
  - "data/raw/excel/gevatter_sentences.xlsx"
  - "data/manifests/excel_prompting_gevatter.json"
  - "data/processed/excel_prompting/gevatter_sentences/gevatter_sentences__gold_labels.csv"
  - "data/processed/excel_prompting/gevatter_sentences/gevatter_sentences__for_prompting.txt"
label_schema: "coarse BORDER/NOBORDER from Scene_Nr transitions in gevatter_sentences.xlsx"
prompt_version: "family B (src/prompts) with json_schema_label_reason"
model_name: "google/gemini-2.5-pro"
varying_factor: "corpus text (Gevatter only; settings matched to 2026-05-31 Excel Gemini reasoning-on baseline)"
fixed_conditions:
  - "prompt family B"
  - "reasoning on"
  - "temperature=0, top_p=1.0, seed=1337, max_tokens=256"
  - "response_format=json_schema with src/prompts/json_schema_label_reason.json"
  - "token-budget context (~409)"
  - "full_eval on all sentences"
random_seed: 1337
output_dir: "outputs/runs/prompting/2026-07-28-excel-gevatter-gemini-reasoning-on/full_google_gemini-2.5-pro_familyB_reasoning-on/"
artifacts_expected:
  - "summary.json"
  - "review_gevatter_sentences.jsonl"
  - "cache_gevatter_sentences.json"
  - "command.txt"
  - "config.json"
artifacts_produced:
  - "outputs/runs/prompting/2026-07-28-excel-gevatter-gemini-reasoning-on/full_google_gemini-2.5-pro_familyB_reasoning-on/summary.json"
  - "outputs/runs/prompting/2026-07-28-excel-gevatter-gemini-reasoning-on/full_google_gemini-2.5-pro_familyB_reasoning-on/review_gevatter_sentences.jsonl"
  - "outputs/runs/prompting/2026-07-28-excel-gevatter-gemini-reasoning-on/full_google_gemini-2.5-pro_familyB_reasoning-on/results_gevatter_sentences.json"
  - "outputs/runs/prompting/2026-07-28-excel-gevatter-gemini-reasoning-on/full_google_gemini-2.5-pro_familyB_reasoning-on/cache_gevatter_sentences.json"
  - "logs/excel_gevatter/2026-07-28-gevatter-gemini-reasoning-on.log"
main_metric_name: "relaxed F1 (tol_3)"
main_metric_value: 0.9091
precision: 0.8333
recall: 1.0
f1: 0.9091
iou: ""
runtime: "~114 s wall clock (32 sentences, avg latency 3.40 s)"
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

Convert `gevatter_sentences.xlsx` into the Excel prompting format, run the same Gemini 2.5 Pro / Prompt B / reasoning-on configuration used for the May Excel model ranking, and score against gold scene borders for inclusion in the Automatic Scene Segmentation report.

## What was held constant

- Model `google/gemini-2.5-pro` via OpenRouter.
- Prompt family B with JSON schema `label` + `reason`.
- Decode: temperature 0, top_p 1.0, seed 1337, max_tokens 256, reasoning on.
- Context mode: token budget ~409 (same as Excel baseline).
- Gold derivation: first sentence of each `Scene_Nr` → BORDER.

## What changed

- New gold text only: *Der Gevatter* (32 sentences, 5 scenes / 5 gold borders).
- Separate manifest `data/manifests/excel_prompting_gevatter.json` (did not overwrite the Gaensemagd+Kleist manifest).
- Prepare-script column inference extended to accept `sentence` and `Scene_Nr`-style columns; sheet name `"Sheet 1"`.

## Outcome

- Run complete (`run_complete=true`), 0 parse failures, accuracy 78.1% (25/32 exact label matches).
- Exact (tol 0): P=0.333 R=0.400 F1=**0.364** (TP=2 FP=4 FN=3).
- Relaxed (tol 3): P=0.833 R=1.000 F1=**0.909** (TP=5 FP=1 FN=0).
- Predictions: 6 borders vs 5 gold (over-prediction ratio 1.2×).
- Three-text macro with May Gemini reasoning-on per-doc F1 (Gaensemagd 0.4545/0.8235, Kleist 0.5417/0.7000, Gevatter 0.3636/0.9091): exact **0.45**, relaxed **0.81**.

## Interpretation

Exact F1 is lower than on the longer Excel texts because several borders are off by 1–2 sentences; relaxed scoring recovers all gold borders. Over-prediction is mild relative to earlier Excel runs (~2× on Gaensemagd+Kleist). Production choice (Gemini 2.5 Pro, reasoning on) remains appropriate.

## Next step

Report draft updated with Gevatter data and scores. Optional: re-run other models from the Excel ranking on Gevatter for a full three-text model table (not required for production confirmation).
