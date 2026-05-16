---
note_type: run
run_id: run_20260515_txt4_3lang_all_families_patched
title: "TXT 4-sentence all-family sweep across DE/EN/RU with patched runner"
date: 2026-05-15
track: prompting
run_type: smoke
status: success
goal: "Validate patched baseline family handling (A..J including H/I) across DE/EN/RU on first 4 sentences per file."
entrypoint: "src/run_prompting_baseline.py"
command: "OPENROUTER_API_KEY=<provided-in-session>; for lang in de en ru and family in A..J: run baseline TXT with max_sentences=4, reasoning=low, family-specific decode config (A/I response_format none -> effective json_schema, H response_format none chunk mode, others response_format json_schema with src/prompts/json_schema_label_reason.json)."
working_directory: "."
git_commit: "c869f5d"
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
prompt_version: "families A..J with patched parser/chunk handling"
model_name: "nvidia/nemotron-3-super-120b-a12b:free"
varying_factor: "language + prompt_family"
fixed_conditions:
  - "input_mode=txt"
  - "first 4 sentences"
  - "reasoning=low"
  - "temperature=0.0"
  - "top_p=1.0"
  - "max_tokens=256"
  - "max_retries=4"
  - "chunk_window=2 for H/I"
  - "score_threshold=50 for I"
random_seed: 1337
output_dir: "outputs/prompting/2026-05-15/{txt4_de_all_families_patched,txt4_en_all_families_patched,txt4_ru_all_families_patched}/"
artifacts_expected:
  - "per-language family_A..family_J: {command.txt,config.json,results.json,summary.json,review.jsonl,review_schema.json}"
artifacts_produced:
  - "outputs/prompting/2026-05-15/txt4_de_all_families_patched/family_A/summary.json"
  - "outputs/prompting/2026-05-15/txt4_de_all_families_patched/family_J/summary.json"
  - "outputs/prompting/2026-05-15/txt4_en_all_families_patched/family_A/summary.json"
  - "outputs/prompting/2026-05-15/txt4_en_all_families_patched/family_J/summary.json"
  - "outputs/prompting/2026-05-15/txt4_ru_all_families_patched/family_A/summary.json"
  - "outputs/prompting/2026-05-15/txt4_ru_all_families_patched/family_J/summary.json"
main_metric_name: "parse_failure_rate"
main_metric_value: 0.0
precision: ""
recall: ""
f1: ""
iou: ""
runtime: "DE 547.8s + EN/RU 879.4s"
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

Run a fresh patched all-family (`A..J`) 4-sentence smoke on DE and mirror EN/RU if DE is stable.

## What was held constant

- Model/provider and deterministic decode controls.
- First 4 sentences policy per language file.
- Single runner (`src/run_prompting_baseline.py`) and patched parser/chunk logic.

## What changed

Language (`DE`, `EN`, `RU`) and prompt family (`A..J`) varied.

## Outcome

All language/family runs completed with zero parse failures.

- DE stable: all families `pf=0/4`.
- EN stable: all families `pf=0/4`.
- RU stable: all families `pf=0/4`.

## Interpretation

Patched runner behavior is stable across all prompt families, including chunk families `H/I`, in this 3-language 4-sentence smoke envelope.

## Next step

Promote to a larger multilingual sample (e.g., first 30 sentences) for families A..J, preserving family-specific effective response formats captured in `summary.json`.
