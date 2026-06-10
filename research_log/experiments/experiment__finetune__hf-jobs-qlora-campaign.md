---
note_type: experiment
experiment_id: finetune_hf_jobs_qlora_campaign
title: "HF Hub QLoRA fine-tuning campaign for scene-boundary detection"
date_opened: 2026-06-09
track: llama
status: active
factor_under_test: "fine-tuning configuration (base model, target format, negatives, context, capacity)"
baseline_run_id: ""
hypothesis: "A small (3B) QLoRA-fine-tuned model trained on local GPU with HF Hub artifacts can beat our prompting natural-distribution baseline (F1@3 ~ 0.51) and approach the paper's fine-tuned Llama3:8b CoT-List result (F1@3 = 0.62-0.63), at HF Pro cost only ($9/mo, $0 extra GPU)."
fixed_conditions:
  - "train split = train_full; eval split = stss_test_2 (natural distribution)"
  - "seed = 1337"
  - "LoRA r=16, alpha=16, dropout=0, 7 target modules (q/k/v/o/gate/up/down)"
  - "epochs=1, lr=2e-4, optim=adamw_8bit, cosine schedule, warmup_ratio=0.05"
  - "max_seq_len=1024; eval = greedy, batched, max_new_tokens=96"
  - "metric = relaxed F1, macro-averaged per text, tolerances 0/1/3"
  - "compute default = local RTX 2070 8GB; HF Jobs t4-small optional fallback"
  - "data + adapters on HF Hub (private dataset scene-seg-sft, public adapter repos)"
variants:
  - "E0 smoke: Llama-3.2-3B, eval_limit 200 (pipeline check)"
  - "E1 anchor: Llama-3.2-3B, cot_list, paper10pct negatives"
  - "E2 model family: Qwen2.5-3B, Gemma-2-2B"
  - "E3 target format: cot_list vs json vs no_cot"
  - "E4 negatives: paper10pct vs ratio(3:1) vs hard"
  - "E5 context: 4 sentences vs tokens512"
  - "E6 capacity: epochs=2; lora_r=32 (best config only)"
  - "E7 post-processing: none vs min_scene_len_3 vs confidence_threshold_plus_min_scene_len_3"
  - "E8 stretch: Llama-3-8B paper repro; eval on test_full; two-stage verifier"
success_metric: "relaxed F1@3 on STSS-Test-2 (macro over texts), then on test_full"
comparison_rule: "One factor changed at a time vs the E1 anchor; promote a change only if F1@3 improves without a material recall@0 collapse."
related_runs: []
related_artifacts: []
notion_targets:
  experiments: true
  runs: true
  artifacts: true
  decisions: true
---

## Research question

Can QLoRA fine-tuning on a local 8 GB GPU with Hugging Face Hub for data and artifacts match or beat
both our prompting natural-distribution baseline and the paper's fine-tuned Llama3:8b on relaxed F1@3
for German scene-boundary detection?

Full plan: [`../../docs/planning/FINETUNING_EXPERIMENTS_PLAN.md`](../../docs/planning/FINETUNING_EXPERIMENTS_PLAN.md).

Supersedes: [`experiment__finetune__kaggle-qlora-campaign.md`](experiment__finetune__kaggle-qlora-campaign.md).

## Baseline

External anchors (paper, relaxed F1@3):
- Llama3:8b CoT-List fine-tuned: STSS-Test-2 = 0.63, Test-Full = 0.62 (Table 3).
- Llama3:8b No-CoT fine-tuned: Test-Full = 0.09 (Table 3).
- GBERT-Large + Half-Stride (best supervised): STSS-Test-2 = 0.66, Test-Full = 0.68 (Table 1).

Internal anchor: prompting on the true ~4%-border distribution reaches F1@3 ~ 0.31 raw / ~0.51 with
post-processing (partial). The E1 run becomes the in-campaign baseline once available.

## Constants

See `fixed_conditions` above. Splits in
[`../../data/manifests/finetune_splits.json`](../../data/manifests/finetune_splits.json).
Data built by [`../../src/finetune/build_sft_dataset.py`](../../src/finetune/build_sft_dataset.py).

## Variants

See `variants` above. Data-side factors require `build_sft_dataset.py` rebuild; training-side factors
change config JSON or `submit_job.sh` env vars.

## Evaluation rule

After each training, on the full held-out split at natural distribution (or `eval_limit` for E0).
[`../../src/finetune/hf_jobs/train_job.py`](../../src/finetune/hf_jobs/train_job.py) reports macro/micro
relaxed F1 at tolerances 0/1/3 per post-processing scenario; uploads `metrics_<model>_<job>.json` to the
adapter repo. Headline = `scenarios.none.tol_3.macro_f1`.

## Interim conclusion

2026-06-09: Migrated from Kaggle to HF Hub + local GPU. Pipeline code ready (`train_job.py`,
`submit_job.sh`, E0/E1 configs). No training run executed yet. Next: E0 smoke locally.

## Final conclusion

(pending)
