---
note_type: sync_note
sync_id: sync_20260331_phase0_phase2_setup
date: 2026-03-31
title: "Phase 0-2 complete: repo init, clone, smoke tests, dual-env setup"
track: cross-project
work_block_type: setup
runs_created:
  - "run_20260331_initial_import_tests"
  - "run_20260331_post_dep_install_imports"
  - "run_20260331_strict_upstream_install"
  - "run_20260331_cpu_pinned_final"
  - "run_20260331_gpu_env_validation"
artifacts_created:
  - "art_gpu_env_report"
  - "art_cpu_pinned_requirements"
issues_created:
  - "issue_transformers_dataclass_compat"
  - "issue_langchain_adapters_missing"
  - "issue_torchvision_nms_mismatch"
  - "issue_working_directory_sensitivity"
  - "issue_unsloth_cpp_extensions_skip"
decisions_created:
  - "decision_dual_environment_strategy"
  - "decision_cpu_env_version_pins"
  - "decision_upstream_isolation"
experiments_updated: []
roadmap_updates:
  - "Phase 0 (repo setup) — completed"
  - "Phase 1 (clone + inspect) — completed"
  - "Phase 2 (smoke tests) — completed"
  - "Phase 3 (baseline execution) — not started, next priority"
notion_sync_priority: high
---

## What was done

Full project initialization and environment validation in one work session (2026-03-31):

1. **Phase 0**: Created research wrapper repository with standard folder structure, `.gitignore`, `README.md`, `PROJECT_PLAN.md`.

2. **Phase 1**: Cloned `LSX-UniWue/scene-segmentation` into `upstream/scene-segmentation/`. Verified directory structure (`ssc/`, `prompting/`, `llama/`, `data/`, `utils/`).

3. **Phase 2 (smoke tests)**: Ran 4 sequential smoke test rounds:
   - Initial imports → all failed (missing peft, wuenlp, langchain)
   - After minimal dep install → new failures (transformers dataclass, langchain.adapters)
   - After strict upstream install → still failing (torchvision::nms, langchain.adapters)
   - After compatibility pinning → ssc.model PASS, prompting.classify PASS

4. **GPU environment**: Created `.venv-gpu` with Unsloth stack. Validated CUDA detection and import.

5. **Documentation**: Wrote `docs/ENVIRONMENT_SETUP.md` and `docs/PHASE2_PHASE3_NOTES.md` with full command logs.

## Main result

- CPU environment (`.venv`) is healthy for SSC model and prompting import validation
- GPU environment (`.venv-gpu`) is healthy for Unsloth/training workflows
- Three dependency compatibility issues were identified and resolved via version pinning
- Two open issues remain: working directory sensitivity (medium) and Unsloth C++ extensions skip (low, non-blocking)

## What needs syncing to Notion

| Notion database | Items to sync |
|-----------------|---------------|
| Roadmap | Phase 0, 1, 2 marked complete; Phase 3 next |
| Runs | 5 run notes (all smoke tests + GPU validation) |
| Issues | 5 issue notes (3 resolved, 2 open) |
| Decisions | 3 decision notes (dual env, version pins, upstream isolation) |
| Artifacts | 2 artifact notes (GPU report, requirements file) |
| Environments | CPU env (.venv) and GPU env (.venv-gpu) descriptions |

## What remains unresolved

- `issue_working_directory_sensitivity` — ongoing constraint, no fix applied
- `issue_unsloth_cpp_extensions_skip` — non-blocking, awaiting upstream torch update
- Phase 3 baseline execution not yet started for any track

## Next step

Begin Phase 3: baseline execution starting with SSC (GPU environment), then prompting (needs API credentials), then llama (dry run).
