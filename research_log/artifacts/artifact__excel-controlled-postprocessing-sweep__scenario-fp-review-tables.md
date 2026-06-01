---
note_type: artifact
artifact_id: art_excel_controlled_postprocessing_fp_tables_20260530
title: "Scenario FP review tables for Excel controlled sweep"
date: 2026-05-30
artifact_type: qualitative
produced_by_run: "run_20260530_excel_controlled_postprocessing_sweep"
track: prompting
path: "outputs/review/excel_controlled_sweep/"
url: ""
description: "Top false-positive review tables exported per post-processing scenario (`none`, `min_scene_len_3`, `min_scene_len_5`) with context, tags, and model reason fields."
report_worthy: true
figure_or_table_candidate: "Table"
related_experiment: "experiment__prompting__post-processing__excel-controlled-sweep"
related_task: "Controlled Excel post-processing experiment"
notion_targets:
  artifacts: true
  runs: true
  decisions: false
---

## What this artifact is

Per-scenario FP tables from `scripts/export_top_fp_review_table.py`:
- `outputs/review/excel_controlled_sweep/none/top_fp_review_table.csv`
- `outputs/review/excel_controlled_sweep/min_scene_len_3/top_fp_review_table.csv`
- `outputs/review/excel_controlled_sweep/min_scene_len_5/top_fp_review_table.csv`

Each table includes `top_k=10` rows per text (`gaensemagd`, `kleist`) with neighboring context and diagnostic tags.

## What it shows

- Which borderline or fragment-like FPs persist across stricter minimum-scene-length rules.
- Which FP clusters are removed as scene-gap constraints tighten.
- Confidence/diagnostic patterns among residual FPs under each scenario.

## Why it matters

The qualitative FP trace complements metric deltas and supports choosing a post-processing default based on error shape, not only aggregate scores.

## Reuse notes

- Re-run with identical `--top_k` when comparing new scenarios.
- Keep input review JSONLs fixed to preserve one-factor interpretation.
