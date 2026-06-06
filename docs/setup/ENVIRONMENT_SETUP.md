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

Two separate environments are maintained to avoid dependency conflicts:

| Environment | Purpose | PyTorch | GPU Support |
|-------------|---------|---------|-------------|
| `.venv` | CPU smoke tests, SSC/prompting import validation | `2.5.1+cpu` | No |
| `.venv-gpu` | GPU training, Unsloth fine-tuning | `2.10.0+cu128` | Yes |

### Why two environments?

1. **transformers compatibility**: SSC smoke tests require `transformers==4.46.3` to avoid dataclass errors; Unsloth requires `transformers>=4.51.3`.
2. **torch/torchvision pairing**: CPU-only wheels avoid CUDA complexity for quick validation; GPU env needs CUDA-enabled wheels.
3. **Unsloth GPU requirement**: Unsloth raises `NotImplementedError` on CPU-only torch.

---

## CPU Environment (`.venv`)

### Purpose

Fast smoke testing of SSC and prompting imports without GPU dependencies.

### Creation

```bash
cd $PROJECT_ROOT
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-basic.txt
```

### Key pinned versions (`requirements-basic.txt`)

```
--extra-index-url https://download.pytorch.org/whl/cpu

pip==24.0
setuptools==81.0.0
wheel==0.45.1

torch==2.5.1+cpu
torchvision==0.20.1+cpu
transformers==4.46.3
datasets==4.8.4
scikit-learn==1.8.0
loguru==0.7.3
langchain==0.1.9
```

### Compatibility notes

| Issue | Root cause | Resolution |
|-------|-----------|------------|
| `SSCModelConfig` dataclass error | `transformers>=5.0` changed `PretrainedConfig` to auto-dataclass | Pin `transformers==4.46.3` |
| `ModuleNotFoundError: langchain.adapters` | `langchain>=0.2` restructured module layout | Pin `langchain==0.1.9` |
| `torchvision::nms` operator missing | torch/torchvision version mismatch | Pin compatible pair `2.5.1+cpu` / `0.20.1+cpu` |

### Smoke test results (from clone root)

| Command | Result |
|---------|--------|
| `python -c "import ssc.model"` | **PASS** |
| `python -c "import ssc.dataset"` | FAIL (Unsloth GPU check) |
| `python -c "import prompting.classify"` | **PASS** |
| `python -m ssc.main --help` | FAIL (Unsloth GPU check) |
| `python -m ssc.train --help` | FAIL (Unsloth GPU check) |
| `python prompting/classify.py` | FAIL (`utils` import path) |

The Unsloth failures are expected in CPU-only mode; they are not blocking for prompting or pure SSC model validation.

---

## GPU Environment (`.venv-gpu`)

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
gpu_env_report.txt
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
