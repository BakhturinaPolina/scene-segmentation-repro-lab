---
note_type: experiment
experiment_id: exp_prompting_stss2_section52_campaign
title: "STSS-Test-2 §5.2 prompt-family campaign on free OpenRouter inventory"
date_opened: 2026-05-15
track: prompting
status: concluded
factor_under_test: "prompt family (A–J), then model (free 120B-class), then context/temperature/reasoning"
baseline_run_id: "run_20260408_prompting_nemotron_stratified"
hypothesis: "Following the §5.2 phased protocol (A–J family sweep → model search → focused factor iteration) on STSS-Test-2 with gold-label scoring will identify a single (model, prompt family) combination that beats the 2026-04-08 nemotron-stratified baseline (F1@0=0.753 with the upstream prompt_classify)."
fixed_conditions:
  - "dataset = data/manifest_stss_test_2.json (Aus guter Familie + Effi Briest XMI)"
  - "evaluator = src/run_prompting_stratified.py (P/R/F1 at tol 0/1/3, sampled-set semantics)"
  - "decode core = temperature=0, top_p=1.0, seed=1337, max_tokens=256"
  - "response_format = json_schema with src/prompts/json_schema_label_reason.json (or json_schema_score_array.json for I, none for A and H)"
  - "context_size = 409 tokens"
  - "chunk_window = 2, score_threshold = 50 (H/I only)"
  - "reasoning = low (locked controls)"
variants:
  - "Phase A: prompt_family ∈ {A,B,C,D,E,F,G,H,I,J} on nvidia/nemotron-3-super-120b-a12b:free"
  - "Phase B: kept families {B, E, D} × {nvidia/nemotron-3-super-120b-a12b:free (carry-over), openai/gpt-oss-120b:free}"
  - "Phase C: surviving combo (Nemotron-Super + B) at full stratified and at E3/E4/E6 factor pilots"
success_metric: "macro_avg F1 at tol=0 on STSS-Test-2 stratified sample"
comparison_rule: "Higher F1@0 wins; tie-break = higher recall (recall is the documented bottleneck)"
related_runs:
  - "run_20260515_stss2_prompting_phase_a_family_sweep_nemotron"
  - "run_20260515_stss2_prompting_phase_b_2models_pinned"
  - "run_20260515_stss2_prompting_phase_c_baseline_and_factors"
  - "run_20260408_prompting_nemotron_stratified"
related_artifacts:
  - "scripts/phase_a_sweep.sh, scripts/phase_b_sweep.sh, scripts/phase_c_sweep.sh"
  - "src/error_tag_review.py"
  - "src/prompts/json_schema_score_array.json"
notion_targets:
  experiments: true
  runs: true
  artifacts: true
  decisions: true
---

## Research question

Within the §5.2 protocol and the current free OpenRouter inventory, what is the
strongest (model, prompt family) combination for scene boundary detection on
STSS-Test-2, and how do the §5.2 follow-up axes (context, temperature, few-shot,
reasoning) move headline F1?

## Baseline

`run_20260408_prompting_nemotron_stratified` — Nemotron-3-Super-120B with the
upstream `prompt_classify` prompt, `reasoning=on`, on the full stratified sample
(892 sentences). F1@0 = 0.753, F1@1 = 0.761, F1@3 = 0.792.

## Constants

See `fixed_conditions` in frontmatter.

## Variants

See `variants` in frontmatter. Three Phase B models were attempted-and-dropped
due to inventory constraints documented in
`issue__api__openrouter-free-inventory-phase-b-constraint`. Phase C E5 (few-shot
count) was skipped because the winning family (B) is zero-shot.

## Evaluation rule

Macro F1@0 on STSS-Test-2. Pilot scope (`max_per_class=15`) is used for
screening only; headline F1 must come from full stratified
(`max_per_class=0`) per `decision__pilot-vs-full-and-reasoning-off-candidate`.

## Interim conclusion

Phase A clean winner: family B (zero-shot JSON with json_schema). Phase B 
recovered the same model (Nemotron Super 120B) as the headline model. Phase C
confirmed the headline at full stratified scope (F1@0=0.763) and surfaced a
provisional follow-up: reasoning=off improves pilot F1 by +0.012 and halves
latency.

## Final conclusion

The §5.2 campaign on STSS-Test-2 selects
**(Nemotron-Super-120B, prompt family B, locked controls)** as the active
default prompting configuration at the conclusion of Phase C.

Headline at full stratified scope: **F1@0 = 0.763** (P=0.774, R=0.754,
F1@1=0.784, F1@3=0.830), based on 892 sentences across the two STSS-Test-2
novels.

This is **+0.010 F1@0 vs the 2026-04-08 upstream-`prompt_classify` baseline**
(F1@0=0.753), achieved with strict json_schema output, zero parse failures,
and 7.99 s/sentence latency.

A provisional follow-up is open via
`decision__pilot-vs-full-and-reasoning-off-candidate`: a one-time full
stratified rerun with `reasoning=off` is expected to either lift this further
(based on pilot evidence F1@0=0.874) or close the candidate as not-supported.

### Per-phase outcomes

| Phase | Scope | Winner | F1@0 | Notes |
|---|---|---|------|---|
| A (10 families × 1 model) | pilot | B | 0.862 | All 10 families parse-failure-free; H broken; A high-R/low-P |
| B (3 families × 2 models) | pilot | Nemotron-Super + B | 0.862 | gpt-oss-120b precision-strong, recall-bottlenecked; 3 candidate models dropped (Venice 429, reasoning-token saturation, Google AI Studio rate-limit) |
| C baseline | full | Nemotron-Super + B | 0.763 | Pilot overestimated by 0.099 |
| C E3 context | pilot | locked 409 | — | 1024 ~ baseline, 2048 hurts |
| C E4 temperature | pilot | locked 0 | — | 0.3 and 1.0 monotonically hurt |
| C E6 reasoning | pilot | off (provisional) | 0.874 | +0.012 vs low; latency halved; pending full-stratified confirmation |
| C E5 few-shot | n/a | — | — | Winner family B is zero-shot; not applicable |

### Error profile of the winner (pilot)

For Nemotron-Super + B at pilot scope, every error (4 FP + 4 FN) is tagged
`near_correct_boundary` by `src/error_tag_review.py` — i.e. the model "sees"
boundaries but sometimes misplaces them by 1–3 sentences. Consistent with
F1@1 (0.877) and F1@3 (0.891) being substantially higher than F1@0 (0.862).
