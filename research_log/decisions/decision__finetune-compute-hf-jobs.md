---
note_type: decision
decision_id: finetune_compute_hf_jobs
title: "Fine-tuning compute: HF Jobs cloud GPUs as default"
date: 2026-06-09
decision_type: process
status: active
decision_statement: "All fine-tuning GPU work runs on Hugging Face Jobs (`COMPUTE=jobs`, `t4-small` default); local CUDA GPU is not used for this campaign."
reasoning_summary: "No local GPU path for the fine-tuning campaign. HF Jobs prepaid credits (~$34–45 for the full matrix) replace local RTX 2070 training. Data build remains on local CPU; adapters and metrics publish to HF Hub as before."
related_experiments:
  - experiment__finetune__hf-jobs-qlora-campaign
related_runs: []
related_artifacts: []
evidence_strength: moderate
follow_up_action: "Run E0 smoke on Jobs; add prepaid credits before core matrix."
notion_targets:
  decisions: true
  runs: true
  artifacts: true
  experiments: true
---

## Context

[`decision__finetune-compute-hf-local.md`](decision__finetune-compute-hf-local.md) (2026-06-09) set local GPU
as the default compute path to minimize cost. The campaign will not use local GPU training; all train + in-job
eval runs go through HF Jobs.

Kaggle path removed; single entry point is `src/finetune/hf_jobs/submit_job.sh`.

## Evidence

- Full matrix on `t4-small`: ~82–106 GPU-h, ~$34–45 prepaid credits (see
  `docs/planning/FINETUNING_EXPERIMENTS_PLAN.md` §0).
- HF Pro ($9/mo) covers private dataset storage and Jobs API; GPU time is prepaid only.
- `submit_job.sh` default changed from `COMPUTE=local` to `COMPUTE=jobs`.

## Decision

1. **Default compute:** HF Jobs via `submit_job.sh` (`COMPUTE=jobs`, `FLAVOR=t4-small`).
2. **8B stretch (E8):** `FLAVOR=t4-medium` (~$0.60/hr).
3. **Local override:** `COMPUTE=local` remains available but is not the campaign default.
4. **Data build:** local CPU only (`build_sft_dataset.py`); no GPU required.
5. **Kaggle:** removed from codebase; historical experiment notes retained.

## Why this is the current standard

- Aligns compute choice with actual execution environment (cloud-only).
- Simplifies run notes: every submission records a Jobs URL.
- Cost is bounded and predictable (~$34–45 beyond HF Pro).

## Consequences

- Prepaid credits required before submitting Jobs (~$35–45 for pilot + core matrix + E8).
- Serial wall-clock ~3–4 days at 24/7; parallel submissions reduce calendar time, not credit spend.
- Run notes must record `compute: jobs`, Job URL, and `FLAVOR`.

## Follow-up

- Execute E0 smoke: `RUN_CONFIG=configs/E0_smoke.json`, `TIMEOUT=2h`.
- Supersedes local-default follow-up in `decision__finetune-compute-hf-local.md`.
