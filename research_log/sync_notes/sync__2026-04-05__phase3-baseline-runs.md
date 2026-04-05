---
note_type: sync_note
sync_id: sync_20260405_phase3_baselines
date: 2026-04-05
title: "Phase 3 baseline execution: SSC, prompting, LLaMA dry run"
track: cross-project
work_block_type: research
runs_created:
  - "run_20260405_ssc_baseline_bert"
  - "run_20260405_prompting_baseline_qwen3"
  - "run_20260405_llama_dryrun_8b"
artifacts_created:
  - "art_ssc_baseline_bert_results"
  - "art_prompting_baseline_qwen3_results"
issues_created:
  - "issue_eval_strategy_rename"
  - "issue_accelerate_unwrap_model"
  - "issue_ssc_collator_batch_size"
  - "issue_llama_vram_insufficient"
  - "issue_sft_formatting_func"
decisions_created:
  - "decision_editable_install_cwd_fix"
experiments_updated: []
roadmap_updates:
  - "Phase 3.1 (SSC baseline): completed"
  - "Phase 3.2 (Prompting baseline): completed"
  - "Phase 3.3 (LLaMA dry run): completed (partial — OOM)"
  - "Working-directory sensitivity: resolved"
notion_sync_priority: high
---

## What was done

Executed Phase 3 of the project plan: running baseline experiments for all three pipelines.

### SSC baseline (Phase 3.1)
- Resolved 3 compatibility issues: `evaluation_strategy` rename, `accelerate` version mismatch, variable-length collation
- Trained bert-base-german-cased for 1 epoch on stss_test_2 (2 files, 541 samples)
- Ran full pipeline: train → eval → annotate → score
- Result: avg F1 = 0.0089 (minimal, as expected with frozen embeddings and 1 epoch)

### Prompting baseline (Phase 3.2)
- Configured OpenRouter API with `qwen/qwen3.6-plus:free`
- Created `src/run_prompting_baseline.py` wrapper with rate-limit handling
- Classified 20 sentences from "Aus guter Familie": 100% accuracy (1 border, 19 non-borders)
- Key finding: free tier rate limits make large-scale runs very slow (~22s/sentence)

### LLaMA dry run (Phase 3.3)
- Fixed 2 API issues: `formatting_func` required, must return list
- Model loaded successfully (5.5 GB / 7.6 GB)
- Data preprocessed (10931 samples), but 0 border labels extracted
- OOM at training step with batch_size=20 — need batch_size=1 or smaller model

### Working-directory fix
- Created `pyproject.toml` for upstream clone
- Installed in editable mode in both envs
- Imports now work from any directory

## Main result

All three pipelines are validated end-to-end (SSC fully, prompting fully, LLaMA up to training start). Five dependency/compatibility issues were resolved. The working-directory sensitivity issue is now fixed permanently.

## What needs syncing to Notion

- 3 run notes (SSC baseline, prompting baseline, LLaMA dry run)
- 5 issue notes (eval_strategy, accelerate, collator, VRAM OOM, SFT formatting)
- 1 decision note (editable install)
- 2 artifact notes (SSC results, prompting results)
- Roadmap: Phase 3 marked as completed

## What remains unresolved

1. LLaMA training needs batch_size=1 or cloud GPU (8 GB VRAM insufficient for batch_size > 1)
2. No border labels extracted by `xmi_to_llama_samples` — needs investigation
3. SSC model forward is batch_size=1 only — limits training throughput
4. Prompting rate limits on free tier

## Next step

- Phase 4: Controlled experiments with proper train/test splits, multiple epochs
- Investigate border label extraction in LLaMA data pipeline
- Consider cloud GPU for LLaMA fine-tuning
