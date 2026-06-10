---
note_type: experiment
experiment_id: finetune_kaggle_qlora_campaign
title: "Kaggle QLoRA fine-tuning campaign for scene-boundary detection"
date_opened: 2026-06-09
track: llama
status: concluded
factor_under_test: "fine-tuning configuration (base model, target format, negatives, context, capacity)"
baseline_run_id: ""
hypothesis: "A free, small (3B) QLoRA-fine-tuned model can beat our prompting natural-distribution baseline (F1@3 ~ 0.51) and approach the paper's fine-tuned Llama3:8b CoT-List result (F1@3 = 0.62-0.63), at zero cost on Kaggle T4."
fixed_conditions:
  - "train split = train_full; eval split = stss_test_2 (natural distribution)"
  - "seed = 1337"
  - "LoRA r=16, alpha=16, dropout=0, 7 target modules (q/k/v/o/gate/up/down)"
  - "epochs=1, lr=2e-4, optim=adamw_8bit, cosine schedule, warmup_ratio=0.05"
  - "max_seq_len=1024; eval = greedy, batched, max_new_tokens=96"
  - "metric = relaxed F1, macro-averaged per text, tolerances 0/1/3"
  - "compute = Kaggle T4 16GB free; adapters + metrics pushed to HF Hub"
variants:
  - "E0 smoke: Llama-3.2-3B, eval_limit 200 (pipeline check)"
  - "E1 anchor: Llama-3.2-3B, cot_list, paper10pct negatives"
  - "E2 model family: Qwen2.5-3B, Gemma-2-2B"
  - "E3 target format: cot_list vs json vs no_cot"
  - "E4 negatives: paper10pct vs ratio(3:1) vs hard"
  - "E5 context: 4 sentences vs tokens512"
  - "E6 capacity: epochs=2; lora_r=32 (best config only)"
  - "E7 post-processing: none vs min_scene_len_3 vs confidence_threshold_plus_min_scene_len_3 (reported in-kernel)"
  - "E8 stretch: Llama-3-8B paper repro; eval on test_full; two-stage verifier"
success_metric: "relaxed F1@3 on STSS-Test-2 (macro over texts), then on test_full"
comparison_rule: "One factor changed at a time vs the E1 anchor; promote a change only if F1@3 improves without a material recall@0 collapse."
related_runs: []
related_artifacts: []
notion_targets:
  experiments: true
  runs: true
  artifacts: true
  decisions: false
---

## Research question

Can free, small QLoRA fine-tuning (Kaggle T4, <=3B models) match or beat both our own prompting
baseline and the paper's fine-tuned Llama3:8b on relaxed F1@3 for German scene-boundary detection, and
in doing so close the fine-tuning reproducibility gap in
[`../../docs/reproducibility/REPRODUCIBILITY_GAP_REVIEW.md`](../../docs/reproducibility/REPRODUCIBILITY_GAP_REVIEW.md)?

Full plan: [`../../docs/planning/FINETUNING_EXPERIMENTS_PLAN.md`](../../docs/planning/FINETUNING_EXPERIMENTS_PLAN.md).

## Baseline

External anchors (paper, relaxed F1@3):
- Llama3:8b CoT-List fine-tuned: STSS-Test-2 = 0.63, Test-Full = 0.62 (Table 3).
- Llama3:8b No-CoT fine-tuned: Test-Full = 0.09 (Table 3).
- GBERT-Large + Half-Stride (best supervised): STSS-Test-2 = 0.66, Test-Full = 0.68 (Table 1).

Internal anchor: prompting on the true ~4%-border distribution reaches F1@3 ~ 0.31 raw / ~0.51 with
post-processing (partial), see
[`experiment__improvement__f3-precision-campaign.md`](experiment__improvement__f3-precision-campaign.md).
The E1 run becomes the in-campaign baseline to beat once available.

## Constants

See `fixed_conditions` above. Splits are pinned in
[`../../data/manifests/finetune_splits.json`](../../data/manifests/finetune_splits.json) (paper Table 6),
with per-text expected counts from Table 5. Data is built by
[`../../src/finetune/build_sft_dataset.py`](../../src/finetune/build_sft_dataset.py) and verified against
those counts (`verification.json`).

Data caveat: the XMI parser counts scene-level borders only (`Szene Ebene 1`), giving 145/172 borders on
STSS-Test-2 (vs 219/227 if non-scenes were also counted as segments). This matches our prompting setup,
so comparisons are consistent; switching to a segment-level definition would require a decision note.

## Variants

See `variants` above. Data-side factors (E3/E4/E5) require rebuilding the SFT JSONL with the relevant
`build_sft_dataset.py` flag; training-side factors (E2/E6) only change the Kaggle config or `MODELS=`.

## Evaluation rule

In-kernel, after each training, on the full held-out split at natural distribution. The kernel
([`../../src/finetune/kaggle/train_kernel.py`](../../src/finetune/kaggle/train_kernel.py)) reports macro
and micro relaxed F1 at tolerances 0/1/3 for each post-processing scenario, and uploads
`metrics_<model>_<job>.json` next to the adapter on the HF Hub. Headline = `scenarios.none.tol_3.macro_f1`.

## Interim conclusion

2026-06-09: Superseded by
[`experiment__finetune__hf-jobs-qlora-campaign.md`](experiment__finetune__hf-jobs-qlora-campaign.md)
and decision
[`../decisions/decision__finetune-compute-hf-local.md`](../decisions/decision__finetune-compute-hf-local.md).
No Kaggle training run was executed.

## Final conclusion

Campaign moved to HF Hub + local GPU before any Kaggle run. Kaggle kernel retained for reference only.
