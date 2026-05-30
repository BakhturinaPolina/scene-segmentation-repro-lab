---
note_type: run
run_id: run_20260530_excel_manifest_familyb_full_eval_whatif
title: "Excel-manifest prompting: family B full-eval run + normalization what-if"
date: 2026-05-30
track: prompting
run_type: experiment
status: success
goal: "Run the project winner configuration on two Excel-derived texts via run_prompting_stratified.py and quantify gap drivers using direct gold scoring, FP analysis, and normalization what-if scenarios."
entrypoint: "src/run_prompting_stratified.py + scripts/score_prompting_vs_excel_gold.py + scripts/normalization_what_if.py"
command: "OPENROUTER_API_KEY=<session> .venv/bin/python src/run_prompting_stratified.py --excel_manifest data/processed/manifest_excel_prompting.json --model nvidia/nemotron-3-super-120b-a12b --prompt_family B --full_eval --reasoning off --temperature 0 --top_p 1.0 --seed 1337 --max_tokens 256 --response_format json_schema --schema_file src/prompts/json_schema_label_reason.json --date 2026-05-30-excel-full-eval"
working_directory: "."
git_commit: "07a008f"
environment: ".venv"
os: "Linux"
hardware: "CPU"
gpu: ""
cuda_notes: ""
api_provider: "openrouter"
api_model: "nvidia/nemotron-3-super-120b-a12b"
api_cost_estimate: "non-free routing; exact cost not captured in run artifacts"
dataset_assets:
  - "data/processed/manifest_excel_prompting.json"
  - "data/processed/excel_prompting/gaensemagd_sentence_level/gaensemagd_sentence_level__gold_labels.csv"
  - "data/processed/excel_prompting/kleist_sentence_level/kleist_sentence_level__gold_labels.csv"
label_schema: "coarse BORDER/NOBORDER from scene/scene_id transitions in Excel exports"
prompt_version: "family B (src/prompts/B_zero_shot_json.txt) with json_schema_label_reason"
model_name: "nvidia/nemotron-3-super-120b-a12b"
varying_factor: "normalization what-if scenario (none / burst collapse / minimum scene length)"
fixed_conditions:
  - "same model and prompt family (B)"
  - "same decode controls (temperature=0, top_p=1.0, max_tokens=256, seed=1337)"
  - "same evaluator and gold files"
random_seed: 1337
output_dir: "outputs/prompting/2026-05-30-excel-full-eval/full_nvidia_nemotron-3-super-120b-a12b_familyB_reasoning-off/"
artifacts_expected:
  - "summary.json"
  - "review_gaensemagd_sentence_level.jsonl"
  - "review_kleist_sentence_level.jsonl"
  - "score_vs_gold_aggregate.json"
  - "fp_analysis_summary.json"
  - "normalization_what_if.csv"
artifacts_produced:
  - "outputs/prompting/2026-05-30-excel-full-eval/full_nvidia_nemotron-3-super-120b-a12b_familyB_reasoning-off/summary.json"
  - "outputs/prompting/2026-05-30-excel-full-eval/full_nvidia_nemotron-3-super-120b-a12b_familyB_reasoning-off/score_vs_gold_gaensemagd.json"
  - "outputs/prompting/2026-05-30-excel-full-eval/full_nvidia_nemotron-3-super-120b-a12b_familyB_reasoning-off/score_vs_gold_kleist.json"
  - "outputs/prompting/2026-05-30-excel-full-eval/full_nvidia_nemotron-3-super-120b-a12b_familyB_reasoning-off/score_vs_gold_aggregate.json"
  - "outputs/prompting/2026-05-30-excel-full-eval/full_nvidia_nemotron-3-super-120b-a12b_familyB_reasoning-off/fp_analysis_summary.json"
  - "outputs/prompting/2026-05-30-excel-full-eval/full_nvidia_nemotron-3-super-120b-a12b_familyB_reasoning-off/top_fp_review_table.csv"
  - "outputs/prompting/2026-05-30-excel-full-eval/full_nvidia_nemotron-3-super-120b-a12b_familyB_reasoning-off/normalization_what_if.json"
  - "outputs/prompting/2026-05-30-excel-full-eval/full_nvidia_nemotron-3-super-120b-a12b_familyB_reasoning-off/normalization_what_if.csv"
main_metric_name: "aggregate exact F1 (BORDER/NOBORDER)"
main_metric_value: 0.1194
precision: 0.0708
recall: 0.3810
f1: 0.1194
iou: ""
runtime: "full_eval runner command: 928979 ms elapsed"
failure_category: ""
related_experiment: "experiment__prompting__stss2-section52-campaign"
related_issue: ""
decision_relevance: true
notion_targets:
  roadmap: "Excel-manifest adaptation and comparability analysis"
  runs: true
  experiments: true
  artifacts: true
  issues: false
  decisions: false
---

## Objective

Run the winner prompting setup from the project campaign (family B, reasoning off, deterministic decode) on two new Excel-derived texts through the same stratified runner used for report pipeline runs, then quantify where metric differences come from.

## What was held constant

- Model: `nvidia/nemotron-3-super-120b-a12b`.
- Prompt family: `B`.
- Decode controls: `temperature=0`, `top_p=1.0`, `seed=1337`, `max_tokens=256`.
- Structured output: `response_format=json_schema` with `src/prompts/json_schema_label_reason.json`.
- Gold matching and scoring interface from `scripts/score_prompting_vs_excel_gold.py`.

## What changed

- Input source changed from STSS XMI dataset path to Excel-manifest path:
  `--excel_manifest data/processed/manifest_excel_prompting.json`.
- Added post-hoc normalization what-if scenarios:
  - baseline
  - burst collapse
  - minimum scene length 3
  - burst collapse + minimum scene length 3

## Outcome

- Full-eval aggregate exact metrics:
  - Precision `0.0708`
  - Recall `0.3810`
  - F1 `0.1194`
  - Accuracy `0.6266`
- FP profile:
  - Gaensemagd: `26` FP, `19.23%` within +-1, `42.31%` within +-3 of gold boundaries.
  - Kleist: `79` FP, `17.72%` within +-1, `32.91%` within +-3.
- Normalization what-if (aggregate):
  - Exact F1 stays low (`0.0952` to `0.1235`), but tolerant F1 improves:
    - tol3 F1 from `0.3889` (baseline) up to `0.5455`
    - tol5 F1 from `0.4468` up to `0.6000`

## Interpretation

The Excel-manifest setup remains precision-limited due to over-segmentation, but smoothing scenarios show many errors are near-placement/fragmentation phenomena rather than entirely unrelated boundary predictions.

Compared with prior baseline-runner TXT path, the stratified runner improves aggregate exact F1 by `+0.0340`, but still does not approach campaign report levels due to data/evaluation regime differences.

## Next step

Run one-factor controlled post-processing experiments on the Excel-manifest path (`none`, `min_scene_len_3`, `min_scene_len_5`, optional confidence threshold) and decide whether a standardized post-processing layer should be introduced for this dataset family.

