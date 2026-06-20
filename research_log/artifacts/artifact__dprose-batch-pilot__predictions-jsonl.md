---
note_type: artifact
artifact_id: art_dprose_batch_pilot_predictions
title: "dProse batch pilot predictions (989 sentences)"
date: 2026-06-19
artifact_type: predictions
produced_by_run: "run_20260619_dprose_batch_pilot"
track: prompting
path: "outputs/runs/dprose_batch/2026-06-19-dprose-batch-pilot/predictions.jsonl"
url: ""
description: "Per-sentence BORDER/NOBORDER predictions from Gemini 2.5 Pro batch pilot on 3 dProse files (989 sentences)."
report_worthy: true
figure_or_table_candidate: "Table"
related_experiment: ""
related_task: "dProse full-corpus scene segmentation"
notion_targets:
  artifacts: true
  runs: true
  decisions: false
---

## What this artifact is

JSONL with one record per sentence: source file, index, text, parsed label, raw model JSON, token usage, parse status.

## What it shows

- 871/989 successfully parsed predictions (88.07%)
- Aggregate labels: 697 NOBORDER, 174 BORDER
- Companion summary: `outputs/runs/dprose_batch/2026-06-19-dprose-batch-pilot/pilot_summary.json`

## Why it matters

First dProse prediction artifact using direct Gemini Batch API (50% pricing). Establishes cost/token baselines for scaling to 120k sentences.

## Reuse notes

Join on `source_file` + `sentence_index` to map back to `data/raw/dprose/*.csv`. Re-run failed keys after increasing `max_output_tokens`.
