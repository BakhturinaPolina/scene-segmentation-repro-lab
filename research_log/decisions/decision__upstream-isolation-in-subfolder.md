---
note_type: decision
decision_id: decision_upstream_isolation
title: "Clone upstream repository into upstream/ subdirectory"
date: 2026-03-31
decision_type: architecture
status: active
decision_statement: "Clone LSX-UniWue/scene-segmentation into upstream/scene-segmentation/ to isolate upstream code from wrapper files"
reasoning_summary: "Keeps planning files, environments, and research logs at the wrapper root while preserving the upstream repository structure intact"
related_experiments: []
related_runs:
  - "run_20260331_initial_import_tests"
related_artifacts: []
evidence_strength: "moderate"
follow_up_action: "Maintain upstream/ as read-only reference; any modifications should be discussed as a separate decision"
notion_targets:
  decisions: true
  runs: false
  artifacts: false
  experiments: false
---

## Context

The project needs to test and extend `LSX-UniWue/scene-segmentation` while maintaining its own planning documents, research logs, dependency files, and environment configurations.

## Evidence

- Mixing upstream code and wrapper files in the same root would create naming conflicts (`requirements.txt`, `README.md`, `data/`)
- The upstream repo has no installable package definition, so it must be used as a working directory
- Keeping it isolated allows `git` tracking of wrapper files separately from upstream code

## Decision

Clone the upstream repository to `upstream/scene-segmentation/`. The wrapper root remains the primary project directory for all research infrastructure.

## Why this is the current standard

This is the simplest separation that avoids file conflicts and allows independent version control of wrapper and upstream code.

## Consequences

- Commands that use upstream code must either `cd upstream/scene-segmentation` or set `PYTHONPATH`
- The `upstream/` directory is git-ignored to avoid tracking a nested repository
- Updates to upstream must be pulled explicitly

## Follow-up

If upstream code needs modification, consider forking or creating a branch within the upstream clone, and document the change as a separate decision.
