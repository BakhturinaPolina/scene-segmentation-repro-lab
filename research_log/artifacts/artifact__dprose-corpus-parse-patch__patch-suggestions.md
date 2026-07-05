---
note_type: artifact
artifact_id: art_dprose_corpus_parse_patch
title: "dProse corpus parse-failure patch suggestions (40 keys)"
date: 2026-07-04
artifact_type: table
produced_by_run: run_20260704_dprose_sync_retry_failed
track: prompting
path: "outputs/runs/dprose_batch/dprose-full-corpus/patch_suggestions.json"
url: ""
description: "Neighbor-consensus label suggestions for 40 sentence-keys; applied 2026-07-04 (100% parse OK, all rows tagged manual_fix)."
report_worthy: true
figure_or_table_candidate: Table
related_experiment: run_20260703_dprose_full_wave07
related_task: "dProse full-corpus parse remediation"
notion_targets:
  artifacts: true
  runs: true
  decisions: false
---

## What this artifact is

JSON/CSV export from `scripts/evaluation/patch_failed_predictions.py` listing suggested BORDER/NOBORDER labels for every remaining parse-failed sentence-key after Wave 7 and the 2026-07-04 retry passes.

Paths:

- `outputs/runs/dprose_batch/dprose-full-corpus/patch_suggestions.json`
- `outputs/runs/dprose_batch/dprose-full-corpus/patch_suggestions.csv`

## What it shows

| Field | Meaning |
|-------|---------|
| `key` | Sentence key (`dprose_<id>:<idx>`) |
| `suggested_label` | BORDER or NOBORDER |
| `confidence` | high / medium / low |
| `method` | Recovery heuristic (see spot-checks doc) |
| `parse_error` | Original failure (`blocked:PROHIBITED_CONTENT`, 503, etc.) |
| `prev_label` / `next_label` | Parsed neighbor context |

Distribution: 18 high, 19 medium, 3 low confidence. Methods: 18 neighbor_agreement, 6 wide_neighbor_agreement, 5 before_border_continuation, 5 after_border_continuation, 2 prev_only, 1 next_only, 3 default_noborder.

## Why it matters

36/40 remaining failures are Gemini safety blocks on literary German prose — re-querying via batch or sync API is unlikely to succeed. Neighbor-consensus patching closes the gap to 100% parse OK without additional API spend, marking rows with `manual_fix` / `manual_fix_confidence` for auditability.

## Reuse notes

```bash
# Review low-confidence rows before apply
grep ',low,' outputs/runs/dprose_batch/dprose-full-corpus/patch_suggestions.csv

# Apply medium+ confidence
.venv/bin/python scripts/evaluation/patch_failed_predictions.py \
  --export_json outputs/runs/dprose_batch/dprose-full-corpus/patch_suggestions.json \
  --apply --min_confidence medium
```

Manual overrides: edit CSV (columns `key,label,reason`) and pass `--overrides patch_overrides.csv`.
