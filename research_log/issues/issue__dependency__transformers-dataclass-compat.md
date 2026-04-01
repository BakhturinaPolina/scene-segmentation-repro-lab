---
note_type: issue
issue_id: issue_transformers_dataclass_compat
title: "transformers 5.x breaks SSCModelConfig dataclass field ordering"
date_opened: 2026-03-31
category: dependency
severity: high
status: resolved
first_seen_in_run: "run_20260331_post_dep_install_imports"
environment: "scene-seg-basic (.venv)"
track: ssc
probable_cause: "transformers>=5.0 auto-converts PretrainedConfig subclasses to dataclasses, breaking upstream field ordering in SSCModelConfig"
attempted_fixes:
  - "Installed upstream requirements.txt — did not resolve (transformers stayed at 5.4.0)"
  - "Pinned transformers==4.46.3 in requirements-basic.txt — resolved"
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

`TypeError: non-default argument 'embedding_model_name' follows default argument` during `import ssc.model`.

## Context

The upstream `ssc/model.py` defines `SSCModelConfig(PretrainedConfig)` with a field ordering that works under transformers 4.x but fails under 5.x because 5.x auto-applies `@dataclass` semantics to `PretrainedConfig` subclasses.

## Evidence

- Error appeared in run `run_20260331_post_dep_install_imports` with `transformers==5.4.0`
- Error persisted in run `run_20260331_strict_upstream_install`
- Error resolved in run `run_20260331_cpu_pinned_final` with `transformers==4.46.3`

## Attempted fixes

1. Strict install from upstream `requirements.txt` — did not help (upstream does not pin transformers)
2. Pin `transformers==4.46.3` — resolved

## Current best understanding

This is a known breaking change in transformers 5.x. The upstream code was written for transformers 4.x. Pinning 4.46.3 is the minimal fix without modifying upstream code.

## Next fix to try

If transformers must be upgraded in the future, the upstream `SSCModelConfig` field ordering needs to be refactored to comply with dataclass rules (defaults after non-defaults).
