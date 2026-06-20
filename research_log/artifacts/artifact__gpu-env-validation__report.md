---
note_type: artifact
artifact_id: art_gpu_env_report
title: "GPU environment report (nvidia-smi + toolkit snapshot)"
date: 2026-03-31
artifact_type: log
produced_by_run: "run_20260331_gpu_env_validation"
track: cross-project
path: "outputs/artifacts/logs/gpu_env_report.txt"
url: ""
description: "Full nvidia-smi output, CUDA toolkit version, Python toolchain, and torch GPU detection results captured during GPU environment setup"
report_worthy: false
figure_or_table_candidate: ""
related_experiment: ""
related_task: ""
notion_targets:
  artifacts: true
  runs: true
  decisions: false
---

## What this artifact is

A text file capturing the complete GPU/CUDA/Python environment state at setup time. Contains nvidia-smi output, nvcc version, Python/pip versions, and torch GPU detection results.

## What it shows

- GPU: NVIDIA GeForce RTX 2070 with Max-Q Design (8 GB VRAM, compute cap 7.5)
- Driver: 580.126.09, CUDA driver 13.0
- CUDA toolkit (nvcc): 12.0.140
- Python 3.12.3, torch 2.5.1+cpu (captured from `.venv`, not `.venv-gpu`)

## Why it matters

Provides a reproducibility anchor for hardware and driver state. If future runs produce unexpected GPU behavior, this snapshot establishes the known-good baseline.

## Reuse notes

This file is git-ignored. If the environment changes significantly, regenerate with `nvidia-smi` and related commands and save a new snapshot.
