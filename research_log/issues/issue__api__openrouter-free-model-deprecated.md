---
note_type: issue
issue_id: issue_openrouter_free_model_deprecated
title: "OpenRouter free model slug returns 404"
date_opened: 2026-05-14
category: api
severity: medium
status: resolved
first_seen_in_run: "run_20260514_phase4_prompting_baseline_live"
environment: ".venv"
track: prompting
probable_cause: "Model slug `qwen/qwen3.6-plus:free` has been deprecated by provider."
attempted_fixes:
  - "Reran smoke test with `--model qwen/qwen3.6-plus`."
  - "Removed `qwen/qwen3.6-plus:free` from active defaults."
  - "Pinned baseline defaults to `nvidia/nemotron-3-super-120b-a12b:free`."
blocking: false
related_runs:
  - "run_20260514_phase4_prompting_baseline_live"
  - "run_20260514_phase4_prompting_stratified_live"
notion_targets:
  issues: true
  runs: true
  roadmap: true
---

## Symptom

Prompting baseline run produced repeated API 404 errors and no parsable model output.

## Context

The legacy baseline script default model was `qwen/qwen3.6-plus:free`.

## Evidence

Provider error message in run output indicated free model deprecation. Runtime defaults were updated to a pinned available free model (`nvidia/nemotron-3-super-120b-a12b:free`) for STSS-Test-2 reproducibility.

## Attempted fixes

- Executed stratified smoke with explicit model override: `--model qwen/qwen3.6-plus`.
- Removed deprecated slug from active wrapper defaults.
- Switched baseline default to `nvidia/nemotron-3-super-120b-a12b:free`.

## Current best understanding

The deprecated slug was the root cause. Active defaults now use a pinned OpenRouter free model and no longer depend on the removed route.

## Next fix to try

None required for this issue. Keep a periodic model-availability check in future sync notes because free-tier inventory can change.
