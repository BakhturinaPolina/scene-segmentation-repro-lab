---
note_type: issue
issue_id: issue_llama_vram_insufficient
title: "LLaMA 8B 4-bit OOMs on RTX 2070 Max-Q (8 GB) with batch_size=20"
date_opened: 2026-04-05
category: CUDA
severity: high
status: open
first_seen_in_run: "run_20260405_llama_dryrun_8b"
environment: ".venv-gpu (unsloth, torch 2.10.0+cu128)"
track: llama
probable_cause: "Model weights use 5.5 GB of 7.6 GB; batch_size=20 exhausts remaining 2.1 GB"
attempted_fixes:
  - "None yet — dry run was expected to potentially OOM"
blocking: true
related_runs:
  - "run_20260405_llama_dryrun_8b"
notion_targets:
  issues: true
  runs: true
  roadmap: true
---

## Symptom

`torch.OutOfMemoryError: CUDA out of memory. Tried to allocate 138.00 MiB. GPU 0 has a total capacity of 7.60 GiB of which 124.50 MiB is free.`

## Context

Running `unsloth/llama-3-8b-bnb-4bit` with LoRA (r=16) on RTX 2070 Max-Q (8 GB). Model loaded at 5.477 GB, leaving ~2.1 GB. Training with batch_size=20 and context_size=256 exceeded available VRAM on the first forward pass.

## Evidence

- Model load: 5.477 GB reserved (72% of 7.603 GB)
- OOM during first training step at swiglu kernel (138 MB allocation failed)
- GPU: NVIDIA GeForce RTX 2070 with Max-Q Design

## Attempted fixes

None yet.

## Current best understanding

The 8B model in 4-bit quantization is too large for comfortable training on 8 GB VRAM. Options:
1. batch_size=1 + gradient_accumulation_steps=20 (may fit but very slow)
2. Reduce context_size further (currently 256)
3. Use a smaller model (e.g., TinyLlama, Phi-3-mini)
4. Cloud GPU (T4, A100)

## Next fix to try

1. Try batch_size=1 + gradient_accumulation_steps=20 + context_size=128
2. If still OOM, try a smaller model or switch to cloud GPU
