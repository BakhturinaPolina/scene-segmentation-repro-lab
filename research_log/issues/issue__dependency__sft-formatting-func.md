---
note_type: issue
issue_id: issue_sft_formatting_func
title: "SFTTrainer requires formatting_func instead of dataset_text_field"
date_opened: 2026-04-05
category: dependency
severity: medium
status: resolved
first_seen_in_run: "run_20260405_llama_dryrun_8b"
environment: ".venv-gpu (trl + unsloth)"
track: llama
probable_cause: "Breaking API change in newer Unsloth/TRL: dataset_text_field no longer accepted"
attempted_fixes:
  - "Replaced dataset_text_field with formatting_func that returns list of strings"
blocking: false
related_runs:
  - "run_20260405_llama_dryrun_8b"
notion_targets:
  issues: true
  runs: true
  roadmap: false
---

## Symptom

`RuntimeError: Unsloth: You must specify a formatting_func`

Followed by:

`ValueError: Unsloth: The formatting_func should return a list of processed strings.`

## Context

The upstream `llama/train_unsloth.py` uses `dataset_text_field="llama_sentences"` which was the old TRL API. Newer versions require a `formatting_func` callable.

## Evidence

Two-step fix needed:
1. First attempt with `return examples["llama_sentences"]` raised the ValueError (must return list)
2. Second attempt with `return list(texts)` and `isinstance` check resolved it

## Attempted fixes

1. Added `formatting_func` that returns `list(examples["llama_sentences"])` — **resolved**.

## Current best understanding

Standard API migration in TRL/Unsloth. The fix is straightforward.

## Next fix to try

N/A — resolved.
