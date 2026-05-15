---
note_type: sync_note
sync_id: sync_20260515_txt_baseline_live_success
date: 2026-05-15
title: "TXT baseline live smoke succeeded"
track: cross-project
work_block_type: research
runs_created:
  - "run_20260515_txt_prompting_baseline_nemotron_live"
artifacts_created:
  - "art_txt_baseline_nemotron_live_outputs_json"
issues_created:
  - ""
decisions_created:
  - ""
experiments_updated:
  - ""
roadmap_updates:
  - "Validated OpenRouter-authenticated TXT baseline smoke path for prompting."
notion_sync_priority: high
---

## What was done

Executed authenticated TXT-mode baseline smoke with Nemotron free and captured reproducibility outputs plus run/artifact notes.

## Main result

Live OpenRouter inference succeeded for all sampled sentences with zero parse failures.

## What needs syncing to Notion

- Successful run record for TXT baseline live smoke.
- Artifact directory references with summary/metrics for the validated smoke command.

## What remains unresolved

No unresolved runtime blockers for TXT smoke; broader prompt-family experiment runs are still pending.

## Next step

Start Phase A prompt-family experiments using the now-validated TXT baseline runtime setup.
