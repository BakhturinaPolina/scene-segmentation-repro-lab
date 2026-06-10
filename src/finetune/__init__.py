"""Fine-tuning pipeline for scene-boundary detection.

Modules:
- ``build_sft_dataset``: build leakage-safe leave-one-text-out SFT datasets
  (CoT-List supervision) from STSS-Test-2 XMI gold + Excel gold.
- ``eval_finetuned``: score a fine-tuned adapter on a held-out fold with the
  same tolerant F1 metric as the prompting runner.

Training and eval live under ``finetune/hf_jobs/`` (local GPU or optional HF Jobs).
The legacy Kaggle kernel under ``finetune/kaggle/`` is deprecated.
"""
