# Experiment Performance Report

Date: 2026-04-09  
Scope: All experiment types already executed and logged in this workspace.

## 1) Executive Summary

- Best validated prompting baseline so far is `nvidia/nemotron-3-super-120b-a12b:free` with macro `F1@tol0=0.753` on full stratified sample (`n=892`).
- `openai/gpt-oss-120b:free` is highly conservative (perfect precision, low recall), yielding lower macro `F1@tol0=0.696` on pilot stratified sample (`n=60`).
- SSC supervised baseline (`bert-base-german-cased`, 1 epoch) runs end-to-end but is not yet competitive (`average_f1=0.0089`, recall bottleneck).
- LLaMA/Unsloth 8B dry run is currently blocked by VRAM constraints on RTX 2070 Max-Q (OOM at first step with batch size 20).
- Recent prompt-family reruns indicate family `I` is materially stronger than family `H` under the same setup, but both are very small-sample results (`n=10` total each).

## 2) Performance Matrix by Experiment Type

| Type | Run / Variant | Main metric | Value | Sample size | Runtime | Status |
|---|---|---:|---:|---:|---:|---|
| Prompting baseline | `qwen/qwen3.6-plus:free` (OpenRouter) | Accuracy | 1.00 | 20 sentences | 449s | Success |
| Prompting model comparison (pilot) | `openai/gpt-oss-120b:free` | Macro F1@tol0 | 0.696 | 60 stratified | ~4 min | Success |
| Prompting model comparison (full) | `nvidia/nemotron-3-super-120b-a12b:free` | Macro F1@tol0 | 0.753 | 892 stratified | ~3 h | Success |
| SSC baseline | `bert-base-german-cased` (1 epoch) | Average F1 | 0.0089 | stss_test_2 | 3401s | Success (weak model) |
| LLaMA dry run | `unsloth/llama-3-8b-bnb-4bit` | N/A | OOM | N/A | 893s | Partial/Failed training |
| Prompt family rerun | Family `I` (`openrouter/free`, reasoning=low) | Macro F1@tol0 | 0.500 | 10 stratified | ~364s | Success |
| Prompt family rerun | Family `H` (`openrouter/free`, reasoning=low) | Macro F1@tol0 | 0.000 | 10 stratified | ~499s | Success (unstable retries) |

## 3) Prompting Track Details

### 3.1 Model-level comparison (same task family/prompting pipeline)

| Model | Precision@tol0 | Recall@tol0 | F1@tol0 | F1@tol3 | Notes |
|---|---:|---:|---:|---:|---|
| `openai/gpt-oss-120b:free` | 1.000 | 0.533 | 0.696 | 0.696 | No false positives; many missed borders |
| `nvidia/nemotron-3-super-120b-a12b:free` (pilot) | 0.873 | 0.667 | 0.753 | 0.820 | Better recall, moderate FP tradeoff |
| `nvidia/nemotron-3-super-120b-a12b:free` (full stratified) | 0.890 | 0.652 | 0.753 | 0.792 | Pilot F1 matched full F1@tol0 |

### 3.2 Prompt-family reruns on `openrouter/free` (recent)

Configuration used for comparability:
- `reasoning=low`, `temperature=0.0`, `top_p=1.0`, `max_tokens=256`, `dry_run=5`, stratified.

| Family | Macro F1@tol0 | Avg parse failure rate | Avg output chars | Avg latency (s) | Observed behavior |
|---|---:|---:|---:|---:|---|
| `I` | 0.500 | 0.00 | 166.1 | 22.962 | Better quality, still occasional retries |
| `H` | 0.000 | 0.10 | 1.5 | 32.910 | Heavy retry churn; one forced fallback case |

## 4) SSC Track Details

Run: `bert-base-german-cased`, coarse labels, 1 epoch, batch size 1.

- Train loss: `0.386`
- Eval (during training): high accuracy but near-zero border detection (`F1=0.0`)
- Pipeline-level tolerance evaluation: `average_f1=0.0089`, `precision=1.0`, `recall=0.0045`

Interpretation:
- The pipeline is operational, but this configuration is not yet a meaningful performance baseline.
- Class imbalance + short training + architecture constraints dominate outcomes.

## 5) LLaMA / Unsloth Track Details

Run: `unsloth/llama-3-8b-bnb-4bit` dry run on RTX 2070 Max-Q (8 GB).

- Model and data loading succeeded.
- Failed at first training step due to CUDA OOM.
- No valid training metrics produced.

Interpretation:
- Current local VRAM is insufficient for the tested batch regime.
- Requires smaller effective batch, smaller model, or stronger GPU.

## 6) Environment/Infrastructure Runs (Cross-project smoke)

These runs validate compatibility and setup, not model performance:
- Initial import smoke: failed due to missing dependencies.
- Post-install smoke: failed due to version/API incompatibilities.
- Strict upstream requirements install: still failed (torchvision/langchain incompatibility issues).
- CPU pinned environment: dependency mismatch resolved; GPU-required paths still unavailable.
- GPU environment validation: successful CUDA + Unsloth import validation.

## 7) Reliability and Comparability Notes

- Not all rows are directly comparable:
  - Prompting model comparison uses different sample scales (`n=60` vs `n=892`).
  - Prompt-family H/I reruns are tiny samples (`n=10`) and should be treated as directional only.
  - SSC and prompting are different paradigms (supervised vs zero-shot prompting).
- The old Phase A manifest at `outputs/prompting/2026-04-09/phase_a_manifest.json` reflects pre-fix failures (`reasoning=off`) and should not be used as current performance evidence.

## 8) Recommended Next Experiments (Performance-focused)

1. Standardize a single prompting benchmark slice (fixed `n`, same docs, same tolerance set) and rerun top 2 models + top 2 prompt families.
2. For SSC, run a stronger but still affordable baseline (more epochs, better imbalance handling) before comparing to prompting.
3. For LLaMA, run feasibility experiment with `batch_size=1` + gradient accumulation and explicit VRAM logging.
4. Add confidence intervals or at least multi-seed repeats for pilot-sized (`n<=60`) comparisons.

## 9) Primary Sources Used

- `research_log/runs/2026-04-05__prompting__baseline__qwen3-openrouter.md`
- `research_log/runs/2026-04-08__prompting__baseline__gptoss120b-stratified.md`
- `research_log/runs/2026-04-08__prompting__baseline__nemotron-stratified.md`
- `research_log/experiments/experiment__prompting__model__free-120b-comparison.md`
- `research_log/runs/2026-04-05__ssc__baseline__bert-german-cased.md`
- `research_log/runs/2026-04-05__llama__dry-run__unsloth-8b.md`
- `research_log/runs/2026-03-31__cross-project__smoke__*.md`
- `outputs/prompting/2026-04-09-i-rerun/strat_openrouter_free_familyI_reasoning-low/summary.json`
- `outputs/prompting/2026-04-09-h-rerun/strat_openrouter_free_familyH_reasoning-low/summary.json`
- `outputs/prompting/2026-04-09/phase_a_manifest.json` (historical failure manifest)
