---
note_type: run
run_id: run_20260606_nemotron_full_eval_stss2
title: "Nemotron-Super-120B full_eval baseline on STSS-Test-2 (true natural distribution)"
date: 2026-06-06
track: prompting
run_type: baseline
status: partial
goal: "Establish the FIRST true (non-stratified) F1@0/1/3 baseline for scene-boundary detection on STSS-Test-2 to anchor the F3 precision campaign."
entrypoint: "src/runners/run_prompting_stratified.py"
command: "python src/runners/run_prompting_stratified.py --full_eval --prompt_family B --reasoning off --model 'nvidia/nemotron-3-super-120b-a12b:free' --date 2026-06-06 --context_size 409 --temperature 0.0 --top_p 1.0 --seed 1337 --max_tokens 256"
working_directory: "."
git_commit: ""
environment: ".venv (CPU client; OpenRouter API)"
os: "Linux"
hardware: "local client, remote inference"
gpu: "n/a (API)"
cuda_notes: ""
api_provider: "OpenRouter"
api_model: "nvidia/nemotron-3-super-120b-a12b:free"
api_cost_estimate: "EUR 0 (free model)"
dataset_assets:
  - "data/manifests/stss_test_2.json"
  - "upstream/scene-segmentation/data/full/stss_test_2/ (Aus guter Familie, Effi Briest)"
label_schema: "BORDER / NOBORDER (coarse, scene level 1)"
prompt_version: "B_zero_shot_json"
model_name: "nvidia/nemotron-3-super-120b-a12b:free"
varying_factor: "none (baseline)"
fixed_conditions:
  - "temperature=0, top_p=1.0, seed=1337, context_size=409, reasoning=off"
random_seed: "1337"
output_dir: "outputs/runs/prompting/2026-06-06/full_nvidia_nemotron-3-super-120b-a12b_free_familyB_reasoning-off"
artifacts_expected:
  - "results_Aus_guter_Familie.json"
  - "results_Effi_Briest.json"
artifacts_produced:
  - "cache_Aus_guter_Familie.json (partial, 819/5025)"
main_metric_name: "relaxed F1@3 (partial)"
main_metric_value: "0.306"
precision: "0.18 (tol3, partial)"
recall: "0.94 (tol3, partial)"
f1: "0.306 (tol3, partial)"
iou: ""
runtime: "in progress"
failure_category: ""
related_experiment: "exp_f3_precision_campaign"
related_issue: ""
decision_relevance: true
notion_targets:
  roadmap: ""
  runs: true
  experiments: true
  artifacts: true
  issues: false
  decisions: true
---

## Objective

Produce the first true natural-distribution P/R/F1 at tolerances 0/1/3 for the
Nemotron baseline on STSS-Test-2. Prior numbers were stratified-inflated
(see [PROGRESS_REPORT.md](../../docs/planning/PROGRESS_REPORT.md) lines 68-95), so
this anchors every later comparison in the F3 campaign.

## What was held constant

Model, decode (temperature=0, top_p=1.0, seed=1337), context_size=409,
reasoning=off, prompt family B, evaluator `evaluate_sampled`.

## What changed

Nothing vs the campaign control; this IS the control. `--full_eval` switches from
stratified sampling to scoring every sentence (natural ~4% border rate).

## Outcome

**Partial.** Per-doc cache resumes automatically. As of 2026-06-08 the cache for
*Aus guter Familie* holds 819/5025 sentences (35 gold borders, ~220 predicted),
giving partial precision ~0.11-0.18, recall ~0.71-0.94, F1@3 ~0.306. *Effi Briest*
not yet started. Resume with the `command` above to finish both novels.

## Interpretation

The baseline over-segments: recall is high, precision very low — exactly the
profile the campaign targets. Post-processing on this partial cache already lifts
F1@3 from 0.306 to 0.511 (confidence_threshold + min_scene_len_3); see artifact
`art_postprocess_partial_aus_guter_familie` and decision
`decision__postprocess-min-scene-len-3`.

## Next step

Finish the full_eval on both novels, then record final F1@0/1/3 here and update
the experiment's Baseline section. This run note flips to `status: success` once
both `results_*.json` exist.
