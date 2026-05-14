---
note_type: sync_note
sync_id: sync_20260514_phase4_live_prompting_smokes
date: 2026-05-14
title: "Phase 4 live prompting smoke tests"
track: prompting
work_block_type: research
runs_created:
  - "run_20260514_phase4_prompting_baseline_live"
  - "run_20260514_phase4_prompting_stratified_live"
  - "run_20260514_phase4_phase_a_family_a_live"
artifacts_created:
  - ""
issues_created:
  - "issue_openrouter_free_model_deprecated"
decisions_created:
  - ""
experiments_updated:
  - ""
roadmap_updates:
  - "docs/PHASE4_STABILIZATION.md commands updated with explicit model flag"
notion_sync_priority: high
---

## What was done

Executed live API smoke runs for Phase 4 prompting workflows and recorded run notes plus a provider deprecation issue.

## Main result

Stratified smoke run succeeded with full reproducibility artifacts; baseline smoke failed due to deprecated default free model slug.

## What needs syncing to Notion

- Two new prompting run notes
- One new API issue note
- Phase 4 runbook update reflecting the model-slug workaround

## What remains unresolved

- Baseline script default model still points to deprecated `:free` suffix.

## Next step

Patch default model slug to `qwen/qwen3.6-plus`, rerun baseline smoke, then close or downgrade the issue note if validated.
