---
note_type: issue
issue_id: issue_working_directory_sensitivity
title: "All upstream imports fail unless cwd is clone root"
date_opened: 2026-03-31
category: config
severity: medium
status: open
first_seen_in_run: "run_20260331_initial_import_tests"
environment: "all"
track: cross-project
probable_cause: "Upstream code uses relative imports and expects ssc/, prompting/, utils/ to be discoverable from cwd"
attempted_fixes:
  - "Always cd to upstream/scene-segmentation before running commands"
  - "Alternative: export PYTHONPATH to include clone root"
blocking: false
related_runs:
  - "run_20260331_initial_import_tests"
notion_targets:
  issues: true
  runs: false
  roadmap: false
---

## Symptom

`ModuleNotFoundError: No module named 'ssc'` when running from the wrapper root (`scene-segmentation-research/`) instead of the clone root (`upstream/scene-segmentation/`).

## Context

The upstream repository has no `setup.py` or `pyproject.toml` — it relies on being the working directory for Python to discover `ssc/`, `prompting/`, and `utils/` as packages.

## Evidence

- Running `python -c "import ssc.model"` from wrapper root fails
- Same command from clone root succeeds (after dependency fixes)
- Documented in docs/PHASE2_PHASE3_NOTES.md and docs/ENVIRONMENT_SETUP.md

## Attempted fixes

1. Always `cd upstream/scene-segmentation` before running — works but easy to forget
2. Set `PYTHONPATH` explicitly — works but must be maintained per-session

## Current best understanding

This is an architectural constraint of the upstream code, not a bug. The project has no installable package definition.

## Next fix to try

Consider creating a thin `pyproject.toml` or `setup.py` in the upstream clone to make the packages installable in editable mode (`pip install -e .`). This would eliminate the cwd dependency. However, this modifies the upstream code and should be a deliberate decision.
