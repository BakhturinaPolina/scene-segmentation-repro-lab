---
note_type: run
run_id: run_20260530_excel_controlled_postprocessing_sweep
title: "Excel-manifest controlled post-processing sweep (none vs min_scene_len_3 vs min_scene_len_5)"
date: 2026-05-30
track: prompting
run_type: experiment
status: success
goal: "Execute a fresh controlled full-eval family-B run on Excel-manifest data, then run one-factor post-processing variants and compare exact+tolerant metrics with FP tables."
entrypoint: "src/run_prompting_stratified.py + scripts/score_prompting_vs_excel_gold.py + scripts/normalization_what_if.py + scripts/export_top_fp_review_table.py"
command: "OPENROUTER_API_KEY=<session> PYTHONUNBUFFERED=1 .venv/bin/python -u src/run_prompting_stratified.py --excel_manifest data/processed/manifest_excel_prompting.json --model nvidia/nemotron-3-super-120b-a12b --prompt_family B --full_eval --reasoning off --temperature 0 --top_p 1.0 --seed 1337 --max_tokens 256 --response_format json_schema --schema_file src/prompts/json_schema_label_reason.json --date 2026-05-30-excel-controlled-sweep"
working_directory: "."
git_commit: "96bae86"
environment: ".venv"
os: "Linux"
hardware: "CPU"
gpu: ""
cuda_notes: ""
api_provider: "openrouter"
api_model: "nvidia/nemotron-3-super-120b-a12b"
api_cost_estimate: "non-free routing; cost not captured in run artifacts"
dataset_assets:
  - "data/processed/manifest_excel_prompting.json"
  - "data/processed/excel_prompting/gaensemagd_sentence_level/gaensemagd_sentence_level__gold_labels.csv"
  - "data/processed/excel_prompting/kleist_sentence_level/kleist_sentence_level__gold_labels.csv"
label_schema: "coarse BORDER/NOBORDER from Excel-derived gold CSVs"
prompt_version: "family B (src/prompts/B_zero_shot_json.txt) + src/prompts/json_schema_label_reason.json"
model_name: "nvidia/nemotron-3-super-120b-a12b"
varying_factor: "post-processing rule only: none, min_scene_len_3, min_scene_len_5"
fixed_conditions:
  - "same model and prompt family (B)"
  - "same decode controls (temperature=0, top_p=1.0, seed=1337, max_tokens=256)"
  - "same full_eval setting and Excel manifest"
  - "same scoring/FP export pipeline across scenarios"
random_seed: 1337
output_dir: "outputs/prompting/2026-05-30-excel-controlled-sweep/full_nvidia_nemotron-3-super-120b-a12b_familyB_reasoning-off/"
artifacts_expected:
  - "summary.json"
  - "outputs/review/excel_controlled_sweep/none/score_vs_gold_aggregate.json"
  - "outputs/review/excel_controlled_sweep/comparison/normalization_what_if.csv"
  - "outputs/review/excel_controlled_sweep/none/top_fp_review_table.csv"
  - "outputs/review/excel_controlled_sweep/min_scene_len_3/top_fp_review_table.csv"
  - "outputs/review/excel_controlled_sweep/min_scene_len_5/top_fp_review_table.csv"
artifacts_produced:
  - "outputs/prompting/2026-05-30-excel-controlled-sweep/full_nvidia_nemotron-3-super-120b-a12b_familyB_reasoning-off/summary.json"
  - "outputs/review/excel_controlled_sweep/none/score_vs_gold_gaensemagd.json"
  - "outputs/review/excel_controlled_sweep/none/score_vs_gold_kleist.json"
  - "outputs/review/excel_controlled_sweep/none/score_vs_gold_aggregate.json"
  - "outputs/review/excel_controlled_sweep/comparison/normalization_what_if.json"
  - "outputs/review/excel_controlled_sweep/comparison/normalization_what_if.csv"
  - "outputs/review/excel_controlled_sweep/none/top_fp_review_table.csv"
  - "outputs/review/excel_controlled_sweep/min_scene_len_3/top_fp_review_table.csv"
  - "outputs/review/excel_controlled_sweep/min_scene_len_5/top_fp_review_table.csv"
main_metric_name: "aggregate exact F1 (none baseline; direct score_vs_gold)"
main_metric_value: 0.0986
precision: 0.0579
recall: 0.3333
f1: 0.0986
iou: ""
runtime: "runner elapsed_ms: 664526"
failure_category: ""
related_experiment: "experiment__prompting__post-processing__excel-controlled-sweep"
related_issue: ""
decision_relevance: true
notion_targets:
  roadmap: "Excel-manifest controlled post-processing sweep"
  runs: true
  experiments: true
  artifacts: true
  issues: false
  decisions: false
---

## Objective

Run a fresh, reproducible full-eval inference on the Excel-manifest path with fixed family-B controls, then isolate one factor (post-processing rule) and compare `none`, `min_scene_len_3`, and `min_scene_len_5`.

## What was held constant

- Model: `nvidia/nemotron-3-super-120b-a12b`.
- Prompt family: `B`.
- Eval mode: `--full_eval`.
- Decode controls: `temperature=0`, `top_p=1.0`, `seed=1337`, `max_tokens=256`.
- Structured output: `response_format=json_schema` with `src/prompts/json_schema_label_reason.json`.
- Input corpus: `data/processed/manifest_excel_prompting.json`.

## What changed

- Post-processing scenario only:
  - `none` (baseline)
  - `min_scene_len_3`
  - `min_scene_len_5`
- FP table export was run once per scenario, using the same cached predictions from the fresh full-eval run.

## Outcome

- Fresh run completed successfully with zero parse failures (`elapsed_ms=664526`).
- Baseline exact aggregate (`score_vs_gold_aggregate.json`): P `0.0579`, R `0.3333`, F1 `0.0986`, Acc `0.5949`.
- One-factor scenario comparison (`normalization_what_if.csv`, aggregate rows):
  - `none`: exact F1 `0.0993`, tol3 F1 `0.3604`, tol5 F1 `0.4242`
  - `min_scene_len_3`: exact F1 `0.0909`, tol3 F1 `0.5063`, tol5 F1 `0.5676`
  - `min_scene_len_5`: exact F1 `0.0896`, tol3 F1 `0.5373`, tol5 F1 `0.6667`
- FP review tables generated for all three variants at `top_k=10` per text.

## Interpretation

The controlled sweep confirms the tradeoff: stronger minimum-scene-length filtering reduces exact recall/F1 but substantially improves tolerant boundary quality (`tol3`/`tol5`). On this Excel-manifest set, `min_scene_len_5` provides the strongest tolerant result while remaining precision-positive vs baseline.

## Next step

Decide whether the deployment objective prioritizes strict exact boundary placement or tolerant boundary proximity; if tolerant behavior is preferred, candidate default is `min_scene_len_5` for this dataset family, followed by a confirmatory rerun on additional Excel-derived texts.
