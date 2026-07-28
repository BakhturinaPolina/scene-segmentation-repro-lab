---
note_type: artifact
artifact_id: art_gevatter_gemini_reasoning_on_summary
title: "Gevatter Gemini 2.5 Pro Family B summary metrics"
date: 2026-07-28
artifact_type: metrics
produced_by_run: "run_20260728_gevatter_gemini_reasoning_on"
track: prompting
path: "outputs/runs/prompting/2026-07-28-excel-gevatter-gemini-reasoning-on/full_google_gemini-2.5-pro_familyB_reasoning-on/summary.json"
url: ""
description: "Full-eval summary for Der Gevatter (32 sentences): exact F1 0.3636, relaxed tol3 F1 0.9091, 6 predicted vs 5 gold borders."
report_worthy: true
figure_or_table_candidate: "Table"
related_experiment: ""
related_task: "Automatic Scene Segmentation report — gold evaluation"
notion_targets:
  artifacts: true
  runs: true
  decisions: false
---

## What this artifact is

`summary.json` from the OpenRouter full-eval run of Gemini 2.5 Pro (reasoning on, Prompt Family B) on the Excel-derived *Der Gevatter* gold text.

## What it shows

| Metric | Value |
| ------ | ----- |
| Sentences classified | 32 / 32 |
| Gold borders | 5 |
| Predicted borders | 6 |
| Over-prediction ratio | 1.2 |
| Exact F1 (tol 0) | 0.3636 |
| Relaxed F1 (tol 3) | 0.9091 |
| Parse failure rate | 0.0 |
| Avg latency | 3.40 s |

Companion review file: `review_gevatter_sentences.jsonl` (per-sentence predictions + raw model responses). Terminal log: `logs/excel_gevatter/2026-07-28-gevatter-gemini-reasoning-on.log`.

## Why it matters

Adds a third close-reading gold text to the Excel evaluation set and confirms that the production Gemini setting recovers all gold borders within tol 3 on a short fairy tale, with only mild over-prediction.

## Reuse notes

- Reproducible via the command in `command.txt` in the same output directory, using `data/manifests/excel_prompting_gevatter.json`.
- Cache file `cache_gevatter_sentences.json` allows rescoring without new API calls.
- Three-text macro with May 2026 Gaensemagd+Kleist Gemini reasoning-on per-doc F1: exact 0.45 / relaxed 0.81.
