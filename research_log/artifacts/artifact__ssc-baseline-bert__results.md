---
note_type: artifact
artifact_id: art_ssc_baseline_bert_results
title: "SSC baseline results.json (bert-base-german-cased, 1 epoch)"
date: 2026-04-05
artifact_type: metrics
produced_by_run: "run_20260405_ssc_baseline_bert"
track: ssc
path: "outputs/ssc/2026-04-05/baseline_bert/stss_test_2/results.json"
url: ""
description: "Pipeline evaluation results (F1, precision, recall) for BERT baseline on stss_test_2"
report_worthy: false
figure_or_table_candidate: "Table"
related_experiment: ""
related_task: "Phase 3.1"
notion_targets:
  artifacts: true
  runs: true
  decisions: false
---

## What this artifact is

JSON file with per-document and average F1/precision/recall from the SSC pipeline evaluation.

## What it shows

```json
{
  "Aus guter Familie.xmi.zip": {"precision": 1.0, "recall": 0.0046, "f1": 0.0091},
  "Effi Briest.xmi.zip": {"precision": 1.0, "recall": 0.0044, "f1": 0.0088},
  "average_f1": 0.0089
}
```

The model barely predicts any borders (recall ≈ 0.5%) but when it does, it's correct (precision = 1.0).

## Why it matters

Establishes the minimum baseline for the SSC pipeline. Any future model should beat F1=0.0089.

## Reuse notes

Can be loaded with `json.load()`. The model checkpoint is in the parent directory (`model.safetensors`, 425 MB).
