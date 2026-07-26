# Gemini Batch Prompt-Family Sweep on Close-Reading Gold (B + K-Q)

Date: 2026-07-22
Run: `outputs/runs/prompting/2026-07-22-excel-gemini-batch-families/`
Runner: `src/runners/run_excel_batch_families.py`
Scorer: `src/eval/excel_gold_scoring.py`

## 1) Purpose and setup

Run the production prompt **B** and its precision/FP-reduction variants
**K-Q** on the two close-reading gold texts through the **official Gemini Batch
API** (the same API path as the dProse production labelling), and score against
gold scene borders at tolerance 0/1/3.

This differs from the May 2026 Excel experiments
([EXCEL_PROMPTING_2026-05-30_REPORT.md](EXCEL_PROMPTING_2026-05-30_REPORT.md),
[EXCEL_EXPERIMENTS_COMPARISON_REPORT.md](EXCEL_EXPERIMENTS_COMPARISON_REPORT.md)),
which used **OpenRouter sync** with a 409-token context window. Here we use the
Gemini Batch API with the production **12-sentence** context window.

Data (identical processed inputs and gold to the May runs):

| Text | Sentences | Gold borders |
|------|-----------|--------------|
| Gaensemagd | 71 | 7 |
| Kleist | 245 | 14 |
| Both | 316 | 21 |

Fixed controls: `gemini-2.5-pro`, Gemini Batch API `mode=file`,
`context_sentences=12`, `temperature=0`, `max_output_tokens=2048`,
`thinking_budget=-1`, schema `json_schema_label_reason.json`, full evaluation.
Only the prompt family varies.

## 2) Results (macro over both texts, ranked by relaxed F1 tol3)

| Family | Factor | F1@0 | P@0 | R@0 | F1@1 | F1@3 | over-pred (x gold) | parse-ok | cost $ |
|--------|--------|------|-----|-----|------|------|--------------------|----------|--------|
| L | strict MAJOR-discontinuity | **0.5844** | 0.4281 | 0.9285 | 0.6833 | **0.7832** | 2.10 | 1.000 | 1.38 |
| Q | combined N+L+M precision fix | 0.4838 | 0.3322 | 0.8928 | 0.6137 | 0.6934 | 2.62 | 0.984 | 1.61 |
| N | border-rarity prior (7%) | 0.4367 | 0.2855 | 0.9285 | 0.5462 | 0.6601 | 3.24 | 1.000 | 1.49 |
| K | negative examples | 0.3703 | 0.2314 | 0.9285 | 0.4713 | 0.5555 | 4.10 | 1.000 | 1.38 |
| M | FP-pattern guard | 0.3709 | 0.2318 | 0.9285 | 0.4628 | 0.5393 | 3.95 | 0.997 | 1.44 |
| **B** | **production baseline** | **0.3776** | 0.2348 | 0.9643 | 0.4487 | **0.5373** | 4.10 | 1.000 | 1.41 |
| P | anti-example | 0.3433 | 0.2075 | 1.0000 | 0.4203 | 0.5212 | 5.00 | 1.000 | 1.33 |
| O | German-fairy few-shot | 0.3456 | 0.2110 | 0.9643 | 0.4232 | 0.5133 | 4.81 | 0.981 | 1.97 |

Per-document detail for B and the best variant L:

| Family | Text | n | gold | pred | tol0 P/R/F1 | tol3 F1 |
|--------|------|---|------|------|-------------|---------|
| B | Gaensemagd | 71 | 7 | 29 | 0.241/1.000/0.389 | 0.583 |
| B | Kleist | 245 | 14 | 57 | 0.228/0.929/0.366 | 0.491 |
| L | Gaensemagd | 71 | 7 | 17 | 0.412/1.000/0.583 | 0.824 |
| L | Kleist | 245 | 14 | 27 | 0.444/0.857/0.585 | 0.743 |

Total batch cost: **$12.02**.

## 3) Key findings

1. **Recall is high everywhere (R@0 0.89-1.00).** The entire F1 spread is driven
   by precision / over-prediction. Over-segmentation is the dominant error mode,
   consistent with all prior Excel runs.

2. **B via Gemini Batch is lower than B via OpenRouter.** This run: F1@0=0.378,
   F1@3=0.537, over-prediction 4.10x. May OpenRouter Excel B: F1@0=0.498,
   F1@3=0.762, ~2.2x. The most likely driver is the **context window**: 12
   sentences each side (production dProse setting) is much wider than the
   OpenRouter 409-token budget, and a wider window appears to invite more
   boundary calls. API path and thinking control also differ, so this is a
   directional, not a same-config, comparison.

3. **The stricter boundary definition (L) is the strongest FP-reduction lever.**
   It roughly halves over-prediction (4.10x -> 2.10x) and lifts relaxed F1 to
   0.78, while keeping recall high. Q (combined) and N (rarity prior) also help.

4. **Some variants backfire under the wide-context batch config.** P
   (anti-example) pushes over-prediction to 5.0x; O (few-shot) to 4.8x. Adding
   more instruction/examples did not help here; tightening the *definition* did.

## 4) Scope and interpretation notes

- **K-Q are precision-focused variants of B**, not the original A-J family
  competitors used to *select* B. Accordingly these numbers belong to the
  report's **Final Remarks** (over-segmentation mitigation), not the Model
  Selection "why B" argument. B remains the production baseline.
- B's headline numbers in the report continue to come from the OpenRouter Excel
  runs; the Gemini-batch B here is an additional, clearly-flagged baseline that
  demonstrates the same qualitative behaviour (high recall, over-prediction) on
  the production API path.

## 5) Reproduce

```bash
set -a && source .env && set +a
PYTHONUNBUFFERED=1 .venv/bin/python -u src/runners/run_excel_batch_families.py \
  --families B,K,L,M,N,O,P,Q --poll_interval 30 \
  --date 2026-07-22-excel-gemini-batch-families
# re-score only (no API):
.venv/bin/python -u src/runners/run_excel_batch_families.py \
  --families B,K,L,M,N,O,P,Q --score_only \
  --date 2026-07-22-excel-gemini-batch-families
```

Prepared-but-not-run families can be added without code changes:
`--families C,D,E,F,G,J` (schemas wired) and `--families A,H,I` (label-only /
chunk pipeline). Use `--dry_run` to render requests without calling the API.
