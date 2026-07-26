---
note_type: sync_note
sync_id: sync_20260722_excel_gemini_batch_families
date: 2026-07-22
title: "Gemini Batch prompt-family sweep on close-reading gold (B + K-Q)"
track: prompting
work_block_type: research
runs_created:
  - "2026-07-22__prompting__experiment__excel-gemini-batch-families.md"
artifacts_created:
  - "artifact__excel-gemini-batch-families__comparison.md"
issues_created:
  - ""
decisions_created:
  - ""
experiments_updated:
  - "experiment__prompting__prompt-family__gemini-batch-excel-BKQ.md"
roadmap_updates:
  - "Excel gold texts now runnable via official Gemini Batch API (new adapter + scorer)."
notion_sync_priority: medium
---

## What was done

- Built an Excel-gold adapter for the Gemini Batch API: manifest
  `data/manifests/excel_batch.json`, index-base alignment in
  `dprose_batch_core.prepare_requests`, a family-sweep CLI
  `src/runners/run_excel_batch_families.py`, and a tolerance scorer
  `src/eval/excel_gold_scoring.py`.
- Ran families B, K, L, M, N, O, P, Q on Gaensemagd + Kleist via the official
  Gemini Batch API and scored vs gold at tol 0/1/3 ($12.02 total).
- Prepared (not run) schemas + wiring for C, D, E, F, G, J and pipeline stubs for
  A, H, I (chunk / label-only), validated by dry-run.

## Main result

- B (Gemini batch): F1@0=0.378, F1@3=0.537, over-prediction 4.10x -- lower than
  the OpenRouter Excel B baseline (0.498 / 0.762, ~2.2x), most likely due to the
  wider 12-sentence context window.
- Best FP-reduction variant L (strict definition): F1@0=0.584, F1@3=0.783,
  over-prediction 2.10x, recall preserved.
- Recall high across all families; over-segmentation is the dominant error.

## What needs syncing to Notion

- Run + experiment + artifact notes above.
- Table for the report: family x {F1@0, F1@3, over-pred, parse-ok}.

## What remains unresolved

- Whether to sweep the prepared families (C-G, J, A, H, I) for a full A-Q picture.
- Whether the report should state B's headline numbers from OpenRouter or Gemini
  batch (different configs); currently OpenRouter remains the headline, Gemini
  batch is an additional, clearly-flagged baseline.

## Next step

Append B (Model Selection) and K-Q (Final Remarks) evidence to
`docs/corpora/report_automatic_scene_segmentation/Report_Model_Selection_notes.md`.
