---
note_type: run
run_id: run_20260709_dprose_final_outputs_scene_id
title: "dProse full corpus — Kleist-layout sentence export + forced opening border"
date: 2026-07-09
track: prompting
run_type: eval-only
status: success
goal: "Rework dProse final sentence artifacts to match Scenes_example output.xlsx column order (Sentence, Phrase, Text, is_scene_boundary, scene_id) plus model_reason; force sentence 0 to a scene boundary so scene_id and is_scene_boundary stay aligned for all 327 books."
entrypoint: "scripts/dprose/generate_final_outputs.py"
command: "python3 scripts/dprose/generate_final_outputs.py"
working_directory: "."
git_commit: "5598bdc"
environment: ".venv (stdlib + openpyxl 3.1.5)"
os: "Linux"
hardware: "CPU"
gpu: ""
cuda_notes: ""
api_provider: ""
api_model: ""
api_cost_estimate: "$0 (post-processing only)"
dataset_assets:
  - "outputs/runs/dprose_batch/dprose-full-corpus/corpus_progress.json"
  - "outputs/runs/dprose_batch/dprose-full-corpus/books/<slug>/predictions.jsonl"
  - "Scenes_example output.xlsx"
label_schema: "is_scene_boundary (TRUE/FALSE) + cumulative scene_id; sentence 0 forced to boundary"
prompt_version: "family B + json_schema_label_reason"
model_name: "gemini-2.5-pro"
varying_factor: "output format (Kleist column layout + forced opening border)"
fixed_conditions:
  - "Same input corpus as run_20260704_dprose_final_outputs; no model calls"
  - "Same anomaly definitions (|z| >= 2.0) and MANUAL_REVIEW table"
  - "scene_id[i] increments on every is_scene_boundary=True; sentence 0 always True"
random_seed: ""
output_dir: "outputs/runs/dprose_batch/dprose-full-corpus/final_outputs"
artifacts_expected:
  - "final_outputs/all_sentences.csv"
  - "final_outputs/all_sentences.xlsx"
  - "final_outputs/per_book_xlsx/<slug>.xlsx"
artifacts_produced:
  - "final_outputs/all_sentences.csv (120,369 rows; columns: slug, Sentence, Phrase, Text, is_scene_boundary, scene_id, model_reason)"
  - "final_outputs/all_sentences.xlsx (same columns/rows; Excel bools for is_scene_boundary)"
  - "final_outputs/per_book_xlsx/ (327 workbooks; columns: [index], Sentence, Phrase, Text, is_scene_boundary, scene_id, model_reason)"
  - "final_outputs/corpus_stats.csv / anomalous_books.csv / final_report.md (refreshed)"
main_metric_name: "sentences exported"
main_metric_value: "120,369 (327/327 books; 4 forced opening borders)"
runtime: "~46 s"
failure_category: ""
related_experiment: "run_20260704_dprose_final_outputs"
related_issue: ""
decision_relevance: false
notion_targets:
  roadmap: "dProse full-corpus prompting"
  runs: true
  experiments: false
  artifacts: true
  issues: false
  decisions: false
---

## Objective

Reviewer asked for dProse sentence outputs that match the Kleist-scenes
example workbook (`Scenes_example output.xlsx`) — same columns in the same
order, plus `model_reason` — and for the 4 books whose model left sentence 0
as NOBORDER to be aligned so `scene_id` and `is_scene_boundary` never disagree.

## What was held constant

- Same input predictions; no re-labelling by the model.
- Same corpus_stats / anomalous_books metric definitions.
- Phrase has no independent meaning in dProse (sentence-level only); it is
  filled with the 0-based sentence index so the column exists in the same
  position as the example.

## What changed

- `force_opening_border`: sentence 0 of every book is set to
  `is_scene_boundary=True` before `scene_id` is computed. Touched 4 books
  (`dprose_1800`, `dprose_209`, `dprose_2348`, `dprose_730`).
- `cumulative_scene_ids` now simply counts borders from the start, so
  `max(scene_id) == sum(is_scene_boundary)` for every book.
- Export columns reshaped to Kleist order + extras:
  - Corpus CSV/XLSX: `slug, Sentence, Phrase, Text, is_scene_boundary, scene_id, model_reason`
  - Per-book XLSX: `[unnamed index], Sentence, Phrase, Text, is_scene_boundary, scene_id, model_reason`
- `Sentence` = 1-based index; `Phrase` = 0-based index (no phrase split in dProse).
- openpyxl illegal-character sanitizer for a few model reasons that contained
  ASCII control chars.

## Outcome

- 327/327 books open with `is_scene_boundary=TRUE` and `scene_id=1`.
- 327/327 books satisfy `max(scene_id) == sum(is_scene_boundary)`.
- 4 opening borders forced (logged in script stdout).
- Files: `all_sentences.csv` (~53 MB), `all_sentences.xlsx` (~19 MB),
  327 per-book workbooks under `per_book_xlsx/`.

## Next step

Hand the refreshed `final_outputs/` to the reviewer. Optionally commit the
script + regenerated artifacts as a format-only change, and pin `openpyxl`
in `requirements.txt`.
