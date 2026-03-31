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

Initial repository setup only.

## Repository Structure

- `PROJECT_PLAN.md` - full project roadmap
- `src/` - helper scripts and wrappers
- `notebooks/` - exploration notebooks
- `data/` - raw/interim/processed data
- `outputs/` - logs, figures, predictions
- `tests/` - test scripts

## Environment

Ubuntu + Cursor IDE + project-local `.venv`.

## Install Order

```bash
pip install -r requirements-basic.txt
# later:
pip install -r requirements.txt
```

Note: do not paste both install lines as one command block in the terminal.
If pasted together, both commands will run sequentially in the same session.
