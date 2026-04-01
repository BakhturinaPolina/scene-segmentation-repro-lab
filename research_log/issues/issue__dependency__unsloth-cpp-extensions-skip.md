---
note_type: issue
issue_id: issue_unsloth_cpp_extensions_skip
title: "Unsloth C++ extensions skipped due to torch < 2.11.0"
date_opened: 2026-03-31
category: dependency
severity: low
status: open
first_seen_in_run: "run_20260331_gpu_env_validation"
environment: "scene-seg-gpu (.venv-gpu)"
track: llama
probable_cause: "Unsloth compiled C++ extensions require torch >= 2.11.0; installed torch is 2.10.0+cu128"
attempted_fixes:
  - "None — accepted as non-blocking warning"
blocking: false
related_runs:
  - "run_20260331_gpu_env_validation"
notion_targets:
  issues: true
  runs: true
  roadmap: false
---

## Symptom

Warning during Unsloth import: `Skipping import of cpp extensions due to incompatible torch version. Please upgrade to torch >= 2.11.0`.

## Context

Unsloth 2026.3.18 ships compiled C++ extensions for performance optimization. These require torch >= 2.11.0. The current GPU environment has torch 2.10.0+cu128 (pulled by Unsloth's own installer).

## Evidence

- Warning appears on every `import unsloth` in `.venv-gpu`
- Training and inference still work via Python fallback paths
- Documented in docs/ENVIRONMENT_SETUP.md

## Attempted fixes

None. The warning is non-blocking and Unsloth itself installed this torch version.

## Current best understanding

This is a timing issue — Unsloth's pip package pulls torch 2.10.0 but the compiled extensions expect 2.11.0. Future Unsloth releases will likely resolve this. No action needed unless performance becomes a concern.

## Next fix to try

When torch 2.11.0+ wheels become available for cu128, upgrade torch in `.venv-gpu` and verify Unsloth C++ extensions load.
