---
note_type: sync_note
sync_id: sync_20260514_stss2_bounded_verification
date: 2026-05-14
title: "STSS-Test-2 bounded verification finalized"
track: cross-project
work_block_type: research
runs_created:
  - "run_20260514_stss2_bounded_final_rerun2"
artifacts_created:
  - "outputs/reproduction/2026-05-14-final-rerun2/stss_test_2/manifest.json"
issues_created:
  - ""
decisions_created:
  - ""
experiments_updated:
  - ""
roadmap_updates:
  - "docs/PHASE4_STABILIZATION.md timeout policy section added (1800s heavy cap)"
  - "docs/PROJECT_PLAN.md Phase 4 bounded timeout policy documented"
notion_sync_priority: high
---

## What was done

Completed a full bounded STSS-Test-2 orchestrator run with live prompting, enforced heavy-step timeout caps, and captured final step outcomes in a single manifest.

## Main result

Prompting and verification steps succeeded (5/7 total), while heavy GPU steps remained unresolved:

- `ssc_baseline` failed by bounded timeout (`exit_code=124` at 1800s).
- `llama_baseline` failed with runtime shape mismatch (`exit_code=1`).

## What needs syncing to Notion

- Run note: `run_20260514_stss2_bounded_final_rerun2`
- Reproduction artifact: `outputs/reproduction/2026-05-14-final-rerun2/stss_test_2/manifest.json`
- Timeout policy updates in Phase 4 docs

## What remains unresolved

- SSC heavy step needs either a higher budget or narrower bounded objective for completion.
- LLaMA heavy step needs upstream/runtime bug triage for fused loss batch-shape mismatch.

## Next step

Treat this bounded manifest as the current reproducibility baseline and run targeted follow-up troubleshooting for SSC and LLaMA as separate, explicitly scoped runs.
