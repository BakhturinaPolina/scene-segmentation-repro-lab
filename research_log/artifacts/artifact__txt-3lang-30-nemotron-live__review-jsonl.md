---
note_type: artifact
artifact_id: art_txt_3lang_30_nemotron_live_review_jsonl
title: "30-sentence DE/EN/RU review JSONL artifacts"
date: 2026-05-15
artifact_type: predictions
produced_by_run: "run_20260515_txt_3lang_30_prompting_baseline_nemotron_live"
track: prompting
path: "outputs/prompting/2026-05-15/"
url: ""
description: "Manual-review-ready JSONL outputs with full sentence text, compact decision, and full raw model response for DE/EN/RU 30-sentence baseline runs."
report_worthy: true
figure_or_table_candidate: "Table"
related_experiment: "experiment_prompting_model_free_120b_comparison"
related_task: "3-language stronger baseline reviewability"
notion_targets:
  artifacts: true
  runs: true
  decisions: false
---

## What this artifact is

Three per-language baseline folders with full review exports:

- `outputs/prompting/2026-05-15/baseline_txt_nemotron_30_de`
- `outputs/prompting/2026-05-15/baseline_txt_nemotron_30_en`
- `outputs/prompting/2026-05-15/baseline_txt_nemotron_30_ru`

Each contains:
- `results.json`
- `summary.json`
- `review.jsonl`
- `review_schema.json`

## What it shows

- Exactly 30 rows per language in `review.jsonl`.
- Full sentence text is preserved (no truncation).
- Both compact decision and full raw model response are stored per sentence.
- Parse failures are zero for DE/EN/RU in this baseline run.

## Why it matters

This is the first multilingual stronger baseline artifact set that is directly suitable for manual meaning-level evaluation sentence by sentence.

## Reuse notes

Use the same `review.jsonl` schema for prompt-family runs to enable aligned manual comparisons against this baseline without additional conversion tooling.
