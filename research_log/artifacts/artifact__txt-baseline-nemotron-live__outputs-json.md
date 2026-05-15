---
note_type: artifact
artifact_id: art_txt_baseline_nemotron_live_outputs_json
title: "TXT baseline smoke outputs (Nemotron free, live run)"
date: 2026-05-15
artifact_type: predictions
produced_by_run: "run_20260515_txt_prompting_baseline_nemotron_live"
track: prompting
path: "outputs/prompting/2026-05-15/baseline_txt_nemotron_smoke_live/"
url: ""
description: "Live authenticated TXT baseline smoke outputs with command/config/results/summary."
report_worthy: false
figure_or_table_candidate: "neither"
related_experiment: ""
related_task: "TXT prompting baseline smoke validation"
notion_targets:
  artifacts: true
  runs: true
  decisions: false
---

## What this artifact is

A baseline smoke output directory containing:
- `command.txt`
- `config.json`
- `results.json`
- `summary.json`

## What it shows

- `input_mode=txt` and `evaluation_mode=inference_only` are active.
- Three sentences were processed with live OpenRouter responses.
- Parse quality for this smoke subset is stable (`parse_failure_rate=0.0`).

## Why it matters

This artifact demonstrates that the TXT baseline path is no longer blocked by authentication and is ready for next-stage prompt-family experimentation.

## Reuse notes

Reuse this output layout and CLI settings as the reference smoke configuration before scaling to larger TXT subsets or adding prompt-family variations.
