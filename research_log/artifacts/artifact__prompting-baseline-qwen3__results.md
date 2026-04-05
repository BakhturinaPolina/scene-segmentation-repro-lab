---
note_type: artifact
artifact_id: art_prompting_baseline_qwen3_results
title: "Prompting baseline results (qwen3.6-plus, 20 sentences)"
date: 2026-04-05
artifact_type: predictions
produced_by_run: "run_20260405_prompting_baseline_qwen3"
track: prompting
path: "outputs/prompting/2026-04-05/baseline_qwen3/"
url: ""
description: "Per-sentence predictions, reasons, and summary from the OpenRouter prompting baseline"
report_worthy: false
figure_or_table_candidate: "neither"
related_experiment: ""
related_task: "Phase 3.2"
notion_targets:
  artifacts: true
  runs: true
  decisions: false
---

## What this artifact is

Two JSON files:
- `results.json`: per-sentence labels (True/False), model reasons, ground truth, and sentence text for 20 sentences
- `summary.json`: aggregate metrics (accuracy, border counts, runtime)

## What it shows

- 20/20 sentences correctly classified (100% accuracy)
- 1 true border, 19 non-borders
- Model provides German-language reasoning for each classification

## Why it matters

Validates the prompting pipeline works with OpenRouter and qwen/qwen3.6-plus:free. The sample is too small for statistical significance but proves end-to-end functionality.

## Reuse notes

The `results.json` includes the model's reasoning text which could be useful for qualitative analysis of LLM scene understanding.
