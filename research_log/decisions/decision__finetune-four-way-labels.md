---
note_type: decision
decision_id: decision__finetune-four-way-labels
title: "Defer four-way boundary labels until after Pilot 0; keep binary scene-only training"
date: 2026-06-09
decision_type: dataset
status: under-review
decision_statement: "Fine-tuning data and eval remain binary (BORDER/NOBORDER) using scene-only XMI parsing until a follow-up decision approves four-way labels and non-scene segment inclusion."
reasoning_summary: "The paper defines SCENE-SCENE, SCENE-NONSCENE, NONSCENE-SCENE, and NOBORDER but trains binary for imbalance reasons. Our prompting baselines and verification use scene-only borders (Szene Ebene 1). Changing label semantics requires parser validation against Table 5 segment counts and fair comparison with existing baselines."
related_experiments:
  - experiment__finetune__hf-jobs-qlora-campaign
related_runs: []
related_artifacts: []
evidence_strength: preliminary
follow_up_action: "After Pilot 0, prototype four_way rows in build_sft_dataset using parse_segments; collapse to binary for primary F1@3 eval."
notion_targets:
  decisions: true
  runs: false
  artifacts: false
  experiments: true
---

## Context

Zehe et al. (NAACL 2025) define a full four-class boundary task but report binary results for Llama fine-tuning. Our `parse_xmi` extracts only `Szene Ebene 1` elements, so gold BORDER = first sentence of each **scene**. Non-scenes (`Nicht-Szene Ebene 1`) are recorded in manifest expected counts but not used as training labels.

Experiment E9 in `FINETUNING_EXPERIMENTS_PLAN.md` targets non-scene merge errors via four-way supervision.

## Evidence

- STSS-Test-2 verification: scene borders 145+172 vs segment borders 219+227 if non-scenes included.
- All prompting and fine-tuning baselines to date use scene-only binary labels.
- `parse_segments()` stub added in `src/data/build_fewshot_from_stss.py`; `--label_mode four_way` raises `NotImplementedError` until this decision is activated.

## Decision

**Pilot 0 and E0–E1 runs use `--label_mode binary` only.** Four-way label generation is blocked pending:

1. Validation that non-scene XMI element type strings match corpus files on disk.
2. Collapse-to-binary eval rule (any segment start → BORDER for primary metric).
3. A/B comparison plan against E1 anchor.

## Why this is the current standard

Keeps fine-tuning comparable to prompting baselines and avoids silent label-definition drift before the full corpus is verified.

## Consequences

- E9 experiment row stays **Code TODO** for training data; parser stub exists for future work.
- Manifest verification continues to report `expected_segment_borders` alongside scene borders.

## Follow-up

Revise this decision to `active` after implementing and verifying `four_way` rows on one STSS-Test-2 novel, then run E9 as a controlled single-factor experiment.
