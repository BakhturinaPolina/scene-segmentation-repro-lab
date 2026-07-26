---
note_type: sync_note
sync_id: sync_20260722_dprose_familyL_spot_rerun
date: 2026-07-22
title: "dProse Family L spot-rerun vs production B"
track: prompting
work_block_type: research
runs_created:
  - "2026-07-22__prompting__experiment__dprose-familyL-spot-rerun.md"
artifacts_created:
  - "artifact__dprose-familyL-spot-rerun__B-vs-L-comparison.md"
issues_created:
  - ""
decisions_created:
  - ""
experiments_updated:
  - "experiment__prompting__prompt-family__gemini-batch-excel-BKQ.md"
roadmap_updates:
  - "Family L transfer-checked on 4 dProse spot texts; no full-corpus L re-run."
notion_sync_priority: medium
---

## What was done

Re-ran four contrasting dProse spot-check texts with Family L under production
batch settings; compared to on-disk Family B labels.

## Main result

BORDER rate −7 to −11 pp on every text (aggregate −35% borders). L mostly a
subset of B. Montage/structural consecutive runs only partially thinned.

## What needs syncing to Notion

- Run + artifact notes; table for Final Remarks.

## What remains unresolved

Whether L should ever replace B for a full-corpus re-label (under-segmentation
risk on low-BORDER dialogue texts; cost ~$500 again).

## Next step

Use in Final Remarks drafting; keep production labels as Family B.
