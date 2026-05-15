---
note_type: sync_note
sync_id: sync_20260515_txt_baseline_smoke_setup
date: 2026-05-15
title: "TXT baseline smoke path implemented and logged"
track: cross-project
work_block_type: setup
runs_created:
  - "run_20260515_txt_prompting_baseline_nemotron_auth_fail"
artifacts_created:
  - "art_txt_baseline_nemotron_auth_fail_outputs_json"
issues_created:
  - ""
decisions_created:
  - ""
experiments_updated:
  - ""
roadmap_updates:
  - "Added TXT input-mode baseline path and TXT manifest generation for prompting smoke checks."
notion_sync_priority: high
---

## What was done

Added a TXT manifest generator, generated `data/manifest_raw_txt.json`, implemented TXT inference-only mode in `src/run_prompting_baseline.py`, executed a TXT smoke run, and logged run/artifact notes.

## Main result

TXT-mode baseline executes end-to-end and writes reproducibility artifacts, but live OpenRouter inference is blocked by missing authentication in the active shell.

## What needs syncing to Notion

- New TXT baseline runtime capability and CLI flags.
- New smoke run evidence with explicit auth-failure diagnostics.
- New artifact path with command/config/results/summary references.

## What remains unresolved

Successful live API responses from `nvidia/nemotron-3-super-120b-a12b:free` have not been validated yet in this shell.

## Next step

Export a valid `OPENROUTER_API_KEY` and rerun the documented TXT smoke command to confirm non-error model outputs and parse success.
