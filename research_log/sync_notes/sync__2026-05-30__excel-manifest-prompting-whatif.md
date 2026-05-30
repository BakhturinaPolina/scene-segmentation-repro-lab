---
note_type: sync_note
sync_id: sync_20260530_excel_manifest_prompting_whatif
date: 2026-05-30
title: "Excel-manifest prompting run, scoring, FP analysis, and normalization what-if"
track: cross-project
work_block_type: research
runs_created:
  - "run_20260530_excel_manifest_familyb_full_eval_whatif"
artifacts_created:
  - "art_excel_manifest_familyb_whatif_table_20260530"
issues_created:
  - ""
decisions_created:
  - ""
experiments_updated:
  - "experiment__prompting__stss2-section52-campaign"
roadmap_updates:
  - "Added evidence for Excel-manifest comparability gap vs report pipeline"
notion_sync_priority: high
---

## What was done

- Adapted `run_prompting_stratified.py` for `--excel_manifest` execution.
- Ran full-eval prompting with family B on two new Excel-derived texts.
- Computed direct gold-vs-pred metrics and FP context artifacts.
- Executed normalization what-if scenarios and exported scenario tables.
- Added a consolidated human-readable report in `docs/EXCEL_PROMPTING_2026-05-30_REPORT.md`.

## Main result

The stratified runner improved metrics versus prior baseline TXT runner, but aggregate exact F1 remains low (`0.1194`) due to high FP volume. Normalization what-if increased tolerant metrics substantially (`tol3` to `0.5455`, `tol5` to `0.6000`), indicating boundary-fragmentation effects.

## What needs syncing to Notion

- Run note: `run_20260530_excel_manifest_familyb_full_eval_whatif`
- Artifact note: `art_excel_manifest_familyb_whatif_table_20260530`
- Docs summary: `docs/EXCEL_PROMPTING_2026-05-30_REPORT.md`
- Core output directory:
  `outputs/prompting/2026-05-30-excel-full-eval/full_nvidia_nemotron-3-super-120b-a12b_familyB_reasoning-off/`

## What remains unresolved

- No decision yet on standardized post-processing for Excel-manifest datasets.
- No controlled threshold sweep (`min_scene_len=3/5/...`, confidence thresholds) completed yet.

## Next step

Run one-factor post-processing sweep on the same cached predictions and decide whether to adopt a dataset-specific boundary-normalization policy.

