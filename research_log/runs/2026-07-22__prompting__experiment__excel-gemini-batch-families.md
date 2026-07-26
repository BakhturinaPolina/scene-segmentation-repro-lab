---
note_type: run
run_id: run_20260722_excel_gemini_batch_families
title: "Prompt-family sweep on close-reading gold via Gemini Batch API (B + K-Q)"
date: 2026-07-22
track: prompting
run_type: experiment
status: success
goal: "Run families B and K-Q on the two close-reading gold texts (Gaensemagd + Kleist) through the official Gemini Batch API, score vs gold at tol 0/1/3, to (a) give a Gemini-batch baseline for B and (b) quantify the FP-reduction variants K-Q for the report's Final Remarks."
entrypoint: "src/runners/run_excel_batch_families.py"
command: "set -a && source .env && set +a; PYTHONUNBUFFERED=1 .venv/bin/python -u src/runners/run_excel_batch_families.py --families B,K,L,M,N,O,P,Q --poll_interval 30 --date 2026-07-22-excel-gemini-batch-families"
working_directory: "/home/polina/Documents/Cursor_Projects/scene-segmentation-research"
git_commit: "0bff9746e720d01885165b809a5ce04592e61910"
environment: ".venv (python 3.12.3), google-genai; GEMINI_API_KEY from .env"
os: "Linux"
hardware: "n/a (server-side batch)"
gpu: "n/a"
cuda_notes: ""
api_provider: "Google Gemini Batch API (official, not OpenRouter)"
api_model: "gemini-2.5-pro"
api_cost_estimate: "$12.02 total (8 families, ~$1.3-2.0 each); batch pricing"
dataset_assets:
  - "data/manifests/excel_batch.json"
  - "data/processed/excel_prompting/gaensemagd_sentence_level/gaensemagd_sentence_level__for_prompting.{txt,jsonl}"
  - "data/processed/excel_prompting/gaensemagd_sentence_level/gaensemagd_sentence_level__gold_labels.csv"
  - "data/processed/excel_prompting/kleist_sentence_level/kleist_sentence_level__for_prompting.{txt,jsonl}"
  - "data/processed/excel_prompting/kleist_sentence_level/kleist_sentence_level__gold_labels.csv"
label_schema: "binary BORDER/NOBORDER at sentence level; gold from Excel scene-id changes (1-based sentence_index)"
prompt_version: "families B, K, L, M, N, O, P, Q (src/prompts/*.txt); schema src/prompts/json_schema_label_reason.json"
model_name: "gemini-2.5-pro"
varying_factor: "prompt family (B baseline vs K-Q precision/FP-reduction variants)"
fixed_conditions:
  - "model gemini-2.5-pro (Gemini Batch API, mode=file)"
  - "context_sentences=12 each side (symmetric sentence-count window)"
  - "temperature=0, max_output_tokens=2048, thinking_budget=-1 (dynamic)"
  - "response schema json_schema_label_reason.json"
  - "same two gold texts, full evaluation (all 316 sentences)"
random_seed: "n/a (Gemini Batch API does not expose seed; temperature 0)"
output_dir: "outputs/runs/prompting/2026-07-22-excel-gemini-batch-families/"
artifacts_expected:
  - "family_<ID>/predictions.jsonl"
  - "family_<ID>/summary.json"
  - "family_<ID>/score.json"
  - "comparison.csv"
artifacts_produced:
  - "outputs/runs/prompting/2026-07-22-excel-gemini-batch-families/comparison.csv"
  - "outputs/runs/prompting/2026-07-22-excel-gemini-batch-families/family_{B,K,L,M,N,O,P,Q}/{predictions.jsonl,summary.json,score.json}"
main_metric_name: "macro relaxed F1 (tol=3) over Gaensemagd + Kleist"
main_metric_value: "B=0.5373; best variant L=0.7832"
precision: "B macro P@0=0.2348; L macro P@0=0.4281"
recall: "B macro R@0=0.9643; L macro R@0=0.9285"
f1: "B macro F1@0=0.3776; L macro F1@0=0.5844"
iou: ""
runtime: "~22 min wall (8 sequential batch jobs, each ~2-3 min server-side)"
failure_category: ""
related_experiment: "experiment__prompting__prompt-family__gemini-batch-excel-BKQ.md"
related_issue: ""
decision_relevance: false
notion_targets:
  roadmap: ""
  runs: true
  experiments: true
  artifacts: true
  issues: false
  decisions: false
---

## Objective

Produce defensible, like-for-like statistics for the Scene Segmentation report by
running the production prompt B and its FP-reduction variants K-Q on the two
close-reading gold texts through the **official Gemini Batch API** (the same API
path used for the dProse production labelling), rather than the OpenRouter sync
path used in the May 2026 Excel experiments.

Two separate purposes, kept distinct per the report structure:

- **B** -> a Gemini-batch baseline for the "why B" Model Selection argument.
- **K-Q** -> FP-reduction / over-segmentation mitigation evidence for the
  report's **Final Remarks** (draft lines 88-95). K-Q are *not* competitors that
  justify choosing B; they are later precision-focused variants *of* B.

## What was held constant

- Model `gemini-2.5-pro`, Gemini Batch API, `mode=file`.
- Context: `context_sentences=12` each side (symmetric sentence-count window) --
  identical to the dProse production config.
- Decoding: `temperature=0`, `max_output_tokens=2048`, `thinking_budget=-1`.
- Output schema: `json_schema_label_reason.json` (label + reason), the production
  schema. All families here are json-label families.
- Data: both gold texts, full evaluation (all 316 sentences; 71 + 245).
- Scoring: `src/eval/excel_gold_scoring.py`, minority-class BORDER F1 at tol 0/1/3,
  macro-averaged over the two texts (same protocol as Zehe relaxed F1).

## What changed

Only the prompt family (B baseline vs K, L, M, N, O, P, Q).

## Outcome

Macro over Gaensemagd + Kleist, full evaluation. Ranked by relaxed F1 (tol3):

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

Per-document detail for B and best variant L:

| Family | Text | n | gold | pred | tol0 P/R/F1 | tol3 F1 |
|--------|------|---|------|------|-------------|---------|
| B | Gaensemagd | 71 | 7 | 29 | 0.241/1.000/0.389 | 0.583 |
| B | Kleist | 245 | 14 | 57 | 0.228/0.929/0.366 | 0.491 |
| L | Gaensemagd | 71 | 7 | 17 | 0.412/1.000/0.583 | 0.824 |
| L | Kleist | 245 | 14 | 27 | 0.444/0.857/0.585 | 0.743 |

B token profile: avg input 1005 tok, avg output 75 tok, avg thoughts 692 tok;
label counts BORDER=86 / NOBORDER=230; parse-ok 1.000.

## Interpretation

- **Recall is high across every family** (R@0 0.89-1.00). The whole spread in F1
  is driven by **precision / over-prediction**, confirming that over-segmentation
  is the dominant error mode on these texts.
- **B via Gemini Batch is lower than B via OpenRouter.** This run's B is
  F1@0=0.378 / F1@3=0.537 with 4.1x over-prediction, versus the May OpenRouter
  Excel B run at F1@0=0.498 / F1@3=0.762 with ~2.2x over-prediction. The most
  likely cause is the **context window**: this run uses 12 sentences each side
  (the dProse production setting), a much wider window than the OpenRouter runs'
  409-token budget, and a wider window appears to encourage more boundary calls.
  This is a directional, defensible observation, not a same-config comparison
  (API path and thinking control also differ).
- **The strict-definition prompt (L) is the strongest FP-reduction lever**: it
  roughly halves over-prediction (4.1x -> 2.1x) and lifts relaxed F1 to 0.78,
  while keeping recall high. This is Final-Remarks material (prompt-level
  over-segmentation mitigation), not a reason to change the production baseline.
- Some variants backfire under the wide-context batch config: P (anti-example)
  and O (few-shot) *increase* over-prediction.

## Next step

- Fold B into the report's Model Selection notes as the Gemini-batch baseline,
  clearly flagged as different-config from the OpenRouter headline numbers.
- Fold L / Q / N into Final Remarks as evidence that prompt-level FP-reduction
  (especially a stricter boundary definition) materially cuts over-segmentation.
- Prepared-but-not-run families C, D, E, F, G, J (schemas wired) and A, H, I
  (pipeline stubs) can be swept later with `--families ...` without code changes.
