---
note_type: artifact
artifact_id: art_txt_3lang_nemotron_live_outputs_json
title: "TXT baseline smoke outputs for DE/EN/RU folders"
date: 2026-05-15
artifact_type: predictions
produced_by_run: "run_20260515_txt_3lang_prompting_baseline_nemotron_live"
track: prompting
path: "outputs/prompting/2026-05-15/"
url: ""
description: "Three separate output folders (DE/EN/RU) from authenticated TXT baseline smoke reruns."
report_worthy: false
figure_or_table_candidate: "neither"
related_experiment: ""
related_task: "Three-language TXT smoke rerun"
notion_targets:
  artifacts: true
  runs: true
  decisions: false
---

## What this artifact is

Three language-specific output folders:
- `outputs/prompting/2026-05-15/baseline_txt_nemotron_smoke_de`
- `outputs/prompting/2026-05-15/baseline_txt_nemotron_smoke_en`
- `outputs/prompting/2026-05-15/baseline_txt_nemotron_smoke_ru`

Each folder includes `command.txt`, `config.json`, `results.json`, `summary.json`.

## What it shows

- Authenticated OpenRouter inference succeeded for all three files.
- Parse failures are zero in all runs.
- Latency differs by language/input chunk characteristics (RU highest in this smoke subset).

## Why it matters

Confirms multilingual TXT smoke reproducibility with clean folder separation, which is suitable for next experiment stages and easier per-language comparison.

## Reuse notes

Use the same `baseline_txt_nemotron_smoke_<lang>` naming for future reruns and prompt-family sweeps to preserve clean comparison structure.
