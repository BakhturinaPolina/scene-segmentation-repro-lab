# Scene Segmentation Research Workspace

This repository is a research workspace for testing and extending
[LSX-UniWue/scene-segmentation](https://github.com/LSX-UniWue/scene-segmentation).

## Goals

- Create a clean reproducible local environment in Cursor on Ubuntu
- Document setup and execution steps
- Test the original repository as-is
- Run controlled experiments on:
  - SSC models
  - Prompting-based segmentation
  - Model backbones and embedding choices
  - LLM choices via OpenRouter
  - Prompt schemas
  - Labeling schemas

## Current Stage

Phase 2 (smoke tests) completed. Environment preparation documented.
Next: Phase 3 baseline execution.

## Repository Structure

```
.
├── README.md
├── rule.md                  # Research logging rules (strict YAML version)
├── requirements.txt         # Base pip/setuptools/wheel
├── requirements-basic.txt   # Pinned CPU smoke-test dependencies
├── docs/
│   ├── planning/            # Roadmap and progress
│   ├── setup/               # Environment setup
│   ├── phases/              # Phase execution notes
│   ├── prompting/           # Experiment reports
│   ├── corpora/             # Corpus catalogs and cost estimates
│   ├── reproducibility/     # Gap reviews
│   └── reference/           # External papers
├── research_log/
│   ├── runs/                # Structured run notes (YAML frontmatter)
│   ├── experiments/         # Experiment comparison notes
│   ├── artifacts/           # Artifact descriptions
│   ├── issues/              # Technical issue notes
│   ├── decisions/           # Standardization decision notes
│   ├── sync_notes/          # End-of-block Notion sync notes
│   └── templates/           # Note templates for each type
├── data/                    # Raw / interim / processed data
├── outputs/                 # runs, review, analysis, reproduction
├── src/                     # core, data, runners, review, prompts
├── scripts/                 # data prep, evaluation, export, sweeps
├── notebooks/               # Exploration notebooks
├── tests/                   # Test scripts
└── upstream/                # Cloned target repository (git-ignored)
```

## Research Log

All research activity is documented in `research_log/` using structured markdown notes with YAML frontmatter. See `rule.md` for the full specification.

The log is designed to sync with a Notion research hub. Each note type maps to a Notion database:

| Note type | Folder | Notion target |
|-----------|--------|---------------|
| Run | `research_log/runs/` | Runs |
| Experiment | `research_log/experiments/` | Experiments |
| Artifact | `research_log/artifacts/` | Artifacts |
| Issue | `research_log/issues/` | Issues |
| Decision | `research_log/decisions/` | Decisions |
| Sync note | `research_log/sync_notes/` | Roadmap / daily summary |

## Environment

Ubuntu 24.04 + Cursor IDE + dual virtual environments:

| Environment | Purpose | Activation |
|-------------|---------|------------|
| `.venv` | CPU smoke tests | `source .venv/bin/activate` |
| `.venv-gpu` | GPU training (Unsloth) | `source .venv-gpu/bin/activate` |

See `docs/setup/ENVIRONMENT_SETUP.md` for full details.

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

Commands that use the upstream code must run from the **clone root**:

```bash
cd upstream/scene-segmentation
python -c "import ssc.model; print('OK')"
```

Running from the wrapper root will cause `ModuleNotFoundError: No module named 'ssc'`.
