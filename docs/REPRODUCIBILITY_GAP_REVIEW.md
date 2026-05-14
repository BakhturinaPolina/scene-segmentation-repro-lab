# Reproducibility Gap Review (Scene Segmentation)

Date: 2026-05-14
Scope reviewed: `research_log/` (runs, issues, artifacts, experiments, sync notes) and current workflow docs.

## Assumed target of "fully reproduce"

This review assumes "fully reproduce" means:

1. Re-run all three upstream workflow families (`ssc`, `prompting`, `llama`) from documented commands.
2. Regenerate comparable metrics with explicit environment/model/data provenance.
3. Reproduce without hidden local state beyond documented requirements.

If the intended target is narrower (for example, prompting-only reproduction), some gaps below become optional.

## Current baseline status from logs

- `prompting`: reproducible for STSS-Test-2 smoke runs (Phase 4 wrappers exist and default to a pinned OpenRouter free model).
- `ssc`: pipeline can run, but current baseline quality is not representative (`F1 ~= 0.009`) and depends on upstream patching history.
- `llama`: not reproducible as a successful training baseline on local hardware (OOM on RTX 2070 8GB).

## Missing data assets

1. **Missing paper-aligned evaluation corpus (Test-Full)**
   - Logs state only STSS-Test-2 is locally available.
   - Impact: cannot fully reproduce paper-level comparisons; only partial replication on STSS-Test-2.

2. **Dataset manifest added (closed)**
   - `data/manifest_stss_test_2.json` now tracks STSS-Test-2 file names, sizes, and checksums.
   - `src/verify_data_manifest.py` validates local files against the manifest.

3. **No pinned split/selection specification for SSC training-quality baseline**
   - Existing SSC baseline uses train/test on same folder for smoke execution.
   - Impact: cannot reproduce a scientifically meaningful supervised baseline comparable to reported literature numbers.

4. **No reproducible data extraction proof for LLaMA labels**
   - LLaMA dry run reports all-NOBORDER extraction and flags data-conversion uncertainty.
   - Impact: fine-tuning target labels may be incorrect or incomplete, blocking valid reproduction.

## Missing scripts and automation

1. **SSC/LLaMA wrappers added (closed)**
   - `src/run_ssc_baseline.py` and `src/run_llama_baseline.py` now provide Phase 4-style wrapper entrypoints with repro artifacts.
   - Impact reduced: cross-track run metadata is now standardized.

2. **End-to-end entrypoint added (closed)**
   - `src/reproduce_stss_test_2.py` orchestrates validation and run steps and writes a reproduction manifest.

3. **No automated patch/bootstrap step for upstream compatibility changes**
   - SSC run notes mention required upstream fixes (collator, argument rename, etc.), but these are not captured as a reproducible patch application flow in this repo.
   - Impact: a fresh clone may fail unless a user reconstructs manual edits.

4. **No scripted artifact integrity check**
   - Reproducibility rules require standard files (`stdout.log`, `stderr.log`, `metrics.json`, etc.), but enforcement is manual.
   - Impact: runs can appear complete while missing required evidence files.

## Missing model specifications / model availability controls

1. **Prompting default model deprecation fixed (closed)**
   - Active defaults removed `qwen/qwen3.6-plus:free` and now pin `nvidia/nemotron-3-super-120b-a12b:free`.

2. **No frozen model inventory snapshot for OpenRouter experiments (open)**
   - Free-tier model availability is dynamic; experiments rely on provider state at runtime.
   - Impact: identical commands may not target equivalent models on later dates.

3. **LLaMA baseline path standardized, success pending execution evidence (partially closed)**
   - Wrapper now defaults to a smaller 4-bit model (`unsloth/Phi-3-mini-4k-instruct-bnb-4bit`) with conservative batch settings for 8 GB VRAM.
   - Remaining gap: a confirmed successful run note under this new configuration.

4. **No paper-comparable SSC baseline model run**
   - Current executed SSC baseline is `bert-base-german-cased` smoke-style; paper-referenced stronger baselines are not reproduced locally.
   - Impact: full-project reproduction of benchmark claims remains incomplete.

## Minimal must-have checklist to close critical gaps

1. Define reproduction target explicitly in docs: **STSS-Test-2-only** vs **paper-comparable**.
2. Keep `data/manifest_stss_test_2.json` updated when data assets change.
3. Keep `src/run_ssc_baseline.py` and `src/run_llama_baseline.py` aligned with upstream argument changes.
4. Add reproducible upstream patch application flow (script or tracked patch files).
5. Maintain a periodic free-model snapshot and record the snapshot date in run notes.
6. Complete one successful LLaMA baseline run note with the new smaller-model wrapper defaults.
7. Keep `src/reproduce_stss_test_2.py` as the canonical run-manifest entrypoint.

## Conclusion

The project now has the core building blocks for **STSS-Test-2-only reproducibility** (manifest verification, wrapper scripts, and orchestration). Remaining risk is mostly operational (provider free-model drift and confirming successful LLaMA run execution under the new smaller-model default).
