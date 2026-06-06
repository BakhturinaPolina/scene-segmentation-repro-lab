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

**Status: COMPLETED (2026-03-31)**

Goal of the first run:
baseline reproducibility, not optimization.

Answer four questions only:

1. does the code run at all?
2. which parts run locally without modification?
3. which parts require API tokens or external services?
4. where do failures occur (`install`, `import`, `path`, `config`, `GPU`, `API`)?

Environment strategy (revised from single `.venv` to dual-environment):

- `.venv` — CPU-only smoke tests with pinned compatible versions
- `.venv-gpu` — GPU training with Unsloth stack

Reason for revision: SSC smoke tests require `transformers==4.46.3`; Unsloth requires `transformers>=4.51.3`. These are incompatible in one environment.

Clone and structure verification checklist (immediately after clone):

- [x] repository opens in Cursor
- [x] folders exist: `ssc`, `prompting`, `llama`, `data`, `utils`
- [x] Cursor interpreter points to `.venv`
- [x] imports resolve from clone root (not wrapper root)

Documentation:

- `docs/setup/ENVIRONMENT_SETUP.md` — full setup instructions and system specs
- `docs/phases/PHASE2_PHASE3_NOTES.md` — detailed smoke test logs and compatibility fixes

## Phase 2 - Smoke Test the Target Code As-Is

**Status: COMPLETED (2026-03-31)**

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

### Results summary

| Module | Import test | Script startup | Blocking issue |
|--------|-------------|----------------|----------------|
| `ssc.model` | PASS (CPU env) | — | — |
| `ssc.dataset` | FAIL | FAIL | Unsloth GPU requirement |
| `prompting.classify` | PASS (CPU env) | FAIL | `utils` path resolution |
| `ssc.main` | — | FAIL | Unsloth GPU requirement |
| `ssc.train` | — | FAIL | Unsloth GPU requirement |

### Key findings

1. **Dependency compatibility**: Required `transformers==4.46.3` and `langchain==0.1.9` for imports to pass.
2. **Working directory sensitivity**: Must run from clone root, not wrapper root.
3. **GPU requirement**: Unsloth blocks all `ssc.dataset` and downstream paths on CPU-only torch.
4. **API/auth**: Not reached; prompting import passes but script fails on path resolution first.

Full details: `docs/phases/PHASE2_PHASE3_NOTES.md`

## Phase 3 - Baseline Execution As-Is

### 3.1 SSC Baseline

**Status: COMPLETED (2026-04-05) — training failure, needs rerun**

BERT-German-cased trained on upstream data. Macro F1 = 0.009 on STSS-Test-2 (model predicts only 1 BORDER per novel). Paper's GBERT-Large achieves 0.66. Cause: likely undertrained or label-imbalance issue. Needs proper hyperparameter tuning before this baseline is meaningful.

Run log: `research_log/runs/2026-04-05__ssc__baseline__bert-german-cased.md`

### 3.2 Prompting Baseline

**Status: COMPLETED (2026-04-05 -- 2026-04-08)**

Pipeline validated with Qwen3.6-Plus (20 sentences), then free-model sweep (8 models x 10 sentences). Full stratified evaluation completed for Nemotron-3-Super-120b (n=892) and GPT-OSS-120b pilot (n=60). Nemotron selected as best model (F1=0.753 at tol=0 on stratified sample).

Critical caveat: stratified sampling inflates precision. Corrected F1 estimate: ~0.38 (tol=0). See `docs/planning/PROGRESS_REPORT.md` for details.

Run logs:
- `research_log/runs/2026-04-05__prompting__baseline__qwen3-openrouter.md`
- `research_log/runs/2026-04-08__prompting__baseline__gptoss120b-stratified.md`
- `research_log/runs/2026-04-08__prompting__baseline__nemotron-stratified.md`
- `research_log/experiments/experiment__prompting__model__free-120b-comparison.md`

### 3.3 LLaMA Baseline

**Status: BLOCKED (2026-04-05) — OOM**

LLaMA-3 8B dry run via Unsloth: out-of-memory on RTX 2070 (8 GB VRAM). Needs larger GPU, quantization, or cloud compute.

Run log: `research_log/runs/2026-04-05__llama__dry-run__unsloth-8b.md`

## Phase 4 - Stabilization and Reproducibility

**Status: IN PROGRESS (2026-05-14)**

Goal:
turn the baseline into a reproducible workflow.

Tasks:
- clean up path handling
- clean up config handling
- document exact commands
- save logs and outputs
- create short "known issues" notes
- define what counts as "working" for each workflow

Bounded runtime policy for reproducible STSS-Test-2 verification:

- heavy-step timeout is fixed at `1800s` (30 minutes) for SSC and LLaMA wrapper runs.
- this policy is documented in `docs/phases/PHASE4_STABILIZATION.md` and should remain unchanged across comparable bounded runs.

Execution and validation checklist:
- `docs/phases/PHASE4_STABILIZATION.md`

## Phase 5 - Controlled Experiments

Only after the baseline works. One factor at a time.

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

### 5.2 Prompting Experiments (OpenRouter Baseline-First)

**Status: Phases A–C completed (2026-05-15); reasoning=off full-stratified confirmation pending.**

This section is the ground-truth protocol for ongoing prompting experiments.

#### Headline result and report

- Winning combination: `nvidia/nemotron-3-super-120b-a12b:free` + prompt family B (zero-shot JSON), with locked decoding controls (temperature 0, seed 1337, max_tokens 256, context 409, response_format json_schema, reasoning low).
- Full-stratified headline on STSS-Test-2 (892 sentences): F1@0 = 0.763, F1@1 = 0.784, F1@3 = 0.830.
- +0.010 F1@0 over the upstream `prompt_classify` baseline at identical scope.
- Full narrative, paper comparison, and caveats: [docs/prompting/PROMPTING_RESULTS_REPORT.md](../prompting/PROMPTING_RESULTS_REPORT.md).

#### Data and comparability constraints

- Available evaluation data: STSS-Test-2 only (2 novels, ~11k sentences total)
- Test-Full from the paper is not yet available locally
- All comparisons to the paper should clearly state dataset mismatch when relevant

#### Prerequisite (must be completed first)

Implement full-eval mode in `src/runners/run_prompting_stratified.py` so evaluation can
run on ALL sentences with natural class distribution (about 4% BORDER), not only
balanced stratified subsets.

#### Fixed controls for prompt comparisons

The following must remain fixed inside each comparison block:

- same left/right context size
- same sentence marker format
- same output schema per prompt family
- same evaluation script and tolerance setup
- same decoding defaults unless that factor is being tested

Recommended decoding defaults:

- `temperature = 0`
- fixed `seed` when the provider/model supports it
- short response budget via `max_tokens`
- JSON output when supported (`json_object` or `json_schema`)

#### Model-bucket strategy (OpenRouter free)

Phase A uses OpenRouter free routing and broad prompt-family screening:

1. `openrouter/free` moving baseline
2. one small fast instruct model
3. one larger free instruct model
4. one free reasoning-capable model

Phase B narrows to pinned models from current free inventory.

Phase C continues only with top 1–2 performing model/prompt combinations.

#### Prompt family grid (A–J)

Run these prompt families in the first full sweep:

| Family | Name | Output style |
|---|---|---|
| A | Zero-shot, label only | single label |
| B | Zero-shot, JSON only | JSON |
| C | Zero-shot, rubric JSON | JSON |
| D | Few-shot, balanced examples | JSON |
| E | Few-shot, contrastive minimal pairs | JSON |
| F | Hidden-rationale rubric | JSON |
| G | Visible CoT rubric | JSON |
| H | Boundary localization over short chunk | sentence id / NONE |
| I | Boundary scoring over short chunk | JSON array |
| J | Two-stage classify-after-analysis | JSON |

Templates for all A–J families are maintained in `src/prompts/`.

#### Experimental phases

| Phase | Purpose | Scope | Keep / Drop policy |
|---|---|---|---|
| Phase A | Prompt search | Run A–J on `openrouter/free` | Keep top 2–3 prompt families |
| Phase B | Model search | Run kept prompts on 3–5 pinned free models | Keep top 1–2 model/prompt combos |
| Phase C | Focused iteration | Deepen best combos (context, temperature, few-shot) | Stop exploring weaker branches |

#### Follow-up axes (one factor at a time, after full-eval)

| ID | Factor | Values |
|---|---|---|
| E1 | Prompt family | A–J |
| E2 | Model bucket/model | router + pinned free models |
| E3 | Context window | 409, 1024, 2048, 4096 |
| E4 | Temperature | 0.0, 0.3, 1.0 |
| E5 | Few-shot count | 0-shot, 2-shot, 4-shot |
| E6 | Reasoning mode | off, low, on |

#### Metrics and logging requirements

Always log:

- precision / recall / F1 at tolerance 0/1/3
- parse failure rate
- average output length
- average latency
- error tags:
  - minor shift false positive
  - implicit shift false negative
  - non-scene confusion
  - early/late but near-correct boundary

#### Operational sequence

```
1. Implement full-eval mode
2. Run prompt-family sweep A–J with openrouter/free
3. Keep top 2–3 prompt families
4. Run those on pinned free-model buckets
5. Keep top 1–2 model/prompt combinations
6. Run focused experiments (context, temperature, few-shot, reasoning)
```

### 5.3 Label Schema Experiments

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
- treat `docs/planning/PROJECT_PLAN.md` as the project roadmap
- update this file when later phases begin
