---
note_type: artifact
artifact_id: art_dprose_final_outputs_tables
title: "dProse final review CSVs (corpus stats, anomalies, all sentences)"
date: 2026-07-04
artifact_type: table
produced_by_run: run_20260704_dprose_final_outputs
track: prompting
path: "outputs/runs/dprose_batch/dprose-full-corpus/final_outputs/"
url: ""
description: "Three CSVs summarizing the 327-book dProse scene-segmentation run for manual review."
report_worthy: true
figure_or_table_candidate: "Table"
related_experiment: "run_20260704_dprose_corpus_retry_failed"
related_task: ""
notion_targets:
  artifacts: true
  runs: true
  decisions: false
---

## What this artifact is

Three CSVs in `final_outputs/`:

- `corpus_stats.csv` — one row per book (327) + a corpus aggregate row.
  Columns: sentence_count, parse_ok_rate, border_rate, scene_length
  median/mean/min/max, short_scene_rate, consecutive_border_pairs,
  max_consecutive_border_run, gaps_ge_10, estimated_cost_usd.
- `anomalous_books.csv` — 16 books with |z(border_rate)| ≥ 2.0 (9 HIGH, 7 LOW).
  Numeric metrics + merge/split candidate counts, plus hand-written
  `likely_cause` and `review_notes` per book and the true opening sentence.
- `all_sentences.csv` — 120,369 rows: slug, sentence_index, sentence_text_full,
  `border` (0/1), `model_reason`, `merge_candidate`, `split_candidate`,
  `review_flag`, `manual_fix`, `manual_fix_confidence`.

## What it shows

- Median per-book border rate 24.0% (range 8.9–41.4%); corpus-median median
  scene length 2 sentences; mean short-scene rate 54%.
- Sentence flags: border 28,185; merge candidates 17,893; split candidates
  49,609; any review flag 67,502 (56.1%).
- HIGH outliers = fragmentary / dialogic / epistolary texts (over-segmentation);
  LOW outliers = long single-setting dialogue / frame narratives, incl. the
  `dprose_693/697/701/702` "Dagobert Trostler" detective series.

## Why it matters

These are the review-ready deliverables for the corpus: `all_sentences.csv`
mirrors the Excel gold-label layout (0/1) but adds model reasoning and
merge/split flags; `anomalous_books.csv` points reviewers at the books most
likely mis-segmented and says exactly where to look.

## Reuse notes

Regenerate with `python3 scripts/dprose/generate_final_outputs.py`. The
qualitative anomaly notes live in the script's `MANUAL_REVIEW` table so re-runs
preserve them; a warning prints if a newly flagged book lacks an entry. No gold
labels — all metrics are plausibility signals, not accuracy.
