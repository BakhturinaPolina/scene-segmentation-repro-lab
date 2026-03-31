# Project Plan: Scene Segmentation Research Workflow

## Project Context

This repository is a research wrapper workspace for testing and extending the
`LSX-UniWue/scene-segmentation` GitHub repository.

The target repository contains three main workflows:

1. `ssc/` - sequential sentence classification
2. `prompting/classify.py` - LLM-based segmentation
3. `llama/` - LLM fine-tuning

The original repository README states that:

- code is provided for sequential sentence classification (`ssc`),
  LLM prompting (`prompting`) and LLM fine-tuning (`llama`)
- prompting requires API credentials for OpenAI and potentially OpenRouter
- prompting may also require a base URL for a running Ollama server
- the data folder contains full annotated files for public-domain texts and
  stand-off annotations for other texts

## Immediate Task Scope

For now, do **not** run the target repository yet.

Current task:

- create a clean GitHub-style research repository
- document the later execution plan
- prepare the environment structure for reproducible work in Cursor on Ubuntu
- keep all future execution/testing/customization steps in this plan as roadmap only

## Local Development Conventions

- OS: Ubuntu
- IDE: Cursor
- Python: always use a fresh project-local virtual environment
- virtual environment path: `.venv`
- do not install global Python packages for this project
- keep setup reproducible and fully documented

## Phase 0 - Repository Setup

Completed / current phase:

- create empty research repository
- initialize Git
- create `.venv`
- select `.venv` interpreter in Cursor
- add `.gitignore`
- add `README.md`
- add this `PROJECT_PLAN.md`
- create standard folders for data, outputs, notebooks, tests, and source code

## Phase 1 - Inspect and Clone Target Repository

Goal of the first run:
baseline reproducibility, not optimization.

Answer four questions only:

1. does the code run at all?
2. which parts run locally without modification?
3. which parts require API tokens or external services?
4. where do failures occur (`install`, `import`, `path`, `config`, `GPU`, `API`)?

Environment strategy for smoke tests (single `.venv` only):

- keep one interpreter at `.venv`
- use staged installs instead of multiple environments:
  - install `requirements-basic.txt` first for fast validation of non-heavy workflows
  - install full dependencies later for complete reproduction, including heavy fine-tuning stack

Clone and structure verification checklist (immediately after clone):

- repository opens in Cursor
- folders exist: `ssc`, `prompting`, `llama`, `data`, `utils`
- Cursor interpreter points to `.venv`
- imports resolve from project root

## Phase 2 - Smoke Test the Target Code As-Is

Goal:
verify that the target code works before any customization.

Scope for this phase:

1. verify imports
2. verify paths and expected data structure
3. determine which workflows can run locally without extra API credentials
4. classify errors into:
   - dependency/setup issues
   - missing paths/files
   - API/auth issues
   - GPU/CUDA issues
   - parsing/format issues

Expected order of testing:

1. `ssc/`
2. `prompting/classify.py`
3. `llama/`

Reason:
smallest surface area first, API-dependent second, heaviest/GPU-sensitive last.

## Phase 3 - Baseline Execution As-Is

### 3.1 SSC Baseline

Goal:
run the sequential sentence classification workflow without modifications.

Tasks:
- identify entry script (`main.py`, `train.py`, or another launcher)
- verify required input paths
- run a minimal training or inference pass
- confirm that outputs are written correctly
- log runtime, device, and result files

### 3.2 Prompting Baseline

Goal:
run `prompting/classify.py` as-is on a small text sample.

Tasks:
- provide API credentials/config where required
- use one default LLM only
- verify request formatting
- verify response parsing
- verify saved outputs

### 3.3 LLaMA Baseline

Goal:
check whether the fine-tuning environment can be installed and started.

Tasks:
- install heavy dependencies only after simpler workflows are tested
- verify whether local hardware/software supports the required stack
- do a dry run if full training is too heavy

## Phase 4 - Stabilization and Reproducibility

Goal:
turn the baseline into a reproducible workflow.

Tasks:
- clean up path handling
- clean up config handling
- document exact commands
- save logs and outputs
- create short "known issues" notes
- define what counts as "working" for each workflow

## Phase 5 - Controlled Experiments

Only after the baseline works.

### 5.1 Encoder / Backbone Experiments for SSC

Hypothesis:
different pretrained encoder models may affect segmentation quality.

Possible variants:
- baseline encoder from original repo
- stronger general transformer baseline
- paraphrase-oriented sentence models
- other sentence-transformer variants
- multilingual variants if needed later

Important rule:
change one variable at a time.

### 5.2 LLM Experiments via OpenRouter

Hypothesis:
different LLMs may perform differently on scene/event segmentation.

Possible comparisons:
- one strong instruction-following model
- one smaller cheaper fast model
- one model already used successfully in prior literary work
- one or more models often associated with creative writing or roleplay

Important rule:
keep prompt and evaluation constant while changing model.

### 5.3 Prompt Schema Experiments

Hypothesis:
task wording and output format may strongly affect results.

Possible variations:
- binary boundary decision
- explicit instructions to track changes in time, place, characters, action
- JSON output vs label list
- short context window vs larger context window
- reasoning-allowed vs no-reasoning output

### 5.4 Label Schema Experiments

Hypothesis:
richer labels may improve interpretability but increase complexity.

Possible label setups:
- binary: boundary / no boundary
- multi-class: time shift / location shift / character shift / action shift
- hierarchical: strong boundary / weak boundary / uncertain boundary

## Phase 6 - Evaluation and Comparison

Goal:
compare all tested settings systematically.

Evaluation dimensions:
- segmentation quality
- robustness
- runtime
- memory usage
- API cost where relevant
- usefulness for literary analysis

Outputs:
- comparison table
- shortlist of best configurations
- recommendation for future project use

## Phase 7 - Integration into Literary Research Pipeline

Possible future integration:
- segmentation before BERTopic
- scene-level topic modeling
- scene-level emotion analysis
- scene-level narrative structure analysis
- scene segmentation as unit for agent-based reading simulations

## Working Principles for Cursor AI Agent

When acting in this repository:

- do not skip environment documentation
- do not install heavy dependencies before the basic structure is clear
- prefer small reproducible tests first
- log every important command in markdown
- separate baseline reproduction from experimental customization
- treat `PROJECT_PLAN.md` as the project roadmap
- update this file when later phases begin
