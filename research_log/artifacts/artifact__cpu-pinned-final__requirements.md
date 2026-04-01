---
note_type: artifact
artifact_id: art_cpu_pinned_requirements
title: "Pinned CPU dependency set (requirements-basic.txt)"
date: 2026-03-31
artifact_type: log
produced_by_run: "run_20260331_cpu_pinned_final"
track: cross-project
path: "requirements-basic.txt"
url: ""
description: "The resolved, pinned dependency file that produces passing imports for ssc.model and prompting.classify on CPU"
report_worthy: false
figure_or_table_candidate: ""
related_experiment: ""
related_task: ""
notion_targets:
  artifacts: true
  runs: true
  decisions: true
---

## What this artifact is

A pip requirements file with explicit version pins and a CPU-only PyTorch wheel index. This is the file that governs `.venv`.

## What it shows

The minimum dependency set that resolves all three compatibility issues discovered during Phase 2-3 smoke testing:
- `torch==2.5.1+cpu` + `torchvision==0.20.1+cpu` (resolves nms mismatch)
- `transformers==4.46.3` (resolves dataclass error)
- `langchain==0.1.9` (resolves adapters import)

## Why it matters

This is the evidence behind `decision_cpu_env_version_pins`. Without these exact pins, the CPU smoke test environment fails.

## Reuse notes

Install with `pip install -r requirements-basic.txt` inside `.venv`. Do not modify without re-running the full smoke test suite.
