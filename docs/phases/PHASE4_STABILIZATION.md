# Phase 4 - Stabilization and Reproducibility

This document operationalizes Phase 4 from `docs/planning/PROJECT_PLAN.md`.

## Scope

- Clean path handling for local wrappers in `src/`.
- Clean config handling via per-run `config.json`.
- Exact runnable commands for baseline workflows.
- Standardized run artifacts (`command.txt`, `config.json`, result files).
- Short known-issues summary.
- Explicit "working" criteria per workflow.

## Bounded Timeout Policy (Fixed)

For reproducible Phase 4 runtime verification, heavy GPU steps are run with a fixed hard cap:

- `heavy_timeout_seconds = 1800` (30 minutes)

This cap applies to:

- `src/run_ssc_baseline.py` (via `--timeout_seconds`)
- `src/run_llama_baseline.py` (via `--timeout_seconds`)
- `src/reproduce_stss_test_2.py` forwarding `--heavy_timeout_seconds`

Policy note:

- Keep this value fixed across comparable bounded verification runs.
- If a different cap is needed for a new objective, log it as a separate run type.

## Path and Config Standard

Runtime helpers:

- `src/workflow_runtime.py`
  - `project_root(...)`
  - `stss_test2_data_dir(...)`
  - `output_dir_for(...)`
  - `write_repro_files(...)`

Applied to:

- `src/run_prompting_baseline.py`
- `src/run_prompting_stratified.py`
- `src/run_prompting_phase_a.py`

Each run now writes:

- `command.txt` - exact command invocation
- `config.json` - normalized runtime arguments

## Exact Commands

All commands run from repository root.

### 1) Phase 4 local unit tests (offline)

```bash
python -m unittest tests/test_workflow_runtime.py -v
```

Expected:

- 5 tests pass.
- No external API key required.

### 2) Prompting baseline smoke run

```bash
source .venv/bin/activate
OPENROUTER_API_KEY=sk-or-... python src/run_prompting_baseline.py --model nvidia/nemotron-3-super-120b-a12b:free --max_sentences 5 --reasoning low
```

Expected artifacts in `outputs/runs/prompting/<today>/baseline_qwen3/`:

- `command.txt`
- `config.json`
- `results.json`
- `summary.json`

### 3) Prompting stratified smoke run

```bash
source .venv/bin/activate
OPENROUTER_API_KEY=sk-or-... python src/run_prompting_stratified.py --model nvidia/nemotron-3-super-120b-a12b:free --dry_run 20 --max_per_class 10 --reasoning low
```

Expected artifacts in `outputs/runs/prompting/<today>/<run_slug>/`:

- `command.txt`
- `config.json`
- `cache_*.json`
- `results_*.json`
- `summary.json`

### 4) Phase A orchestrator smoke run

```bash
source .venv/bin/activate
OPENROUTER_API_KEY=sk-or-... python src/run_prompting_phase_a.py --families A,B --model nvidia/nemotron-3-super-120b-a12b:free --dry_run 5 --reasoning off
```

Expected artifacts in `outputs/runs/prompting/<today>/`:

- `command.txt`
- `config.json`
- `phase_a_manifest.json`

Note: for `openrouter/free`, reasoning `off` is automatically switched to `low`.

### 5) Full bounded STSS-Test-2 verification (canonical)

```bash
source .venv-gpu/bin/activate
OPENROUTER_API_KEY=sk-or-... python3 src/reproduce_stss_test_2.py --date <YYYY-MM-DD-tag> --heavy_timeout_seconds 1800
```

Expected artifacts in `outputs/reproduction/<YYYY-MM-DD-tag>/stss_test_2/`:

- `command.txt`
- `config.json`
- `manifest.json` (authoritative step status: success/failed/skipped)

## Known Issues (Short)

1. **SSC / LLaMA import chain on CPU**:
   `ssc.dataset` and downstream training paths still depend on Unsloth GPU stack.

2. **Prompting requires API credentials**:
   `OPENROUTER_API_KEY` is mandatory for live runs.

3. **Default baseline model slug fixed**:
   Deprecated `qwen/qwen3.6-plus:free` was removed from defaults. Use `--model nvidia/nemotron-3-super-120b-a12b:free` for live smoke tests.

4. **Upstream dependency sensitivity**:
   Compatibility still relies on pinned versions documented in `docs/setup/ENVIRONMENT_SETUP.md` and related run notes.

## Definition of "Working"

### Prompting workflow

Working if:

- script starts from repo root without path edits,
- writes `command.txt` and `config.json`,
- produces non-empty `summary.json`,
- exits with code 0.

### SSC workflow

Working if:

- imports and startup command run with documented environment,
- clear failure category is logged when blocked by GPU/Unsloth,
- run note includes reproducible command and environment details.

### LLaMA workflow

Working if:

- dry-run starts in `.venv-gpu` (or logs hardware block explicitly),
- OOM or dependency failures are reproducibly logged with exact command and environment,
- run outputs and issue note are linked.

## Logging Reminder

When executing these commands for real benchmarking/comparison:

- create a `run` note immediately,
- create `artifact` notes for key outputs,
- create/update `issue` note for blocking failures,
- create a `sync_note` at the end of the work block.
