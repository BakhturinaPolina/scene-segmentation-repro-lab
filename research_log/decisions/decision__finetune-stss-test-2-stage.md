---
note_type: decision
decision_id: finetune_stss_test_2_stage
title: "Fine-tuning stage: STSS-Test-2 only until full corpus arrives"
date: 2026-06-11
decision_type: process
status: active
decision_statement: "All fine-tuning work stays on STSS-Test-2 (Aus guter Familie + Effi Briest) via LOO folds until the full 41-text corpus is on disk; E1+ corpus runs remain gated."
reasoning_summary: "Only two annotated XMI zips are available locally. Cross-fold training (train one novel, eval the other) is the only honest finetune setup with this data. Metrics are tagged debug and must not be reported as paper-comparable performance."
related_experiments:
  - experiment__finetune__hf-jobs-qlora-campaign
related_runs: []
related_artifacts: []
evidence_strength: strong
follow_up_action: "Complete E0 full folds on HF Jobs; resume E1 when train_full corpus is available."
notion_targets:
  decisions: true
  runs: true
  artifacts: true
  experiments: true
---

## Context

Full corpus (`train_full`, 32 texts) is not on disk. STSS-Test-2 provides two novels with gold scene
annotations under `upstream/scene-segmentation/data/full/stss_test_2/`.

## Decision

1. **Default `DATA_SCOPE=stss_test_2`** in `submit_job.sh` (alias: `pilot`).
2. **Folds mode with `--stss_only`**: no Excel prompting texts in training; only the two STSS novels.
3. **Paper-like build defaults**: `cot_list`, `paper10pct`, `tokens512` context.
4. **Jobs**: `fold_A` (train Aus guter Familie → eval Effi Briest), `fold_B` (reverse).
5. **All runs tagged `debug: true`**; headline metric path unchanged: `scenarios.none.tol_3.macro_f1`.
6. **E1+ corpus experiments** remain blocked until ≥10 XMI zips under `upstream/.../data/full/`.

## When to revisit

Place the full 41-text corpus on disk and switch to `DATA_SCOPE=corpus` for paper-comparable E1 anchor.
