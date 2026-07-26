---
note_type: experiment
experiment_id: exp_gemini_batch_excel_BKQ
title: "Gemini Batch prompt-family sweep on close-reading gold (B + K-Q)"
date_opened: 2026-07-22
track: prompting
status: concluded
factor_under_test: "prompt family (B baseline vs K-Q FP-reduction variants) under the Gemini Batch API"
baseline_run_id: "run_20260722_excel_gemini_batch_families (family B)"
hypothesis: "On the two close-reading gold texts, running via the official Gemini Batch API with the production context window (12 sentences/side) reproduces B's behaviour; the K-Q precision variants trade recall for precision and reduce over-segmentation."
fixed_conditions:
  - "gemini-2.5-pro, Gemini Batch API, mode=file"
  - "context_sentences=12, temperature=0, max_output_tokens=2048, thinking_budget=-1"
  - "json_schema_label_reason.json output schema"
  - "both gold texts, full evaluation (316 sentences)"
variants:
  - "B (production baseline)"
  - "K (negative examples), L (strict definition), M (FP-pattern guard)"
  - "N (rarity prior), O (German-fairy few-shot), P (anti-example), Q (combined N+L+M)"
success_metric: "macro relaxed F1 (tol=3) on the BORDER class, and over-prediction ratio (pred borders / gold borders)"
comparison_rule: "one factor (prompt family) varied at a time; all other decoding/context/data held constant"
related_runs:
  - "2026-07-22__prompting__experiment__excel-gemini-batch-families.md"
related_artifacts:
  - "artifact__excel-gemini-batch-families__comparison.md"
notion_targets:
  experiments: true
  runs: true
  artifacts: true
  decisions: false
---

## Research question

Under the official Gemini Batch API (the production labelling path) with the
production context window, how does prompt B behave on the two close-reading gold
texts, and how much do the precision-focused variants K-Q reduce
over-segmentation?

## Baseline

Family B: macro F1@0=0.3776, F1@3=0.5373, over-prediction 4.10x gold, parse-ok
1.000. Note this is meaningfully lower than the May OpenRouter Excel B run
(0.4981 / 0.7617, ~2.2x), attributed mainly to the wider 12-sentence context.

## Constants

Model, API path, context (12 sentences/side), decoding (T=0, max_out=2048,
thinking=-1), output schema, gold texts, full-eval scoring at tol 0/1/3.

## Variants

K, L, M, N, O, P, Q -- all precision/FP-reduction variants of B, same schema and
per-sentence request structure, so they run on the identical batch pipeline.

## Evaluation rule

Minority-class (BORDER) precision/recall/F1 at tolerance 0/1/3, macro-averaged
over Gaensemagd + Kleist (Zehe relaxed-F1 protocol). Ranking metric: F1@3.

## Interim conclusion

Ranking by F1@3: L (0.783) > Q (0.693) > N (0.660) > K (0.556) > M (0.539) >
B (0.537) > P (0.521) > O (0.513). Recall stays high (0.89-1.00) everywhere;
differences are driven by precision / over-prediction.

## Final conclusion

- The stricter boundary definition (L) is the single most effective prompt-level
  lever against over-segmentation on these texts: over-prediction 4.10x -> 2.10x,
  F1@3 0.537 -> 0.783, with recall preserved.
- Combined precision fix (Q) and rarity prior (N) also help; anti-example (P) and
  few-shot (O) hurt under this wide-context batch config.
- These K-Q findings belong to the report's **Final Remarks** (over-segmentation
  mitigation), not to the Model Selection "why B" argument. B remains the
  production baseline; L/Q/N are refinements to consider for future runs.
