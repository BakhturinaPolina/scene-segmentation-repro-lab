# Scene Segmentation Research Workspace

This repository is a research workspace for testing and extending
`LSX-UniWue/scene-segmentation`.

## Goals

- create a clean reproducible local environment in Cursor on Ubuntu
- document setup and execution steps
- test the original repository as-is
- later run controlled experiments on:
  - SSC models
  - prompting-based segmentation
  - model backbones and embedding choices
  - LLM choices via OpenRouter
  - prompt schemas
  - labeling schemas

## Current Stage

Phase 2 (smoke tests) completed. Environment preparation documented.

## Repository Structure

- `PROJECT_PLAN.md` - full project roadmap
- `ENVIRONMENT_SETUP.md` - environment setup instructions and system specs
- `PHASE2_PHASE3_NOTES.md` - detailed smoke test logs and compatibility fixes
- `upstream/` - cloned target repository (git-ignored contents)
- `src/` - helper scripts and wrappers
- `notebooks/` - exploration notebooks
- `data/` - raw/interim/processed data
- `outputs/` - logs, figures, predictions
- `tests/` - test scripts

## Environment

Ubuntu 24.04 + Cursor IDE + dual virtual environments:

| Environment | Purpose | Activation |
|-------------|---------|------------|
| `.venv` | CPU smoke tests | `source .venv/bin/activate` |
| `.venv-gpu` | GPU training (Unsloth) | `source .venv-gpu/bin/activate` |

See `ENVIRONMENT_SETUP.md` for full details.

## Quick Start

### CPU environment (smoke tests)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-basic.txt
```

### GPU environment (training)

```bash
python3 -m venv .venv-gpu
source .venv-gpu/bin/activate
pip install --upgrade pip setuptools wheel
pip install unsloth unsloth-zoo
```

### Verify GPU

```bash
source .venv-gpu/bin/activate
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

## Working Directory

Commands must run from the **clone root**:

```bash
cd upstream/scene-segmentation
python -c "import ssc.model; print('OK')"
```

Running from the wrapper root will cause `ModuleNotFoundError: No module named 'ssc'`.

## Install Order (legacy note)

```bash
pip install -r requirements-basic.txt
# later:
pip install -r requirements.txt
```

Note: do not paste both install lines as one command block in the terminal.
If pasted together, both commands will run sequentially in the same session.
