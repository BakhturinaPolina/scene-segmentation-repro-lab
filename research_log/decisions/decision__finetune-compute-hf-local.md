---
note_type: decision
decision_id: finetune_compute_hf_local
title: "Fine-tuning compute: Hugging Face Hub + local GPU (Kaggle deprecated)"
date: 2026-06-09
decision_type: process
status: active
decision_statement: "All new fine-tuning runs use Hugging Face Hub for datasets and adapters, with local CUDA GPU as the default compute path; HF Jobs cloud GPUs are optional fallback only."
reasoning_summary: "HF Pro ($9/mo) covers private dataset storage and Hub publishing but does not include Jobs GPU credits. The developer machine has an RTX 2070 (8 GB) suitable for 3B QLoRA. Local runs cost $0 extra vs ~$35–50 prepaid credits for the full matrix on t4-small Jobs."
related_experiments:
  - experiment__finetune__hf-jobs-qlora-campaign
related_runs: []
related_artifacts: []
evidence_strength: moderate
follow_up_action: "Run E0 smoke locally; use COMPUTE=jobs only if 8B repro OOMs on 8 GB VRAM."
notion_targets:
  decisions: true
  runs: true
  artifacts: true
  experiments: true
---

## Context

The original plan (`FINETUNING_EXPERIMENTS_PLAN.md`, Kaggle edition) targeted free Kaggle T4 GPUs
(30 h/week, 12 h session cap). The user has HF Pro ($9/month) and prefers minimal extra spend.

## Evidence

- HF Pro unlocks private repos and Jobs API but Jobs billing is **prepaid credits**, not included in
  the subscription ([HF billing docs](https://huggingface.co/docs/hub/en/billing)).
- Local hardware: NVIDIA RTX 2070 Max-Q, 8 GB VRAM — sufficient for 3B QLoRA with `batch_size=1`.
- Existing `train_kernel.py` logic ported to `src/finetune/hf_jobs/train_job.py` with dual local/cloud
  entry points.
- Kaggle path added maintenance overhead (API token, dataset versioning, session time guards) without
  cost advantage once HF Hub is the artifact store anyway.

## Decision

1. **Deprecate** `src/finetune/kaggle/` for new runs.
2. **Default compute:** local GPU via `submit_job.sh` (`COMPUTE=local`).
3. **Data + artifacts:** private HF dataset `{user}/scene-seg-sft`; public adapter repos
   `{user}/scene-seg-{model}-{job}`.
4. **Cloud fallback:** `COMPUTE=jobs FLAVOR=t4-small` when local VRAM insufficient (8B stretch).

## Why this is the current standard

- Total marginal cost for the core 3B matrix = **$0** beyond HF Pro.
- Same experiment matrix, metrics, and logging rules as the Kaggle plan.
- HF Hub is already the destination for adapters; removing Kaggle simplifies the pipeline.

## Consequences

- Wall-clock for the full matrix is ~1–2 weeks of local GPU time (serial), vs ~2 weeks calendar on
  Kaggle free quota.
- 8B paper repro (E8) may require prepaid Jobs credits or aggressive memory settings locally.
- Run notes should record `compute: local|jobs` and Job URL when applicable.

## Follow-up

- Execute E0 smoke with `RUN_CONFIG=src/finetune/hf_jobs/configs/E0_smoke.json`.
- Mark `experiment__finetune__kaggle-qlora-campaign` as superseded by
  `experiment__finetune__hf-jobs-qlora-campaign`.
