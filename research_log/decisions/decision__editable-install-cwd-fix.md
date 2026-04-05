---
note_type: decision
decision_id: decision_editable_install_cwd_fix
title: "Fix working-directory sensitivity via editable pip install"
date: 2026-04-05
decision_type: architecture
status: active
decision_statement: "Add pyproject.toml to upstream clone and install in editable mode to eliminate CWD dependency for imports"
reasoning_summary: "Upstream code has no package definition; all imports fail unless CWD is the clone root. A thin pyproject.toml with pip install -e allows imports from any directory."
related_experiments: []
related_runs:
  - "run_20260405_ssc_baseline_bert"
  - "run_20260405_prompting_baseline_qwen3"
  - "run_20260405_llama_dryrun_8b"
related_artifacts: []
evidence_strength: "strong"
follow_up_action: "Verify all scripts still work after the change"
notion_targets:
  decisions: true
  runs: true
  artifacts: false
  experiments: false
---

## Context

The upstream `scene-segmentation` repo has no `setup.py` or `pyproject.toml`. Python imports (`from ssc.model import ...`, `from utils import ...`) only work when the CWD is the clone root. This was documented in `issue__config__working-directory-sensitivity.md`.

## Evidence

- All three pipelines (SSC, prompting, LLaMA) required `cd upstream/scene-segmentation` or `PYTHONPATH` manipulation
- The wrapper project's `src/` scripts couldn't import upstream modules without path hacks
- Tested: after `pip install -e .`, imports work from `/tmp` (arbitrary directory)

## Decision

Created `upstream/scene-segmentation/pyproject.toml` with:
- `setuptools` build backend
- Package discovery for `ssc`, `prompting`, `utils`, `llama`
- Installed via `pip install -e .` in both `.venv` and `.venv-gpu`

## Why this is the current standard

- Eliminates fragile CWD requirements
- Works with both virtual environments
- Editable install means code changes are immediately reflected
- Minimal modification to upstream (one new file, no code changes)

## Consequences

- The `pyproject.toml` is a local addition not present in the original upstream repo
- If upstream is re-cloned, the pyproject.toml must be recreated or git-ignored
- The `utils` package name is generic and could conflict with other packages (not an issue in isolated venvs)

## Follow-up

Update `issue__config__working-directory-sensitivity.md` status to resolved.
