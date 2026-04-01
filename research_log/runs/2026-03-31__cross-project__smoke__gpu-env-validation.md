---
note_type: run
run_id: run_20260331_gpu_env_validation
title: "GPU environment creation and validation"
date: 2026-03-31
track: cross-project
run_type: smoke
status: success
goal: "Create .venv-gpu, install GPU-enabled PyTorch + Unsloth, validate CUDA and import"
entrypoint: "python -c 'import ...'"
command: |
  python3 -m venv .venv-gpu
  source .venv-gpu/bin/activate
  pip install --upgrade pip setuptools wheel
  pip install --index-url https://download.pytorch.org/whl/cu124 torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1
  pip install unsloth unsloth-zoo
  pip uninstall -y torchaudio
  python -c "import torch; print(torch.__version__, torch.version.cuda, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
  python -c "import unsloth; print('unsloth', unsloth.__version__)"
  python -c "import transformers,trl,peft,accelerate,bitsandbytes; print(transformers.__version__, trl.__version__, peft.__version__, accelerate.__version__, bitsandbytes.__version__)"
working_directory: "."
git_commit: "9848021"
environment: "scene-seg-gpu (.venv-gpu)"
os: "Linux"
hardware: "RTX 2070 Max-Q, 8 GB VRAM"
gpu: "NVIDIA GeForce RTX 2070 with Max-Q Design"
cuda_notes: "Driver 580.126.09, CUDA driver 13.0, nvcc 12.0.140, compute cap 7.5"
api_provider: ""
api_model: ""
api_cost_estimate: ""
dataset_assets: []
label_schema: ""
prompt_version: ""
model_name: ""
varying_factor: "none"
fixed_conditions:
  - "fresh .venv-gpu"
  - "Unsloth pulls its preferred torch version (2.10.0+cu128)"
random_seed: ""
output_dir: ""
artifacts_expected:
  - "gpu_env_report.txt"
artifacts_produced:
  - "gpu_env_report.txt"
main_metric_name: ""
main_metric_value: ""
precision: ""
recall: ""
f1: ""
iou: ""
runtime: ""
failure_category: ""
related_experiment: ""
related_issue: "issue_unsloth_cpp_extensions_skip"
decision_relevance: true
notion_targets:
  roadmap: true
  runs: true
  experiments: ""
  artifacts: true
  issues: true
  decisions: true
---

## Objective

Create a GPU-enabled environment suitable for Unsloth fine-tuning and any workflow that requires CUDA.

## What was held constant

- System GPU hardware (RTX 2070 Max-Q)
- NVIDIA driver (580.126.09)
- System CUDA toolkit (12.0.140)

## What changed

- Created new `.venv-gpu` virtual environment
- Initially installed torch 2.5.1+cu124; Unsloth then upgraded to torch 2.10.0+cu128
- Removed torchaudio to avoid version conflict

## Outcome

Final resolved stack:

| Package | Version |
|---------|---------|
| torch | 2.10.0+cu128 |
| torchvision | 0.25.0 |
| transformers | 4.52.4 |
| trl | 0.18.2 |
| peft | 0.18.1 |
| accelerate | 0.34.2 |
| bitsandbytes | 0.49.2 |
| unsloth | 2026.3.18 |
| xformers | 0.0.35 |

Validation results:
- `torch.cuda.is_available()` → `True`
- `torch.cuda.get_device_name(0)` → `NVIDIA GeForce RTX 2070 with Max-Q Design`
- `import unsloth` → `unsloth 2026.3.18` (with patching messages)

Known warning: `Skipping import of cpp extensions due to incompatible torch version` — Unsloth C++ extensions expect torch >= 2.11.0; training works via Python fallback.

## Interpretation

GPU environment is functional. The Unsloth stack installed cleanly and recognizes the local GPU. The C++ extensions warning is non-blocking.

## Next step

Use `.venv-gpu` for ssc.dataset imports, training dry runs, and Unsloth fine-tuning workflows in Phase 3.
