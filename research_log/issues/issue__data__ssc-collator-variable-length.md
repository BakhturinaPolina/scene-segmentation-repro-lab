---
note_type: issue
issue_id: issue_ssc_collator_batch_size
title: "Default data collator fails on variable-length labels/sep_token_indices"
date_opened: 2026-04-05
category: data
severity: high
status: resolved
first_seen_in_run: "run_20260405_ssc_baseline_bert"
environment: ".venv-gpu (transformers 4.52.4)"
track: ssc
probable_cause: "SSC dataset produces variable-length lists for labels, sep_token_indices, sentence_indices per sample; default collator cannot batch ragged sequences"
attempted_fixes:
  - "Added SSCDataCollator to ssc/train.py that pads labels (-100), sep_token_indices (0), sentence_indices (-1) to max batch length"
  - "Reduced batch_size to 1 because model forward uses .squeeze() and flat indexing incompatible with batch > 1"
blocking: false
related_runs:
  - "run_20260405_ssc_baseline_bert"
notion_targets:
  issues: true
  runs: true
  roadmap: false
---

## Symptom

`ValueError: expected sequence of length 25 at dim 1 (got 18)` when the default data collator tries to stack variable-length label lists.

After fixing with a custom collator: `CUDA error: device-side assert` in cross_entropy_loss with batch_size > 1.

## Context

Each SSC training sample has a different number of sentences per context window. `input_ids` and `attention_mask` are padded to `max_length` by the tokenizer, but `labels`, `sep_token_indices`, and `sentence_indices` are per-sentence lists of variable length.

The model's `forward()` uses `.squeeze()` and `embeddings[sep_token_indices, :]` which works for batch_size=1 (squeeze removes the batch dimension, and sep_token_indices indexes the sequence dimension) but breaks for batch_size > 1 (squeeze is a no-op, sep_token_indices indexes the batch dimension instead).

## Evidence

- batch_size=4: ValueError from default collator
- batch_size=4 + SSCDataCollator: CUDA assert in cross_entropy
- batch_size=1 + SSCDataCollator: works correctly

## Attempted fixes

1. Custom `SSCDataCollator` — pads variable-length fields. **Partial fix**: solves collation but not model forward.
2. Reduced `batch_size=1` — **fully resolved** the training issue.

## Current best understanding

The SSC model architecture assumes batch_size=1. This is an upstream design limitation, not a bug in the newer transformers version. The custom collator is still useful for when batch_size=1 produces single-element lists that need tensor wrapping.

## Next fix to try

For proper batched training, the model's `forward()` would need refactoring to handle per-sample indexing (e.g., using `torch.gather` or loops over the batch dimension). This is a non-trivial change.
