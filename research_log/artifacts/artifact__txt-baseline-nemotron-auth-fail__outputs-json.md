---
note_type: artifact
artifact_id: art_txt_baseline_nemotron_auth_fail_outputs_json
title: "TXT baseline smoke outputs (Nemotron free, auth failure)"
date: 2026-05-15
artifact_type: predictions
produced_by_run: "run_20260515_txt_prompting_baseline_nemotron_auth_fail"
track: prompting
path: "outputs/prompting/2026-05-15/baseline_txt_nemotron_smoke/"
url: ""
description: "Reproducibility outputs from TXT baseline smoke run, including command/config/results/summary with API auth failure diagnostics."
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

A smoke-run output directory containing:
- `command.txt`
- `config.json`
- `results.json`
- `summary.json`

## What it shows

- TXT inference-only mode is active (`input_mode=txt`, `evaluation_mode=inference_only`).
- Three sentences were processed from the selected raw TXT file.
- All API requests returned `401 Missing Authentication header`, yielding parse failures for every sentence.

## Why it matters

This confirms the new TXT pipeline wiring and artifact generation are functional, while clearly isolating the remaining blocker to OpenRouter credentials rather than code execution.

## Reuse notes

After setting a valid `OPENROUTER_API_KEY`, rerun with the same output folder pattern and compare `summary.json` fields (`parse_failure_rate`, `avg_output_chars`, latency) to confirm transition from auth-failure to live responses.
