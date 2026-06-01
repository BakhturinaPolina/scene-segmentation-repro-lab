---
note_type: sync_note
sync_id: sync_20260530_excel_controlled_postprocessing_sweep
date: 2026-05-30
title: "Fresh Excel full-eval rerun + one-factor post-processing sweep completed"
track: cross-project
work_block_type: research
runs_created:
  - "run_20260530_excel_controlled_postprocessing_sweep"
artifacts_created:
  - "art_excel_controlled_postprocessing_comparison_table_20260530"
  - "art_excel_controlled_postprocessing_fp_tables_20260530"
issues_created:
  - ""
decisions_created:
  - ""
experiments_updated:
  - "exp_prompting_post_processing_excel_controlled_sweep"
roadmap_updates:
  - "Controlled one-factor evidence added for Excel-manifest post-processing policy"
notion_sync_priority: high
---

## What was done

- Executed fresh controlled full-eval rerun on Excel-manifest with fixed family-B settings.
- Copied review outputs into scenario workspace at `outputs/review/excel_controlled_sweep/none/`.
- Generated baseline exact scoring JSONs and aggregate exact summary.
- Updated analysis tooling for `min_scene_len_5` and scenario-selectable FP export.
- Produced one-factor comparison metrics table and FP tables for `none`, `min_scene_len_3`, `min_scene_len_5`.
- Logged run, experiment, and artifacts in `research_log/`.

## Main result

- Fresh run succeeded with zero parse failures (`elapsed_ms=664526`).
- Baseline exact aggregate (`score_vs_gold_aggregate.json`): P `0.0579`, R `0.3333`, F1 `0.0986`.
- Tolerant quality improved with stronger smoothing:
  - `tol5_F1`: `0.4242` (`none`) -> `0.5676` (`min_scene_len_3`) -> `0.6667` (`min_scene_len_5`)
- Exact F1 decreased slightly across smoothing scenarios (`0.0993` -> `0.0909` -> `0.0896` in comparison table).

## What needs syncing to Notion

- Run note: `run_20260530_excel_controlled_postprocessing_sweep`
- Experiment note: `exp_prompting_post_processing_excel_controlled_sweep`
- Artifact notes:
  - `art_excel_controlled_postprocessing_comparison_table_20260530`
  - `art_excel_controlled_postprocessing_fp_tables_20260530`
- Output roots:
  - `outputs/prompting/2026-05-30-excel-controlled-sweep/full_nvidia_nemotron-3-super-120b-a12b_familyB_reasoning-off/`
  - `outputs/review/excel_controlled_sweep/`

## What remains unresolved

- No formal decision note yet selecting default post-processing policy for Excel-manifest datasets.
- No external validation yet on additional Excel-derived corpora beyond the two current texts.

## Next step

Create a decision note selecting either strict-exact or tolerant-first objective, then run a confirmation sweep on additional Excel-derived texts using the same fixed controls.
