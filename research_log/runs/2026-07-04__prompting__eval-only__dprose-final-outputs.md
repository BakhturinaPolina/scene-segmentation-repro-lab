---
note_type: run
run_id: run_20260704_dprose_final_outputs
title: "dProse full corpus — final review CSVs + corpus report"
date: 2026-07-04
track: prompting
run_type: eval-only
status: success
goal: "Turn the completed 327-book dProse corpus into review-ready artifacts: per-book metrics CSV, border-rate anomaly CSV with manual notes, sentence-level CSV (0/1 + model reasoning), and a short plain-language corpus report."
entrypoint: "scripts/dprose/generate_final_outputs.py"
command: "python3 scripts/dprose/generate_final_outputs.py"
working_directory: "."
git_commit: "e9dede3"
environment: ".venv (stdlib only: csv/json/statistics)"
os: "Linux"
hardware: "CPU"
gpu: ""
cuda_notes: ""
api_provider: ""
api_model: ""
api_cost_estimate: "$0 (post-processing only)"
dataset_assets:
  - "outputs/runs/dprose_batch/dprose-full-corpus/corpus_progress.json"
  - "outputs/runs/dprose_batch/dprose-full-corpus/books/<slug>/book_review.json"
  - "outputs/runs/dprose_batch/dprose-full-corpus/books/<slug>/predictions.jsonl"
label_schema: "prediction-only BORDER/NOBORDER (no gold labels)"
prompt_version: "family B + json_schema_label_reason"
model_name: "gemini-2.5-pro"
varying_factor: "none"
fixed_conditions:
  - "Reads completed corpus artifacts; no model calls"
  - "Anomaly threshold |z(border_rate)| >= 2.0 across 327 books"
  - "split_candidate = NOBORDER inside a scene >= 10 sentences; merge_candidate = BORDER adjacent to BORDER"
random_seed: ""
output_dir: "outputs/runs/dprose_batch/dprose-full-corpus/final_outputs"
artifacts_expected:
  - "final_outputs/corpus_stats.csv"
  - "final_outputs/anomalous_books.csv"
  - "final_outputs/all_sentences.csv"
  - "final_outputs/final_report.md"
artifacts_produced:
  - "final_outputs/corpus_stats.csv (327 books + aggregate row)"
  - "final_outputs/anomalous_books.csv (16 outliers, manual review columns filled)"
  - "final_outputs/all_sentences.csv (120,369 rows)"
  - "final_outputs/final_report.md"
main_metric_name: "sentences exported"
main_metric_value: "120,369 (327/327 books)"
runtime: "~6 s"
failure_category: ""
related_experiment: "run_20260704_dprose_corpus_retry_failed"
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

Produce the final, human-review-ready deliverables for the completed dProse
full-corpus scene-segmentation run (327 books, 120,369 sentences). Four
artifacts in `outputs/runs/dprose_batch/dprose-full-corpus/final_outputs/`.

## What was held constant

- Source of truth: per-book `book_review.json` (pre-computed scene stats) and
  `predictions.jsonl` (sentence labels + model reasoning); `corpus_progress.json`
  for the authoritative 327-book list.
- Two pilot-seeded books (`dprose_2158`, `dprose_806`) lack `book_review.json`;
  their stats are recomputed on the fly via the imported
  `evaluation.review_dprose_book.summarize_book` so all 327 books are covered.
- Metric definitions match `review_dprose_book.py` (scene lengths, consecutive
  BORDER runs, short-scene rate, gaps ≥ 10).

## What changed

New script `scripts/dprose/generate_final_outputs.py`. No corpus data mutated.

## Outcome

- `corpus_stats.csv`: 327 book rows + 1 aggregate row.
- `anomalous_books.csv`: 16 border-rate outliers (9 HIGH, 7 LOW). Numeric
  columns script-filled; `likely_cause` / `review_notes` filled by hand after
  reading each book's actual BORDER sentences (stored in the script's
  `MANUAL_REVIEW` table for reproducibility).
- `all_sentences.csv`: 120,369 rows. `border` 0/1, `model_reason`,
  `merge_candidate`/`split_candidate`/`review_flag`, `manual_fix` columns.
  Flags: border=28,185; merge=17,893; split=49,609; any-flag=67,502 (56.1%).
- `final_report.md`: plain-language corpus summary.

## Interpretation

Corpus-median per-book median scene length is 2 sentences; median border rate
24.0% (range 8.9–41.4%). HIGH outliers are fragmentary/dialogic/epistolary
texts (over-segmentation); LOW outliers are long single-setting dialogue or
frame narratives — notably four books (`dprose_693/697/701/702`) from the same
recurring "Dagobert Trostler" detective series. The wide border-rate spread
reflects dProse's genre heterogeneity; there is no single correct rate.

## Data-quality notes

- Fixed a preview bug: `book_review.json.first_sentence_preview` is not always
  the true opening (some `predictions.jsonl` are not stored in strict index
  order after retries), so the anomaly CSV now derives the preview from the
  index-0 sentence.
- Stale root artifacts `corpus_summary.json` and `predictions_full.jsonl`
  (3-book pilot) are ignored; documented in the report.

## Next step

Optional: hand-review pass on the 16 anomalous books using `review_notes`
(start with `dprose_661`, 408 split candidates). Optionally commit the new
script + artifacts.
