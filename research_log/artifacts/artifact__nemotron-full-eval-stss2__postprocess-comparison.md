---
note_type: artifact
artifact_id: art_postprocess_partial_aus_guter_familie
title: "Post-processing scenario comparison on the partial Nemotron baseline cache"
date: 2026-06-08
artifact_type: comparison
produced_by_run: run_20260606_nemotron_full_eval_stss2
track: prompting
path: "outputs/review/postprocess/aus_guter_familie_partial_postproc.json"
url: ""
description: "P/R/F1 at tol 0/1/3 for 7 post-processing scenarios applied to the partial Aus-guter-Familie cache."
report_worthy: true
figure_or_table_candidate: "Table"
related_experiment: exp_f3_precision_campaign
related_task: "Step 3 post-processing"
notion_targets:
  artifacts: true
  runs: true
  decisions: true
---

## What this artifact is

JSON output of `src/postprocess/run_postprocess.py --scenario all` run on the
partial Stage-1 cache
`outputs/runs/prompting/2026-06-06/full_.../cache_Aus_guter_Familie.json`
(819 cached sentences, 35 gold borders).

Reproduce:

```bash
python src/postprocess/run_postprocess.py \
  --cache outputs/runs/prompting/2026-06-06/full_nvidia_nemotron-3-super-120b-a12b_free_familyB_reasoning-off/cache_Aus_guter_Familie.json \
  --scenario all --confidence_threshold 0.9 --tolerances 0 1 3 \
  --out outputs/review/postprocess/aus_guter_familie_partial_postproc.json
```

## What it shows

| Scenario | pred borders | F1@0 | F1@1 | F1@3 |
|----------|-------------:|-----:|-----:|-----:|
| none (raw) | 220 | 0.196 | 0.245 | 0.306 |
| min_scene_len_3 | 141 | 0.239 | 0.318 | 0.393 |
| min_scene_len_5 | 109 | 0.181 | 0.278 | 0.432 |
| burst_collapse | 169 | 0.226 | 0.296 | 0.363 |
| burst_collapse + min_scene_len_3 | 135 | 0.235 | 0.318 | 0.415 |
| confidence_threshold (0.9) | 75 | 0.291 | 0.355 | 0.466 |
| confidence_threshold + min_scene_len_3 | 60 | 0.316 | 0.400 | **0.511** |

## Why it matters

Confirms (on partial data) that free post-processing substantially improves
precision and F1@3 with no extra API spend. The combined rule
(confidence_threshold + min_scene_len_3) is the current best and motivates the
Step-3 default. `min_scene_len_5` helps F1@3 only by sacrificing recall, which is
risky for novels with small gold gaps (Kleist min gap=1).

## Reuse notes

Numbers are from a partial cache and will shift once the full_eval completes; treat
as directional. Re-run the same command on the completed caches for both novels to
get final post-processing numbers, then update the experiment's Final conclusion.
