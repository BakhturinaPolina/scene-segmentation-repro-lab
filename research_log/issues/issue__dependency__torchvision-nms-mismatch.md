---
note_type: issue
issue_id: issue_torchvision_nms_mismatch
title: "torchvision::nms operator missing after strict upstream install"
date_opened: 2026-03-31
category: dependency
severity: high
status: resolved
first_seen_in_run: "run_20260331_strict_upstream_install"
environment: "scene-seg-basic (.venv)"
track: ssc
probable_cause: "pip resolver installed incompatible torch/torchvision version pair; compiled C++ ops for nms not available"
attempted_fixes:
  - "Pinned torch==2.5.1+cpu and torchvision==0.20.1+cpu — resolved"
blocking: true
related_runs:
  - "run_20260331_strict_upstream_install"
  - "run_20260331_cpu_pinned_final"
notion_targets:
  issues: true
  runs: true
  roadmap: false
---

## Symptom

`RuntimeError: operator torchvision::nms does not exist` during `import ssc.model`, cascading into `Could not import module 'PreTrainedModel'`.

## Context

After strict install from upstream `requirements.txt`, pip resolved a torch/torchvision combination where the compiled `nms` operator was missing. This broke the entire transformers import chain on the CPU environment.

## Evidence

- Error appeared only in run `run_20260331_strict_upstream_install`
- Not present in earlier runs (torch was 2.5.1+cpu with matching torchvision)
- Resolved in run `run_20260331_cpu_pinned_final` by explicitly pinning compatible pair

## Attempted fixes

1. Pin `torch==2.5.1+cpu` + `torchvision==0.20.1+cpu` from CPU wheel index — resolved

## Current best understanding

CPU-only torch/torchvision pairs must be pinned together from the same release. The generic pip resolver can pull mismatched versions when not constrained.

## Next fix to try

No further fix needed. The pinned pair is stable. If torch needs upgrading, find the matching torchvision from the PyTorch compatibility matrix.
