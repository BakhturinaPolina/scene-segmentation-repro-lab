---
note_type: experiment
experiment_id: exp_excel_fp_ofat_openrouter
title: "Excel FP reduction OFAT campaign (14-model OpenRouter sweep + decode/prompt/postprocess)"
date_opened: 2026-06-14
track: prompting
status: active
factor_under_test: "model backbone, then decoding, prompt wording, context window, post-processing, verification"
baseline_run_id: ""
hypothesis: "Model choice and precision-focused interventions (sparse-border priors, min-gap, two-pass verify) raise relaxed F1@3 on Excel texts while cutting 5–6× border over-prediction toward ≤2× gold."
fixed_conditions:
  - "corpus = data/manifests/excel_prompting.json (Gänsemagd + Kleist, 316 sentences, 21 gold borders)"
  - "prompt family B unless Stage 3 explicitly changes it"
  - "temperature = 0, top_p = 1.0, seed = 1337, max_tokens = 256"
  - "context_mode = tokens, context_size = 409 unless Stage 4 changes it"
  - "evaluator = evaluate_sampled at tol 0/1/3"
  - "full_eval = true (natural distribution, all sentences)"
variants:
  - "Stage 1: 14 OpenRouter models (9 free + 5 paid)"
  - "Stage 2: temperature 0.2, top_p 0.9, presence_penalty 1.0"
  - "Stage 3: prompt families N (rarity), O (fairy few-shot), P (anti-example)"
  - "Stage 4: sentence context windows 64/32/16"
  - "Stage 5: min_gap 2–6, n-per-k rate cap"
  - "Stage 6: two-pass yes/no verifier"
  - "Stage 7: discourse cue post-processing"
  - "Stage 8: tiny LoRA on Excel corpus (optional)"
success_metric: "relaxed F1@3 ≥ 0.80 AND overprediction_ratio ≤ 2.0; stage gate F3 ≥ 0.76"
comparison_rule: "one factor at a time vs locked baseline; Stage 1 varies model only"
related_runs: []
related_artifacts: []
notion_targets:
  experiments: true
  runs: true
  artifacts: true
  decisions: false
---

## Research question

Can we beat Gemini's Excel F3 (0.76) and cut border over-prediction (currently ~5–6× gold) using free/low-cost OpenRouter models and precision-focused OFAT tweaks?

## Baseline

See [`docs/prompting/EXCEL_EXPERIMENTS_COMPARISON_REPORT.md`](../../docs/prompting/EXCEL_EXPERIMENTS_COMPARISON_REPORT.md):
- Best F3: **0.76** (Gemini 2.5 Pro, reasoning on)
- Over-segmentation is the dominant error type

## Constants

See `fixed_conditions` above and full plan [`docs/planning/EXCEL_FP_REDUCTION_OFAT_PLAN.md`](../../docs/planning/EXCEL_FP_REDUCTION_OFAT_PLAN.md).

## Variants

| Stage | Factor | How to run |
|-------|--------|------------|
| 1 | model | `bash scripts/sweeps/excel_ofat_stage1_models.sh` |
| 2 | decoding | runner CLI flags on Stage-1 winner |
| 3 | prompt N/O/P | `--prompt_family N|O|P` |
| 4 | context | `--context_mode sentences --sentence_window N` |
| 5 | post-process | `src/postprocess/run_postprocess.py --scenario all` |
| 6 | verify | `src/runners/run_two_stage_verify.py --excel_manifest ...` |
| 7 | discourse | scenario `discourse_plus_min_scene_len_3` |

## Evaluation rule

Primary: macro-averaged F1@3 across both Excel texts. Secondary: overprediction_ratio ≤ 2.0 without recall collapse. Stop early when both gates met.

## Interim conclusion

*(pending Stage 1 runs)*

## Final conclusion

*(pending)*
