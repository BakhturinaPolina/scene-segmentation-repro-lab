---
note_type: sync_note
sync_id: sync_20260515_stss2_section52_campaign
date: 2026-05-15
title: "STSS-Test-2 §5.2 prompt-family campaign (Phase A–C) completed end-to-end"
track: prompting
work_block_type: research
runs_created:
  - "run_20260515_stss2_prompting_phase_a_family_sweep_nemotron"
  - "run_20260515_stss2_prompting_phase_b_2models_pinned"
  - "run_20260515_stss2_prompting_phase_c_baseline_and_factors"
artifacts_created:
  - "scripts/phase_a_sweep.sh"
  - "scripts/phase_b_sweep.sh"
  - "scripts/phase_c_sweep.sh"
  - "src/error_tag_review.py"
  - "src/prompts/json_schema_score_array.json"
issues_created:
  - "issue_api_openrouter_free_inventory_phase_b_constraint"
decisions_created:
  - "decision_pilot_vs_full_and_reasoning_off_candidate"
experiments_updated:
  - "exp_prompting_stss2_section52_campaign (new)"
roadmap_updates:
  - "PROJECT_PLAN.md §5.2 Phase A–C executed end-to-end on STSS-Test-2"
notion_sync_priority: high
---

## What was done

Executed the §5.2 prompting protocol end-to-end against
`data/manifest_stss_test_2.json` with gold-label scoring on the existing
`src/run_prompting_stratified.py` runner, no runner code changes.

- Phase A: 10 prompt families × 1 pinned model (Nemotron-Super-120B free),
  `max_per_class=15`, 92 min wall-clock, all exit=0, all parse-failure-free.
- Phase B: 3 kept families × 2 pinned models (Nemotron-Super carry-over +
  gpt-oss-120b), 78 min wall-clock for the new sweep; 3 candidate models
  smoke-blocked at the locked controls (Venice 429, reasoning-token
  saturation, Google AI Studio rate-limit).
- Phase C: full-stratified baseline of the headline combo (892 sentences,
  120 min) + 5 factor pilots E3/E4/E6 (38 min), all exit=0.

Built a post-hoc error tagger (`src/error_tag_review.py`) and ran it across
Phase A/B/C outputs for the surviving combo and key comparators.

## Main result

Headline: **Nemotron-Super-120B + prompt family B (zero-shot JSON,
`json_schema_label_reason.json`), locked decoding controls** is the §5.2
campaign winner. Full-stratified F1@0 = **0.763** (P=0.774, R=0.754,
F1@3=0.830), +0.010 vs the 2026-04-08 upstream `prompt_classify` baseline
(0.753), at 7.99 s/sentence with zero parse failures.

Provisional follow-up: pilot-scope evidence shows `reasoning=off` lifts
F1@0 to 0.874 (R=0.933) and halves latency. Pending one full-stratified
confirmation rerun before changing the locked default.

## What needs syncing to Notion

- New runs (Phase A/B/C) — table of metrics per (model, family, scope).
- Updated experiment row `exp_prompting_stss2_section52_campaign` with
  per-phase outcomes and headline F1.
- New issue `issue_api_openrouter_free_inventory_phase_b_constraint` (model
  bucket spec cannot be filled with current free inventory at locked
  controls).
- New decision `decision_pilot_vs_full_and_reasoning_off_candidate`
  (headline reporting standard + provisional reasoning-mode candidate).

## What remains unresolved

- `reasoning=off` confirmation at full stratified scope — single
  ~1h command in the decision note.
- Reopening the §5.2 model bucket once non-Venice providers carry a
  reasoning-capable free model that doesn't saturate `max_tokens=256`.
- Potential new follow-up axis E7 (max_tokens) to make reasoning-token
  models comparable at the §5.2 controls.

## Next step

Run the confirmation command from
`decision__pilot-vs-full-and-reasoning-off-candidate.md` (one
`--max_per_class 0 --reasoning off` rerun, ~1h). If F1@0 ≥ 0.763,
amend `decision__default-openrouter-free-model.md` to lock
`reasoning=off` for this combo.
