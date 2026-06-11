---
note_type: experiment
experiment_id: exp_f3_precision_campaign
title: "F3 precision improvement campaign (prompts + post-processing + QLoRA fine-tuning)"
date_opened: 2026-06-08
track: prompting
status: active
factor_under_test: "precision interventions (prompt wording, post-processing, fine-tuning)"
baseline_run_id: run_20260606_nemotron_full_eval_stss2
hypothesis: "Targeted precision interventions raise relaxed F1@3 on STSS-Test-2 without collapsing recall, since the Nemotron baseline over-segments (recall ~100%, precision ~12%)."
fixed_conditions:
  - "model = nvidia/nemotron-3-super-120b-a12b:free (prompt + verify stages)"
  - "temperature = 0"
  - "top_p = 1.0"
  - "seed = 1337"
  - "context_size = 409 tokens"
  - "reasoning = off"
  - "evaluator = run_prompting_stratified.evaluate_sampled / src.postprocess.evaluate_sampled (identical semantics)"
  - "corpus = data/manifests/stss_test_2.json (Effi Briest, Aus guter Familie)"
variants:
  - "prompt B (control, current default)"
  - "prompt K = B + negative examples (factor P1)"
  - "prompt L = B + strict MAJOR-discontinuity definition (factor P2)"
  - "prompt M = B + FP-pattern guard (factor P4)"
  - "post-processing: min_scene_len_3, confidence_threshold, combined (factor P3)"
  - "fine-tune: Llama-3.2-3B / Qwen2.5-3B / Gemma-2-2B QLoRA (leave-one-text-out)"
  - "two-stage verifier on predicted borders (optional)"
success_metric: "relaxed F1@3 on STSS-Test-2 (beat Step-1 true baseline); secondary precision@0 up without recall@0 collapse"
comparison_rule: "one factor at a time vs the control; pilot at --max_per_class 15 then promote winners to --full_eval"
related_runs:
  - run_20260606_nemotron_full_eval_stss2
related_artifacts:
  - art_postprocess_partial_aus_guter_familie
notion_targets:
  experiments: true
  runs: true
  artifacts: true
  decisions: true
---

## Research question

Can we raise relaxed F1@3 for German scene-boundary detection on STSS-Test-2 by
attacking precision (the bottleneck), staying under EUR 100 and preferring free
methods? Plan: [docs/planning/F3_IMPROVEMENT_PLAN.md](../../docs/planning/F3_IMPROVEMENT_PLAN.md).

## Baseline

The first true (non-stratified) baseline is the in-progress Nemotron `--full_eval`
run (prompt B, reasoning off). On the partial cache (Aus guter Familie, 819/5025
sentences) the raw model emits ~220 borders for 35 gold borders: precision ~0.11,
recall ~0.71-0.94 across tolerances, F1@3 ~0.30. See run note
[2026-06-06 baseline](../runs/2026-06-06__prompting__baseline__nemotron-full-eval-stss2.md).

## Constants

See `fixed_conditions` above. Every variant changes exactly one of: the prompt
template, a post-processing rule, the base model (fine-tune), or adds a verifier
stage. Decode settings, seed, context, and evaluator are held fixed.

## Variants

| Factor | Variant | How to run |
|--------|---------|-----------|
| P1 negatives | prompt K | `bash scripts/sweeps/precision_prompt_sweep.sh` (family K) |
| P2 strict def | prompt L | same sweep (family L) |
| P4 FP guard | prompt M | same sweep (family M) |
| P3 threshold/min-len | post-process | `python src/postprocess/run_postprocess.py --cache <cache> --scenario all` |
| fine-tune | 3 small QLoRA models | `bash src/finetune/hf_jobs/submit_job.sh` then `src/finetune/eval_finetuned.py` |
| verify | Stage-2 verifier | `python src/runners/run_two_stage_verify.py --cache <cache> ...` |

Pilot smoke (2026-06-08, family K, `--dry_run 4` on Effi Briest) confirmed the
K/L/M templates parse cleanly through the live runner (0/4 parse failures,
valid JSON label+confidence). Full pilot/sweep is queued via the script above.

## Evaluation rule

Primary: relaxed F1@3 on STSS-Test-2. Secondary: precision@0 must rise.
Control: recall@0 must not regress materially. Pilot (`--max_per_class 15`)
screens variants; winners promoted to `--full_eval`.

## Interim conclusion

Post-processing already shows strong, free precision gains on the partial cache
(see decision note `decision__postprocess-min-scene-len-3`):

| Scenario | pred borders | F1@0 | F1@1 | F1@3 |
|----------|-------------:|-----:|-----:|-----:|
| none (raw) | 220 | 0.196 | 0.245 | 0.306 |
| min_scene_len_3 | 141 | 0.239 | 0.318 | 0.393 |
| min_scene_len_5 | 109 | 0.181 | 0.278 | 0.432 |
| confidence_threshold (0.9) | 75 | 0.291 | 0.355 | 0.466 |
| confidence_threshold + min_scene_len_3 | 60 | 0.316 | 0.400 | **0.511** |

(Partial cache, Aus guter Familie, gold borders = 35. Numbers will change on the
full run; treated as directional, not final.)

## Final conclusion

_Pending: full baseline + prompt sweep + fine-tune evaluation._
