---
note_type: artifact
artifact_id: art_dprose_batch_pilot_2048_predictions
title: "dProse batch pilot predictions @ 2048 tokens (989 sentences)"
date: 2026-06-20
artifact_type: predictions
produced_by_run: "run_20260620_dprose_batch_pilot_2048"
track: prompting
path: "outputs/runs/dprose_batch/2026-06-20-dprose-batch-pilot-2048/predictions.jsonl"
url: ""
description: "Per-sentence BORDER/NOBORDER predictions from Gemini 2.5 Pro batch pilot rerun at max_output_tokens=2048 (989 sentences, 3 files)."
report_worthy: true
figure_or_table_candidate: "Table"
related_experiment: "run_20260619_dprose_batch_pilot"
related_task: "dProse full-corpus scene segmentation"
notion_targets:
  artifacts: true
  runs: true
  decisions: false
---

## What this artifact is

JSONL with one record per sentence: source file, index, text, parsed label, raw model JSON, token usage, parse status. Produced by full pilot rerun at max_output_tokens=2048.

## What it shows

- 988/989 successfully parsed predictions (99.90%)
- Aggregate labels: 753 NOBORDER, 235 BORDER
- 1 residual truncation failure: `dprose_100:22` (thought_tokens=1973 > 2048 cap)
- Companion summary: `outputs/runs/dprose_batch/2026-06-20-dprose-batch-pilot-2048/pilot_summary.json`

## Why it matters

Validates max_output_tokens=2048 as the production config for dProse full-corpus batch run. Replaces the partial 1024-token pilot artifact (88% parse rate) as the authoritative pilot predictions.

## Reuse notes

Join on `source_file` + `sentence_index` to map back to `data/raw/dprose/*.csv`. For the single failed key, re-run with max_output_tokens=4096 or cap thinking_budget.
