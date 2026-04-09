---
note_type: experiment
experiment_id: experiment__prompting__model__free-120b-comparison
title: "Free-tier 120B model comparison for scene boundary prompting"
date_opened: 2026-04-08
track: prompting
status: concluded
factor_under_test: "LLM model (free 120B-class via OpenRouter)"
baseline_run_id: "run_20260408_prompting_gptoss120b_stratified"
hypothesis: "Nemotron-3-Super-120b will achieve higher F1 than GPT-OSS-120b due to better recall on subtle scene transitions"
fixed_conditions:
  - "prompt: upstream prompt_classify"
  - "context_size: 409 tokens"
  - "dataset: both novels in stss_test_2"
  - "provider: OpenRouter free tier"
variants:
  - "openai/gpt-oss-120b:free"
  - "nvidia/nemotron-3-super-120b-a12b:free"
success_metric: "macro-averaged F1 at tol=0"
comparison_rule: "Higher F1 wins; if F1 is tied, prefer higher recall"
related_runs:
  - "run_20260408_prompting_gptoss120b_stratified"
  - "run_20260408_prompting_nemotron_stratified"
related_artifacts: []
notion_targets:
  experiments: true
  runs: true
  artifacts: true
  decisions: false
---

## Research question

Which free-tier 120B-class model performs better at zero-shot scene boundary detection in German literary texts?

## Baseline

GPT-OSS-120b:free — pilot (max_per_class=15): macro F1=0.696 (P=1.000, R=0.533) at tol=0.

## Constants

- Upstream default prompt (`prompt_classify`)
- Context window 409 tokens
- Stratified sampling with seed 1337
- Two novels: *Aus guter Familie* (5025 sents, 219 borders) and *Effi Briest* (5906 sents, 227 borders)
- OpenRouter free tier

## Variants

| Model | Params | Active Params | Provider |
|---|---|---|---|
| openai/gpt-oss-120b:free | 120B | 120B | OpenRouter |
| nvidia/nemotron-3-super-120b-a12b:free | 120B | 12B (MoE) | OpenRouter |

## Results

### Pilot comparison (max_per_class=15, n=60)

| Model | P (tol=0) | R (tol=0) | F1 (tol=0) | F1 (tol=1) | F1 (tol=3) | Avg latency |
|---|---|---|---|---|---|---|
| GPT-OSS-120b | **1.000** | 0.533 | 0.696 | 0.696 | 0.696 | ~4s |
| Nemotron-3-Super | 0.873 | **0.667** | **0.753** | **0.804** | **0.820** | ~10s |

### Full stratified run — Nemotron (max_per_class=0, n=892)

| Document | Sentences | Accuracy | P (tol=0) | R (tol=0) | F1 (tol=0) | TP | FP | FN |
|---|---|---|---|---|---|---|---|---|
| Aus guter Familie | 438 | 76.5% | 0.858 | 0.635 | 0.730 | 139 | 23 | 80 |
| Effi Briest | 454 | 80.6% | 0.921 | 0.670 | 0.775 | 152 | 13 | 75 |
| **Macro Avg** | **892** | | **0.890** | **0.652** | **0.753** | | | |

Multi-tolerance (macro-averaged):

| Tolerance | P | R | F1 |
|---|---|---|---|
| tol=0 | 0.890 | 0.652 | 0.753 |
| tol=1 | 0.901 | 0.659 | 0.761 |
| tol=3 | 0.933 | 0.688 | 0.792 |

### Pilot reliability check

| | Pilot (n=60) | Full (n=892) |
|---|---|---|
| F1 (tol=0) | 0.753 | 0.753 |
| Precision | 0.873 | 0.890 |
| Recall | 0.667 | 0.652 |

Pilot macro F1 exactly matched the full run, validating max_per_class=15 as a reliable estimator.

## Evaluation rule

Higher F1 at tol=0 wins. Nemotron wins over GPT-OSS by +0.057 F1 (pilot). Full-run Nemotron F1=0.753.

## Error analysis

### Pilot-level (max_per_class=15)
- **GPT-OSS failure mode**: pure under-detection (FP=0, FN=14). Only detects borders with explicit structural markers.
- **Nemotron failure mode**: mostly under-detection (FN=10) with 3 false positives. More willing to predict BORDER.
- **Shared failures**: both miss subtle transitions (idx=4386 "Sie fuhren auf dem Wasser...", idx=2716, idx=2735).

### Full-run (Nemotron, n=892)
- **36 false positives** across 892 sentences (4.0% FP rate) — model is precise.
- **155 false negatives** — model misses ~35% of borders.
- **Recall is the bottleneck**, not precision.
- **Effi Briest outperforms Aus guter Familie** (F1=0.775 vs 0.730): its scene transitions are more structurally marked.
- **Tolerance helps moderately**: +0.039 F1 from tol=0 to tol=3.

## Final conclusion

**Nemotron-3-Super-120b is the better model** for scene boundary prompting. It achieves higher F1 than GPT-OSS at all tolerance levels by trading marginal precision for substantially better recall.

Full stratified results (F1=0.753 at tol=0, F1=0.792 at tol=3) provide a solid zero-shot prompting baseline for comparison with supervised fine-tuning approaches.

**Runtime**: ~3 hours for 892 sentences on free tier.
