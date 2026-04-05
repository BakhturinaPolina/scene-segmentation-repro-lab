---
note_type: run
run_id: run_20260405_llama_dryrun_8b
title: "LLaMA dry run: unsloth/llama-3-8b-bnb-4bit on RTX 2070 (OOM)"
date: 2026-04-05
track: llama
run_type: dry-run
status: partial
goal: "Verify the Unsloth fine-tuning pipeline loads and processes data; check VRAM requirements"
entrypoint: "python llama/train_unsloth.py"
command: >
  PYTHONPATH=$(pwd) python llama/train_unsloth.py
  --train_folder data/full/stss_test_2
  --test_folder data/full/stss_test_2
  --model_identifier ../../outputs/llama/2026-04-05/dryrun_8b
  --context_size 256 --random_seed 42
  --model unsloth/llama-3-8b-bnb-4bit
  --num_train_epochs 1 --cot_config no_cot
working_directory: "upstream/scene-segmentation"
git_commit: "8649e50"
environment: ".venv-gpu"
os: "Linux 6.17.0-111019-tuxedo"
hardware: "NVIDIA GeForce RTX 2070 Max-Q (8 GB)"
gpu: "NVIDIA GeForce RTX 2070 with Max-Q Design (7.603 GB usable)"
cuda_notes: "CUDA 12.0, torch 2.10.0+cu128"
api_provider: ""
api_model: ""
api_cost_estimate: ""
dataset_assets:
  - "data/full/stss_test_2 (2 XMI files)"
label_schema: "Coarse (True/False scene boundary)"
prompt_version: "no_cot"
model_name: "unsloth/llama-3-8b-bnb-4bit"
varying_factor: "none"
fixed_conditions:
  - "4-bit quantization, LoRA r=16, context_size=256"
  - "per_device_train_batch_size=20 (caused OOM)"
random_seed: "42"
output_dir: "outputs/llama/2026-04-05/dryrun_8b"
artifacts_expected:
  - "adapter_config.json"
  - "adapter_model.safetensors"
artifacts_produced: []
main_metric_name: ""
main_metric_value: ""
precision: ""
recall: ""
f1: ""
iou: ""
runtime: "893s (failed during first training step)"
failure_category: "CUDA OOM"
related_experiment: ""
related_issue: "issue_llama_vram_insufficient, issue_sft_formatting_func"
decision_relevance: true
notion_targets:
  roadmap: "Phase 3.3"
  runs: true
  experiments: ""
  artifacts: false
  issues: true
  decisions: true
---

## Objective

Check whether the Unsloth fine-tuning pipeline can run on the available hardware (RTX 2070 Max-Q, 8 GB). Not expected to produce a trained model.

## What was held constant

- unsloth/llama-3-8b-bnb-4bit, 4-bit quantization
- LoRA config: r=16, target_modules=[q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj]

## What changed

Two upstream code patches required:
1. `dataset_text_field` replaced with `formatting_func` for newer Unsloth/TRL API
2. `formatting_func` must return list of strings (not single string)

## Outcome

- Model loaded successfully: 5.477 GB of 7.603 GB reserved
- Data preprocessed: 10931 samples (all NOBORDER -- no border labels extracted)
- Downsampled to ~10% (~1093 samples)
- **OOM at first training step** with batch_size=20, context_size=256

## Interpretation

The 8B model in 4-bit uses 5.5 GB, leaving only ~2.1 GB for activations and gradients. Training with batch_size=20 is impossible. batch_size=1 with gradient_accumulation_steps=20 might work but would be very slow.

The data issue (0 border labels) also needs investigation -- the `xmi_to_llama_samples` function may not correctly extract borders from these XMI files, or the files genuinely contain only non-scene annotations.

## Next step

1. Try batch_size=1 + gradient_accumulation_steps=20
2. Investigate why no border labels were extracted from xmi_to_llama_samples
3. Consider using a smaller model or cloud GPU for real training
