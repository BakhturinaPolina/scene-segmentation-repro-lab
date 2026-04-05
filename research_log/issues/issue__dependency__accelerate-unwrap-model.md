---
note_type: issue
issue_id: issue_accelerate_unwrap_model
title: "accelerate.unwrap_model() got unexpected kwarg keep_torch_compile"
date_opened: 2026-04-05
category: dependency
severity: medium
status: resolved
first_seen_in_run: "run_20260405_ssc_baseline_bert"
environment: ".venv-gpu (accelerate 0.34.2, transformers 4.52.4)"
track: ssc
probable_cause: "accelerate 0.34.2 incompatible with transformers 4.52.4"
attempted_fixes:
  - "pip install --upgrade accelerate (upgraded to latest compatible version)"
blocking: false
related_runs:
  - "run_20260405_ssc_baseline_bert"
notion_targets:
  issues: true
  runs: true
  roadmap: false
---

## Symptom

`TypeError: Accelerator.unwrap_model() got an unexpected keyword argument 'keep_torch_compile'`

## Context

Occurred during `trainer.train()` in the training loop. The `transformers` 4.52.4 trainer calls `accelerator.unwrap_model(keep_torch_compile=...)` which was not yet supported in `accelerate` 0.34.2.

## Evidence

Stack trace pointed to `transformers/trainer.py` calling `accelerate/accelerator.py`.

## Attempted fixes

1. `pip install --upgrade accelerate` — **resolved**. Upgraded to a version compatible with transformers 4.52.4.

## Current best understanding

Version mismatch between transformers and accelerate. Resolved by upgrading accelerate.

## Next fix to try

N/A — resolved.
