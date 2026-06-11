---
note_type: decision
decision_id: decision_postprocess_min_scene_len_3
title: "Default boundary post-processing = confidence_threshold + min_scene_len_3 (not min_scene_len_5)"
date: 2026-06-08
decision_type: process
status: active
decision_statement: "Adopt min_scene_len_3 (optionally combined with a confidence threshold) as the default boundary post-processing rule; do NOT use min_scene_len_5."
reasoning_summary: "Gold border gaps in the Excel corpus are as small as 1 (Kleist) and 3 (Gaensemagd), so a min-gap of 5 deletes 17-31% of TRUE borders; min_scene_len_3 plus confidence filtering improves precision/F1@3 without that recall sacrifice."
related_experiments:
  - exp_f3_precision_campaign
related_runs:
  - run_20260606_nemotron_full_eval_stss2
related_artifacts:
  - art_postprocess_partial_aus_guter_familie
evidence_strength: preliminary
follow_up_action: "Confirm on the completed full_eval caches for both novels before locking as the global default."
notion_targets:
  decisions: true
  runs: true
  artifacts: true
  experiments: true
---

## Context

The Nemotron baseline over-segments. A cheap, free way to raise precision is to
suppress borders that are implausibly close together (min scene length) and/or
borders the model is unsure about (confidence threshold). The question was which
min-gap to use; an earlier comparison report had floated `min_scene_len_5`.

## Evidence

Gold border-gap statistics (computed from Excel gold CSVs):

- Gaensemagd: min gap = 3, avg ~7.5.
- Kleist: min gap = 1, avg ~18.6.

`min_scene_len_5` would erase any true border within 4 sentences of the previous
one, i.e. 17-31% of true borders in these texts. The partial-cache scenario sweep
(artifact `art_postprocess_partial_aus_guter_familie`) shows `min_scene_len_5`
reaches a high F1@3 only by dropping recall (R@3 0.857 vs 0.943 for min_scene_len_3),
whereas `confidence_threshold + min_scene_len_3` reaches the best F1@3 (0.511) while
keeping recall higher than the len-5 rule.

## Decision

Default post-processing = `confidence_threshold` (>=0.85-0.9) combined with
`min_scene_len_3`. `min_scene_len_5` is rejected as the default.

## Why this is the current standard

It improves precision/F1@3 across the partial baseline without the recall loss that
a 5-sentence minimum forces on texts with small true gaps (Kleist gap=1). It is
free (pure post-processing) and reversible (a flag in
`src/postprocess/run_postprocess.py`).

## Consequences

- The Step-3 default and the fine-tune/eval default scenario use min_scene_len_3.
- This is a process default, not a change to the model baseline; the baseline run
  itself is unchanged.

## Follow-up

Re-run `run_postprocess.py --scenario all` on the COMPLETED full_eval caches for
both novels and confirm the ranking before treating this as the locked global
default. Downgrade `evidence_strength` to `moderate`/`strong` once confirmed.
