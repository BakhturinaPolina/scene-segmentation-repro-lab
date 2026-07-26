---
note_type: artifact
artifact_id: art_excel_gemini_batch_families_comparison
title: "Comparison table: Gemini Batch prompt-family sweep on close-reading gold (B + K-Q)"
date: 2026-07-22
artifact_type: comparison
produced_by_run: "run_20260722_excel_gemini_batch_families"
track: prompting
path: "outputs/runs/prompting/2026-07-22-excel-gemini-batch-families/comparison.csv"
url: ""
description: "Per-family macro P/R/F1 at tol 0/1/3, over-prediction ratio, parse-ok rate, and batch cost for families B, K, L, M, N, O, P, Q on Gaensemagd + Kleist via the Gemini Batch API."
report_worthy: true
figure_or_table_candidate: "Table"
related_experiment: "experiment__prompting__prompt-family__gemini-batch-excel-BKQ.md"
related_task: ""
notion_targets:
  artifacts: true
  runs: true
  decisions: false
---

## What this artifact is

A cross-family comparison CSV (plus per-family `predictions.jsonl`, `summary.json`,
`score.json`) from the 2026-07-22 Gemini Batch sweep of prompt families B and
K-Q on the two close-reading gold texts.

Companion analysis doc: `docs/prompting/EXCEL_GEMINI_BATCH_FAMILIES_REPORT.md`.

## What it shows

Ranked by relaxed F1 (tol3), macro over Gaensemagd + Kleist:

| Family | F1@0 | F1@3 | over-pred (x gold) | parse-ok |
|--------|------|------|--------------------|----------|
| L | 0.5844 | 0.7832 | 2.10 | 1.000 |
| Q | 0.4838 | 0.6934 | 2.62 | 0.984 |
| N | 0.4367 | 0.6601 | 3.24 | 1.000 |
| K | 0.3703 | 0.5555 | 4.10 | 1.000 |
| M | 0.3709 | 0.5393 | 3.95 | 0.997 |
| B | 0.3776 | 0.5373 | 4.10 | 1.000 |
| P | 0.3433 | 0.5212 | 5.00 | 1.000 |
| O | 0.3456 | 0.5133 | 4.81 | 0.981 |

Total batch cost: $12.02.

## Why it matters

- Provides the Gemini-batch baseline for B (Model Selection) and quantifies the
  FP-reduction variants K-Q (Final Remarks over-segmentation point).
- Shows recall is uniformly high; precision/over-prediction is the differentiator.

## Reuse notes

- Re-score without re-calling the API: `--score_only` on the same `--date`.
- Regenerate the comparison from saved predictions with the same runner.
- Scoring logic: `src/eval/excel_gold_scoring.py` (BORDER-class F1 at tol 0/1/3,
  1-based gold/prediction indices aligned to 0-based positions).
