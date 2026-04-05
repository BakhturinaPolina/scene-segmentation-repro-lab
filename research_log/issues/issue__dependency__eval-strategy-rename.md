---
note_type: issue
issue_id: issue_eval_strategy_rename
title: "TrainingArguments.evaluation_strategy renamed to eval_strategy in transformers 4.52"
date_opened: 2026-04-05
category: dependency
severity: medium
status: resolved
first_seen_in_run: "run_20260405_ssc_baseline_bert"
environment: ".venv-gpu (transformers 4.52.4)"
track: ssc
probable_cause: "Breaking API change in transformers >= 4.50"
attempted_fixes:
  - "Renamed evaluation_strategy to eval_strategy in ssc/train.py (2 occurrences)"
blocking: false
related_runs:
  - "run_20260405_ssc_baseline_bert"
notion_targets:
  issues: true
  runs: true
  roadmap: false
---

## Symptom

`TypeError: TrainingArguments.__init__() got an unexpected keyword argument 'evaluation_strategy'`

## Context

The upstream `ssc/train.py` uses `evaluation_strategy="epoch"` which was deprecated and removed in `transformers >= 4.50`. The GPU environment has `transformers==4.52.4`.

## Evidence

Two occurrences in `ssc/train.py` (lines 133 and 154 in original code).

## Attempted fixes

1. Replaced `evaluation_strategy` with `eval_strategy` in both `TrainingArguments` blocks — **resolved**.

## Current best understanding

Standard deprecation cycle. The fix is straightforward.

## Next fix to try

N/A — resolved.
