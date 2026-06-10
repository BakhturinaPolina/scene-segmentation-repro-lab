# Deprecated: Kaggle fine-tuning kernel

This directory is **no longer used**. The project switched to Hugging Face Hub for data, adapters, and
compute orchestration.

**Use instead:**

- [`../hf_jobs/train_job.py`](../hf_jobs/train_job.py) — training + eval script
- [`../hf_jobs/submit_job.sh`](../hf_jobs/submit_job.sh) — build, upload, run (local GPU by default)
- [`../../../docs/planning/FINETUNING_EXPERIMENTS_PLAN.md`](../../../docs/planning/FINETUNING_EXPERIMENTS_PLAN.md)

These files are kept for reference and reproducibility of the original Kaggle-based plan.
