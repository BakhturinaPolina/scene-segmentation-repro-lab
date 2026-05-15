---
note_type: sync_note
sync_id: sync_20260515_txt_3lang_30_baseline_review_ready
date: 2026-05-15
title: "3-language 30-sentence baseline completed with review outputs"
track: cross-project
work_block_type: research
runs_created:
  - "run_20260515_txt_3lang_30_prompting_baseline_nemotron_live"
artifacts_created:
  - "art_txt_3lang_30_nemotron_live_review_jsonl"
issues_created:
  - ""
decisions_created:
  - ""
experiments_updated:
  - "experiment_prompting_model_free_120b_comparison"
roadmap_updates:
  - "Added full-sentence review JSONL output format to baseline and stratified runners."
  - "Completed deterministic DE/EN/RU first-30-sentence baseline runs with comparable review artifacts."
notion_sync_priority: high
---

## What was done

Implemented review-output improvements (`review.jsonl` + `review_schema.json`, full sentence retention, compact decisions) in baseline and stratified runners, then executed DE/EN/RU baseline runs with first 30 sentences each.

## Main result

All three 30-sentence multilingual baseline runs completed successfully with zero parse failures and reviewer-ready outputs containing full sentence text plus compact/raw model reasoning.

## What needs syncing to Notion

- New baseline run note with multilingual metrics.
- New artifact note for review JSONL assets.
- Experiment context update indicating this baseline is now manually reviewable at sentence granularity.

## What remains unresolved

Prompt-family runs have not yet been regenerated with the same 30-sentence multilingual setup.

## Next step

Run prompt-family experiments (starting with family A) on the same DE/EN/RU first-30 setup and compare against baseline using the shared review schema.
