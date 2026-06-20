# Phase 2 and Phase 3 Notes

> `$PROJECT_ROOT` refers to the local clone of this repository.

Date: 2026-03-31  
Workspace: `$PROJECT_ROOT`

## Scope

- Performed only Phase 2 (clone + integrity checks) and Phase 3 (smoke tests).
- No training, tuning, customization, or repository rewrites were performed.
- All Python commands were run with the project-local interpreter:
  - `$PROJECT_ROOT/.venv/bin/python`

## Phase 2 - Clone and Structure Verification

### Clone location

- Target cloned to:
  - `$PROJECT_ROOT/upstream/scene-segmentation`
- Wrapper/planning files at workspace root were preserved.

### Observed repository structure

Verified required top-level directories in the clone:

- `ssc` - present
- `prompting` - present
- `llama` - present
- `data` - present
- `utils` - present

Additional top-level files/folders observed:

- `README.md`
- `requirements.txt`
- `Dockerfile`

### Interpreter used

- Verified `.venv` interpreter path and version:
  - executable: `$PROJECT_ROOT/.venv/bin/python`
  - version: `3.12.3`

### Cursor/editor import-resolution check (pre-execution)

- `ReadLints` on:
  - `upstream/scene-segmentation/ssc/model.py`
  - `upstream/scene-segmentation/ssc/dataset.py`
  - `upstream/scene-segmentation/prompting/classify.py`
- Result: no editor diagnostics reported at this stage.

Local package discoverability checks:

- From clone root, module discovery succeeded for `ssc`, `prompting`, `utils`.
- From workspace root, module discovery failed for `ssc`, `prompting`, `utils`.

### Immediate red flags before execution

1. **Working-directory sensitivity is high**
   - Running from the wrapper root will break local imports (`ModuleNotFoundError: ssc`).
   - Commands should be run from clone root (or with `PYTHONPATH` explicitly set).
2. **Potential interpreter mismatch risk in Cursor UI**
   - No explicit `.vscode/settings.json` pin was found.
   - If Cursor is not currently using `./.venv/bin/python`, later failures are likely.
3. **Upstream dependency surface is larger than minimal smoke env**
   - Early imports already require modules not in minimal setup (`peft`, `wuenlp`, `langchain`).

---

## Phase 3 - Smoke Test Without Training

## 3.1 Explicit import tests

All tests were executed from:

- cwd: `$PROJECT_ROOT/upstream/scene-segmentation`
- interpreter: `$PROJECT_ROOT/.venv/bin/python`

### Import test results

1. Command:

```bash
$PROJECT_ROOT/.venv/bin/python -c "import ssc.model; print('OK ssc.model')"
```

Result: **failed**  
First error: `ModuleNotFoundError: No module named 'peft'`  
Likely cause: missing dependency (`peft`) required at import-time by `ssc/model.py`.

2. Command:

```bash
$PROJECT_ROOT/.venv/bin/python -c "import ssc.dataset; print('OK ssc.dataset')"
```

Result: **failed**  
First error: `ModuleNotFoundError: No module named 'wuenlp'`  
Likely cause: missing dependency (`wuenlp`) required at import-time by `ssc/dataset.py`.

3. Command:

```bash
$PROJECT_ROOT/.venv/bin/python -c "import prompting.classify; print('OK prompting.classify')"
```

Result: **failed**  
First error: `ModuleNotFoundError: No module named 'langchain'`  
Likely cause: missing dependency (`langchain`) required at import-time by `prompting/classify.py`.

Control check for cwd assumptions:

```bash
cd $PROJECT_ROOT
$PROJECT_ROOT/.venv/bin/python -c "import ssc.model"
```

Result: **failed** with `ModuleNotFoundError: No module named 'ssc'`  
Interpretation: local modules require running from clone root (or equivalent path setup).

## 3.2 Script startup checks

All tests were executed from clone root with `.venv` Python.

1. Command:

```bash
$PROJECT_ROOT/.venv/bin/python -m ssc.main --help
```

Starts? **No**  
First meaningful stopping point: import crash before CLI help due to `ModuleNotFoundError: peft`.  
Stop classification: **problematic** (import-level environment issue, script logic not reached).

2. Command:

```bash
$PROJECT_ROOT/.venv/bin/python -m ssc.train --help
```

Starts? **No**  
First meaningful stopping point: import crash before CLI help due to `ModuleNotFoundError: wuenlp`.  
Stop classification: **problematic** (import-level environment issue, script logic not reached).

3. Command:

```bash
$PROJECT_ROOT/.venv/bin/python prompting/classify.py
```

Starts? **No**  
First meaningful stopping point: import crash due to `ModuleNotFoundError: langchain`.  
Stop classification: **problematic** (import-level environment issue, no API/auth checkpoint reached).

## 3.3 Failure classification

### dependency error

1. `peft` missing
- Area: `ssc`
- Trigger: `import ssc.model` and `python -m ssc.main --help`
- Root cause: dependency not present in current `.venv`.
- Blast radius: blocks SSC model/main entrypoint startup.

2. `wuenlp` missing
- Area: `ssc`
- Trigger: `import ssc.dataset` and `python -m ssc.train --help`
- Root cause: dependency not present in current `.venv`.
- Blast radius: blocks SSC dataset/train workflow.

3. `langchain` missing
- Area: `prompting`
- Trigger: `import prompting.classify` and `python prompting/classify.py`
- Root cause: dependency not present in current `.venv`.
- Blast radius: blocks prompting workflow startup.

### interpreter / working-directory / import-resolution error

1. local package not found from wrapper root
- Area: `ssc` (also affects `prompting`, `utils`)
- Trigger: running import from workspace root instead of clone root.
- Root cause: package discovery depends on cwd/project root.
- Blast radius: can block all workflows if commands are executed from wrong directory.

### auth/API error

- No auth/API failure reached yet.
- Reason: prompting flow stops at missing `langchain` import before any credential usage.

### CUDA/GPU error

- No CUDA/GPU failure reached yet.
- Reason: scripts do not proceed far enough due to earlier dependency failures.

### missing file/path error

- No missing data/config file error reached yet.
- Reason: startup stops at import stage first.

### data format/parsing error

- No parsing failures reached yet.
- Reason: runtime does not reach data loading/parsing.

### unknown / needs deeper inspection

- None at this stage; current blockers are clear and categorized.

---

## Concise summary

### Working now

- Upstream repository cloned cleanly into isolated subfolder.
- Required top-level structure is present (`ssc`, `prompting`, `llama`, `data`, `utils`).
- `.venv` interpreter is valid and runnable.
- Editor-level diagnostics did not report immediate unresolved imports in checked files.

### Starts but needs config

- None reached yet.
- Prompting likely needs API/base-URL configuration later, but current run does not reach that point.

### Blocked by environment

- `ssc` blocked by missing `peft` and `wuenlp`.
- `prompting` blocked by missing `langchain`.
- These are import-time dependency blockers, not model-logic failures.

### Blocked by unclear repository assumptions

- Commands are sensitive to working directory.
- Running from wrapper root fails local package resolution (`ssc`, `prompting`, `utils` not found).
- If Cursor interpreter is not `./.venv/bin/python`, this can become an additional blocker.

---

## Dependency-unblock update (minimal, reproducible, no training)

This update installs only the three previously missing modules and re-runs the same smoke commands.

### Install step performed

Baseline check command:

```bash
$PROJECT_ROOT/.venv/bin/python -m pip show peft langchain wuenlp
```

Baseline result:
- `peft` not found
- `langchain` not found
- `wuenlp` not found

Install command used:

```bash
$PROJECT_ROOT/.venv/bin/python -m pip install peft langchain "git+https://wuenlp.professor-x.de"
```

Installed package versions (post-install):
- `peft==0.18.1`
- `langchain==1.2.13`
- `WueNLP==0.6.9` (from `git+https://wuenlp.professor-x.de`, redirected to the WueNLP GitLab source)
- existing `transformers==5.4.0` remained in use

### Re-run of same import smoke commands

All re-tests were run from clone root:
`$PROJECT_ROOT/upstream/scene-segmentation`

1. Command:

```bash
$PROJECT_ROOT/.venv/bin/python -c "import ssc.model; print('OK ssc.model')"
```

Result: **failed**  
First stop: `TypeError: non-default argument 'embedding_model_name' follows default argument` from `transformers.configuration_utils` dataclass handling while defining `SSCModelConfig`.

Interpretation:
- Missing-package blocker is resolved.
- New blocker is framework/API compatibility between upstream `ssc/model.py` config class pattern and currently installed `transformers` behavior.

2. Command:

```bash
$PROJECT_ROOT/.venv/bin/python -c "import ssc.dataset; print('OK ssc.dataset')"
```

Result: **failed**  
First stop: same `TypeError` via `ssc.dataset -> ssc.model`.

Interpretation:
- `wuenlp` import now succeeds.
- `ssc` path is now blocked by the same `transformers` compatibility issue.

3. Command:

```bash
$PROJECT_ROOT/.venv/bin/python -c "import prompting.classify; print('OK prompting.classify')"
```

Result: **failed**  
First stop: `ModuleNotFoundError: No module named 'langchain.adapters'`.

Interpretation:
- `langchain` is installed, but upstream code expects an older `langchain` module layout that includes `langchain.adapters`.

### Re-run of same startup smoke commands

1. Command:

```bash
$PROJECT_ROOT/.venv/bin/python -m ssc.main --help
```

Result: **failed**  
First meaningful stop: same dataclass `TypeError` during import.
Classification: problematic stop before script logic.

2. Command:

```bash
$PROJECT_ROOT/.venv/bin/python -m ssc.train --help
```

Result: **failed**  
First meaningful stop: same dataclass `TypeError` during import.
Classification: problematic stop before script logic.

3. Command:

```bash
$PROJECT_ROOT/.venv/bin/python prompting/classify.py
```

Result: **failed**  
First meaningful stop: `ModuleNotFoundError: No module named 'langchain.adapters'`.
Classification: problematic stop before API/config checkpoint.

### Updated error reclassification

#### dependency error

1. `langchain.adapters` not found under installed `langchain==1.2.13`
- Area: `prompting`
- Root cause: dependency API/layout mismatch (upstream code written for older `langchain` interface).
- Blast radius: blocks prompting workflow startup.

#### interpreter / working-directory / import-resolution error

1. local package resolution still cwd-sensitive (unchanged)
- Area: `ssc`, `prompting`, `utils`
- Root cause: execution from wrapper root instead of clone root.
- Blast radius: can block all workflows if cwd is wrong.

#### unknown / needs deeper inspection

1. `SSCModelConfig` dataclass `TypeError` during `ssc.model` import
- Area: `ssc` (and anything importing `ssc.model`)
- Plain-English explanation: class definition fails before runtime because current `transformers` dataclass treatment rejects field ordering as interpreted from upstream config class.
- Likely root cause: compatibility mismatch between upstream code and installed `transformers` generation.
- Blast radius: blocks SSC import/startup path broadly.
- Status: likely environment compatibility issue, but requires version-compatibility check to confirm exact fix.

#### auth/API error

- Still not reached in prompting; import fails before credentials/base-URL handling.

#### CUDA/GPU error

- Not reached.

#### missing file/path error

- Not reached in this phase.

#### data format/parsing error

- Not reached in this phase.

### Updated concise summary after unblock attempt

#### Working now

- Clone and structure checks remain healthy.
- `.venv` interpreter usage remains correct.
- Previously missing packages `peft`, `WueNLP`, and `langchain` are now installed.
- Earlier missing-package import errors (`peft`, `wuenlp`, `langchain`) were moved forward to deeper checkpoints.

#### Starts but needs config

- None reached yet.
- Prompting still does not reach API key/base URL checkpoint due to import-level `langchain` API mismatch.

#### Blocked by environment

- `ssc`: blocked by `transformers` compatibility issue (`SSCModelConfig` dataclass error at import time).
- `prompting`: blocked by `langchain` module-layout mismatch (`langchain.adapters` missing in installed version).

#### Blocked by unclear repository assumptions

- Cwd sensitivity remains unchanged (must execute from clone root or set path explicitly).

---

## Strict full install update (upstream `requirements.txt`)

Requested action: install exactly from upstream requirements and re-run the same smoke commands.

### Install command and outcome

Command:

```bash
$PROJECT_ROOT/.venv/bin/python -m pip install -r "$PROJECT_ROOT/upstream/scene-segmentation/requirements.txt"
```

Result: **completed successfully** (`exit_code: 0`, elapsed about 312s).

Notable packages installed during strict run (in addition to prior minimal installs):
- `unsloth==2025.7.2`
- `trl==1.0.0`
- `bitsandbytes==0.49.2`
- `xformers==0.0.35`
- `torchvision==0.26.0`
- `cvxpy==1.8.2`
- `pygamma-agreement==0.5.9`

Observed key versions after strict install:
- `transformers==5.4.0` (unchanged)
- `langchain==1.2.13` (unchanged)
- `trl==1.0.0`
- `unsloth==2025.7.2`

### Re-run of the same import tests (strict environment)

All tests run from clone root with `.venv` Python.

1. `import ssc.model`:

```bash
$PROJECT_ROOT/.venv/bin/python -c "import ssc.model; print('OK ssc.model')"
```

Result: **failed**

First meaningful stop:
- `RuntimeError: operator torchvision::nms does not exist`
- Follow-on import failure:
  - `ModuleNotFoundError: Could not import module 'PreTrainedModel'.`

Likely cause:
- strict install introduced a `torch`/`torchvision` operator mismatch on this CPU environment; this now breaks `transformers` model imports at module import time.

2. `import ssc.dataset`:

```bash
$PROJECT_ROOT/.venv/bin/python -c "import ssc.dataset; print('OK ssc.dataset')"
```

Result: **failed** with same `torchvision::nms`/`PreTrainedModel` import chain (via `ssc.model`).

3. `import prompting.classify`:

```bash
$PROJECT_ROOT/.venv/bin/python -c "import prompting.classify; print('OK prompting.classify')"
```

Result: **failed**

First meaningful stop:
- `ModuleNotFoundError: No module named 'langchain.adapters'`

Likely cause:
- upstream prompting code expects an older `langchain` API layout than `langchain==1.2.13`.

### Re-run of the same script startup tests (strict environment)

1. `python -m ssc.main --help`:

```bash
$PROJECT_ROOT/.venv/bin/python -m ssc.main --help
```

Result: **failed** before script logic.

First meaningful stop:
- same `torchvision::nms` runtime error in `transformers` import chain.

Classification: problematic import-time environment failure.

2. `python -m ssc.train --help`:

```bash
$PROJECT_ROOT/.venv/bin/python -m ssc.train --help
```

Result: **failed** before script logic.

First meaningful stop:
- same `torchvision::nms` runtime error and downstream `TrainingArguments` import failure from `transformers`.

Classification: problematic import-time environment failure.

3. `python prompting/classify.py`:

```bash
$PROJECT_ROOT/.venv/bin/python prompting/classify.py
```

Result: **failed** before script logic.

First meaningful stop:
- `ModuleNotFoundError: No module named 'langchain.adapters'`

Classification: problematic import-time dependency API mismatch.

### Updated classification after strict full install

#### dependency error

1. `langchain.adapters` missing in installed `langchain==1.2.13`
- Area: `prompting`
- Root cause: API/layout mismatch with code expectations.
- Blast radius: blocks prompting startup.

#### CUDA/GPU / framework binary compatibility error

1. `torchvision::nms` operator missing during `transformers` import
- Area: `ssc` (and imports through `transformers`)
- Root cause (likely): `torch`/`torchvision` compatibility issue in current environment.
- Blast radius: blocks SSC imports and SSC script startup.

#### interpreter / working-directory / import-resolution error

- Cwd sensitivity still applies (must run from clone root).

#### auth/API error

- Still not reached; prompting does not progress to credential handling.

#### missing file/path error

- Still not reached.

#### data format/parsing error

- Still not reached.

#### unknown / needs deeper inspection

- The exact `torch`/`torchvision` pairing expected by upstream stack on this machine likely needs confirmation, but the failure category is clear.

### Strict install summary

#### Working now

- Strict upstream installation completed in `.venv`.
- More dependencies are present than before; early missing-package blockers were not the primary remaining issue.

#### Starts but needs config

- None reached yet.

#### Blocked by environment

- `ssc` blocked by `torch`/`torchvision`/`transformers` import chain compatibility (`torchvision::nms` missing).
- `prompting` blocked by `langchain` API mismatch (`langchain.adapters` missing).

#### Blocked by unclear repository assumptions

- Cwd/project-root assumption remains unchanged and still important.

---

## Compatibility pinning pass (no code changes)

Date: 2026-03-31

### Objective

Resolve import-time failures via minimal dependency version pinning only, without modifying upstream code or running training.

### Pass 1: torch/torchvision and langchain

#### Problem

1. `torchvision::nms` operator missing — torch/torchvision version mismatch.
2. `ModuleNotFoundError: langchain.adapters` — langchain 1.x restructured module layout.

#### Resolution

Updated `requirements-basic.txt` to pin:

```
--extra-index-url https://download.pytorch.org/whl/cpu

torch==2.5.1+cpu
torchvision==0.20.1+cpu
langchain==0.1.9
```

#### Verification

```bash
source .venv/bin/activate
pip install -r requirements-basic.txt
python -c "import torch, torchvision; from torchvision.ops import nms; print('nms_ok', callable(nms))"
python -c "import langchain.adapters; print('HAS_ADAPTERS')"
```

Results:
- `torch 2.5.1+cpu`, `torchvision 0.20.1+cpu` — compatible pair confirmed.
- `langchain.adapters` import — **PASS**.

### Pass 2: transformers dataclass compatibility

#### Problem

`TypeError: non-default argument 'embedding_model_name' follows default argument` during `import ssc.model`.

Root cause: `transformers>=5.0` auto-converts `PretrainedConfig` subclasses to dataclasses, breaking upstream field ordering.

#### Resolution

Downgraded transformers in `requirements-basic.txt`:

```
transformers==4.46.3
```

#### Verification

```bash
source .venv/bin/activate
pip install -r requirements-basic.txt
cd upstream/scene-segmentation
python -c "import ssc.model; print('OK ssc.model')"
python -c "import prompting.classify; print('OK prompting.classify')"
```

Results:
- `import ssc.model` — **PASS**.
- `import prompting.classify` — **PASS**.

### Remaining failures after pinning (CPU environment)

| Command | Result | Reason |
|---------|--------|--------|
| `import ssc.dataset` | FAIL | Unsloth raises `NotImplementedError` on CPU-only torch |
| `python -m ssc.main --help` | FAIL | Same Unsloth GPU check |
| `python -m ssc.train --help` | FAIL | Same Unsloth GPU check |
| `python prompting/classify.py` | FAIL | `ModuleNotFoundError: utils` (path issue when running script directly) |

These are expected: Unsloth requires GPU, and script execution needs correct `PYTHONPATH` or cwd.

### Commits

- `3525715` — Pin CPU-compatible torch/vision and langchain/transformers for smoke tests.
- `9848021` — Document install command behavior and ignore local GPU artifacts.

---

## GPU environment setup

Date: 2026-03-31

### Objective

Create a separate GPU-enabled environment for Unsloth training workflows.

### System verification

Commands run:

```bash
nvidia-smi -L
nvidia-smi --query-gpu=name,driver_version,vbios_version,memory.total,compute_cap --format=csv,noheader
nvcc --version
```

Results:
- GPU: NVIDIA GeForce RTX 2070 with Max-Q Design
- Driver: 580.126.09
- CUDA (driver): 13.0
- CUDA Toolkit (nvcc): 12.0.140
- Compute capability: 7.5
- VRAM: 8192 MiB

### Environment creation

```bash
cd $PROJECT_ROOT
python3 -m venv .venv-gpu
source .venv-gpu/bin/activate
pip install --upgrade pip setuptools wheel
```

### PyTorch GPU installation

Initial approach (explicit CUDA 12.4 wheels):

```bash
pip install --index-url https://download.pytorch.org/whl/cu124 \
  torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1
```

Final state (after Unsloth pulled newer versions):

```bash
pip install unsloth unsloth-zoo
```

Unsloth upgraded torch to `2.10.0+cu128` and pulled compatible dependencies.

### Final resolved versions

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

### Validation

```bash
source .venv-gpu/bin/activate
python -c "import torch; print(torch.__version__, torch.version.cuda, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

Output:
```
2.10.0+cu128 12.8 True NVIDIA GeForce RTX 2070 with Max-Q Design
```

```bash
python -c "import unsloth; print('unsloth', unsloth.__version__)"
```

Output:
```
🦥 Unsloth: Will patch your computer to enable 2x faster free finetuning.
🦥 Unsloth Zoo will now patch everything to make training faster!
unsloth 2026.3.18
```

### Cleanup

Removed incompatible torchaudio:

```bash
pip uninstall -y torchaudio
```

### Known warnings

1. `Skipping import of cpp extensions due to incompatible torch version. Please upgrade to torch >= 2.11.0`
   - Cause: Unsloth C++ extensions expect torch >= 2.11; current is 2.10.0.
   - Impact: Training works via Python fallback; some speed optimizations unavailable.

2. Import order warning:
   - Unsloth should be imported before `transformers`, `trl`, `peft` in scripts.

### Git-ignored artifacts

Added to `.gitignore`:
```
.venv-gpu/
unsloth_compiled_cache/
gpu_env_report.txt
outputs/artifacts/logs/gpu_env_report.txt
```

---

## Summary: two-environment strategy

| Environment | Location | Purpose | torch | transformers |
|-------------|----------|---------|-------|--------------|
| `.venv` | project root | CPU smoke tests | 2.5.1+cpu | 4.46.3 |
| `.venv-gpu` | project root | GPU training | 2.10.0+cu128 | 4.52.4 |

This separation avoids dependency conflicts between SSC smoke-test compatibility requirements and Unsloth training requirements.

See `docs/setup/ENVIRONMENT_SETUP.md` for full setup instructions and quick reference commands.
