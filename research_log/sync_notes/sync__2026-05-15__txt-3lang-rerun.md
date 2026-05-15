---
note_type: sync_note
sync_id: sync_20260515_txt_3lang_rerun
date: 2026-05-15
title: "TXT 3-language smoke rerun completed"
track: cross-project
work_block_type: research
runs_created:
  - "run_20260515_txt_3lang_prompting_baseline_nemotron_live"
artifacts_created:
  - "art_txt_3lang_nemotron_live_outputs_json"
issues_created:
  - ""
decisions_created:
  - ""
experiments_updated:
  - ""
roadmap_updates:
  - "Completed DE/EN/RU TXT smoke reruns with separate output folders and live API responses."
notion_sync_priority: high
---

## What was done

Executed three TXT smoke runs (DE/EN/RU) using the same Nemotron free setup and saved outputs in three new separate prompting folders.

## Main result

All runs succeeded with zero parse failures and complete reproducibility artifacts.

## What needs syncing to Notion

- New run note for the three-language rerun.
- New artifact note referencing the three per-language output directories.

## What remains unresolved

Only smoke-scale (3 sentences/file) was run; broader baseline and prompt-family sweeps remain.

## Next step

Run 20-sentence per-language baseline or start prompt-family A/B sweep on the same three-folder structure.
