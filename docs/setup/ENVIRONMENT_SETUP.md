# Environment Setup Documentation

> `$PROJECT_ROOT` refers to the local clone of this repository.

Date: 2026-03-31  
Workspace: `$PROJECT_ROOT`

This document records the environment preparation work for Phases 1–2 of the project plan.

---

## System Specification

### Hardware

- GPU: NVIDIA GeForce RTX 2070 with Max-Q Design (8 GB VRAM, compute capability 7.5)
- RAM: 62 GB
- Disk: 1.8 TB NVMe (~670 GB available)

### Software

- OS: Ubuntu 24.04.4 LTS (noble)
- Kernel: 6.17.0-111019-tuxedo
- Architecture: x86_64
- Python: 3.12.3
- GCC: 13.3.0

### NVIDIA Stack

- Driver: 580.126.09
- CUDA (driver): 13.0
- CUDA Toolkit (nvcc): 12.0.140 (installed via `apt install nvidia-cuda-toolkit`)
- cuDNN: bundled via PyTorch wheels (not system-installed)
- Secure Boot: not applicable (EFI variables not supported)

---

## Virtual Environment Strategy

A single CUDA-enabled environment (`.venv`) is used for finetune, eval, prompting, and Gemini pilots. See `README.md` Quick Start.

Historical note: Phase 2 maintained separate CPU (`.venv`) and GPU (`.venv-gpu`) environments because SSC smoke tests required `transformers==4.46.3` while Unsloth required `transformers>=4.51.3`. The unified `requirements.txt` targets the finetune/Gemini stack (`transformers==4.57.3`). Upstream SSC imports may still need a separate CPU venv with older pins if required.

| Environment | Purpose | PyTorch | GPU Support |
|-------------|---------|---------|-------------|
| `.venv` | Finetune, eval, prompting, Gemini pilot | CUDA (cu128 wheel) | Yes |

---

## Primary Environment (`.venv`)

### Purpose

Finetune/eval, prompting runners, and Gemini Batch API pilots.

### Creation

```bash
cd $PROJECT_ROOT
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
```

### Key pinned versions (`requirements.txt`)

```
pip>=24.0
setuptools>=81.0.0
wheel>=0.45.1

google-genai==2.9.0

huggingface_hub>=0.34
unsloth==2026.6.1
unsloth_zoo==2026.6.1
trl==0.22.2
transformers==4.57.3
datasets>=3.0
accelerate>=1.4
peft>=0.7
bitsandbytes>=0.49
tqdm>=4.66

scikit-learn==1.8.0
loguru==0.7.3
langchain==0.1.9
```

### Compatibility notes

| Issue | Root cause | Resolution |
|-------|-----------|------------|
| `SSCModelConfig` dataclass error | `transformers>=5.0` changed `PretrainedConfig` to auto-dataclass | Use separate CPU venv with `transformers==4.46.3` for SSC smoke only |
| `ModuleNotFoundError: langchain.adapters` | `langchain>=0.2` restructured module layout | Pin `langchain==0.1.9` |
| Unsloth GPU requirement | Unsloth raises `NotImplementedError` on CPU-only torch | Install CUDA torch before other deps |

### Smoke test results (from clone root)

| Command | Result |
|---------|--------|
| `python -c "import ssc.model"` | **PASS** (CPU venv only; may fail with finetune transformers pin) |
| `python -c "import ssc.dataset"` | FAIL (Unsloth GPU check) |
| `python -c "import prompting.classify"` | **PASS** |
| `python -m ssc.main --help` | FAIL (Unsloth GPU check) |
| `python -m ssc.train --help` | FAIL (Unsloth GPU check) |
| `python prompting/classify.py` | FAIL (`utils` import path) |

The Unsloth failures in the table above were observed under the historical CPU-only `.venv`; with CUDA torch they should pass.

### Validation commands

```bash
source .venv/bin/activate

# GPU detection
python -c "import torch; print(torch.__version__, torch.version.cuda, torch.cuda.is_available(), torch.cuda.get_device_name(0))"

# Unsloth import
python -c "import unsloth; print('unsloth', unsloth.__version__)"
```

---

## Legacy GPU Environment (`.venv-gpu`, removed)

> **Superseded:** `.venv-gpu` was merged into `.venv` (see `README.md`). This section is kept as a historical record of the March 2026 setup.

### Purpose

GPU-accelerated training and Unsloth fine-tuning workflows.

### Creation

```bash
cd $PROJECT_ROOT
python3 -m venv .venv-gpu
source .venv-gpu/bin/activate
pip install --upgrade pip setuptools wheel
```

### PyTorch installation (CUDA 12.8)

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
```

Or let Unsloth pull its preferred versions:

```bash
pip install unsloth unsloth-zoo
```

### Final resolved stack

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

### Validation commands

```bash
source .venv-gpu/bin/activate

# GPU detection
python -c "import torch; print(torch.__version__, torch.version.cuda, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
# Expected: 2.10.0+cu128 12.8 True NVIDIA GeForce RTX 2070 with Max-Q Design

# Unsloth import
python -c "import unsloth; print('unsloth', unsloth.__version__)"
# Expected: unsloth 2026.3.18

# Full stack
python -c "import transformers,trl,peft,accelerate,bitsandbytes; print(transformers.__version__, trl.__version__, peft.__version__, accelerate.__version__, bitsandbytes.__version__)"
# Expected: 4.52.4 0.18.2 0.18.1 0.34.2 0.49.2
```

### Known warnings

1. **Import order**: Unsloth should be imported before `transformers`, `trl`, `peft`:
   ```python
   import unsloth
   from transformers import ...
   ```

2. **C++ extensions skip**: Message `Skipping import of cpp extensions due to incompatible torch version` appears because Unsloth's compiled extensions expect `torch >= 2.11.0`. Training still works via Python fallback paths.

3. **torchaudio removed**: Uninstalled to avoid version conflict with torch 2.10.0.

---

## Working Directory Requirements

All commands must be run from the **clone root**, not the wrapper root:

```bash
cd $PROJECT_ROOT/upstream/scene-segmentation
```

Running from `$PROJECT_ROOT` will cause:
```
ModuleNotFoundError: No module named 'ssc'
```

Alternative: set `PYTHONPATH`:
```bash
export PYTHONPATH="$PROJECT_ROOT/upstream/scene-segmentation:$PYTHONPATH"
```

---

## Git-ignored artifacts

The following are excluded from version control (`.gitignore`):

```
.venv/
.venv-gpu/
unsloth_compiled_cache/
eval_partial.jsonl
outputs/artifacts/logs/gpu_env_report.txt
```

---

## Upstream repository location

The target repository (`LSX-UniWue/scene-segmentation`) is cloned to:

```
$PROJECT_ROOT/upstream/scene-segmentation
```

This isolation keeps wrapper files and upstream code separate.

---

## Commit history for environment work

| Commit | Description |
|--------|-------------|
| `cc4b09f` | Initialize research workspace for scene segmentation project |
| `42c0a92` | Add staged dependency install workflow for smoke tests |
| `3525715` | Pin CPU-compatible torch/vision and langchain/transformers for smoke tests |
| `9848021` | Document install command behavior and ignore local GPU artifacts |

---

## Quick reference

### Activate CPU environment
```bash
cd $PROJECT_ROOT
source .venv/bin/activate
```

### Activate GPU environment
```bash
cd $PROJECT_ROOT
source .venv-gpu/bin/activate
```

### Run smoke test (CPU)
```bash
source .venv/bin/activate
cd upstream/scene-segmentation
python -c "import ssc.model; print('OK')"
python -c "import prompting.classify; print('OK')"
```

### Run GPU validation
```bash
source .venv-gpu/bin/activate
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
python -c "import unsloth; print(unsloth.__version__)"
```
