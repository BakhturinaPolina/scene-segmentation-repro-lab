---
note_type: artifact
artifact_id: art_excel_controlled_postprocessing_comparison_table_20260530
title: "Excel controlled sweep comparison table (none/min_scene_len_3/min_scene_len_5)"
date: 2026-05-30
artifact_type: table
produced_by_run: "run_20260530_excel_controlled_postprocessing_sweep"
track: prompting
path: "outputs/review/excel_controlled_sweep/comparison/normalization_what_if.csv"
url: ""
description: "One-factor comparison table with exact and tolerant metrics for three post-processing rules on the same fresh full-eval predictions."
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

CSV/JSON outputs from `scripts/normalization_what_if.py` with scenarios constrained to:
- `none`
- `min_scene_len_3`
- `min_scene_len_5`

## What it shows

Aggregate rows:
- `none`: exact F1 `0.0993`, tol3 F1 `0.3604`, tol5 F1 `0.4242`
- `min_scene_len_3`: exact F1 `0.0909`, tol3 F1 `0.5063`, tol5 F1 `0.5676`
- `min_scene_len_5`: exact F1 `0.0896`, tol3 F1 `0.5373`, tol5 F1 `0.6667`

## Why it matters

It cleanly isolates post-processing as the single variable and quantifies the exact-vs-tolerant tradeoff needed for policy selection on Excel-manifest datasets.

## Reuse notes

- Keep model/prompt/decode/full_eval fixed when adding future thresholds.
- Append new scenario rows rather than replacing historical rows to preserve comparability.
