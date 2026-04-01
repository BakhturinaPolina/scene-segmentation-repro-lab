---
note_type: issue
issue_id: issue_langchain_adapters_missing
title: "langchain 1.x removed langchain.adapters module used by prompting code"
date_opened: 2026-03-31
category: dependency
severity: high
status: resolved
first_seen_in_run: "run_20260331_post_dep_install_imports"
environment: "scene-seg-basic (.venv)"
track: prompting
probable_cause: "langchain>=0.2 restructured module layout; langchain.adapters no longer exists"
attempted_fixes:
  - "Installed upstream requirements.txt — did not resolve (langchain stayed at 1.2.13)"
  - "Pinned langchain==0.1.9 in requirements-basic.txt — resolved"
blocking: true
related_runs:
  - "run_20260331_post_dep_install_imports"
  - "run_20260331_strict_upstream_install"
  - "run_20260331_cpu_pinned_final"
notion_targets:
  issues: true
  runs: true
  roadmap: false
---

## Symptom

`ModuleNotFoundError: No module named 'langchain.adapters'` during `import prompting.classify`.

## Context

The upstream `prompting/classify.py` imports from `langchain.adapters`, which existed in langchain 0.1.x but was removed in the 0.2+ restructuring (split into langchain-core, langchain-community, etc.).

## Evidence

- Error appeared in run `run_20260331_post_dep_install_imports` with `langchain==1.2.13`
- Error persisted in run `run_20260331_strict_upstream_install`
- Error resolved in run `run_20260331_cpu_pinned_final` with `langchain==0.1.9`

## Attempted fixes

1. Strict install from upstream `requirements.txt` — did not help
2. Pin `langchain==0.1.9` — resolved

## Current best understanding

The upstream prompting code was written for langchain 0.1.x. The 0.1.9 pin is the minimal compatible version.

## Next fix to try

If langchain must be upgraded, the upstream prompting code needs to be refactored to use the new module layout (langchain-core, langchain-community).
