---
note_type: artifact
artifact_id: art_dprose_B_vs_L_spot_comparison
title: "dProse Family B (production) vs Family L spot-rerun comparison"
date: 2026-07-22
artifact_type: comparison
produced_by_run: "run_20260722_dprose_familyL_spot_rerun"
track: prompting
path: "outputs/runs/dprose_batch/2026-07-22-dprose-familyL-spot-rerun/B_vs_L_comparison.json"
url: ""
description: "Per-book border-rate / consecutive-run / L∩B agreement for four spot-check dProse texts under production B vs Family L."
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

JSON comparison of production Family B labels vs a Family L Gemini Batch re-run
on `dprose_52`, `dprose_119`, `dprose_137`, `dprose_100`.

## What it shows

BORDER rate drops −7.0 to −11.4 pp on every text; aggregate borders 234 → 153.
L is mostly a subset of B (only_L ≤ 5 per book). Consecutive montage/structural
runs shrink only modestly.

## Why it matters

Final-Remarks evidence that the Excel-gold FP-reduction from L transfers to
production dProse texts under the same batch config, with the caveat that
post-process merges are still needed for dense consecutive-BORDER clusters.

## Reuse notes

Regenerate with:

```bash
.venv/bin/python scripts/evaluation/compare_dprose_B_vs_L.py \
  --l_predictions outputs/runs/dprose_batch/2026-07-22-dprose-familyL-spot-rerun/predictions.jsonl \
  --out outputs/runs/dprose_batch/2026-07-22-dprose-familyL-spot-rerun/B_vs_L_comparison.json
```
