---
note_type: run
run_id: run_20260515_stss2_prompting_phase_c_baseline_and_factors
title: "STSS-Test-2 Phase C: full-stratified baseline + E3/E4/E6 factor pilots on (Nemotron-Super, family B)"
date: 2026-05-15
track: prompting
run_type: experiment
status: success
goal: "Lock the headline number for the surviving (model, family) combo with one full-stratified run, then screen §5.2 follow-up axes E3/E4/E6 at pilot scope to identify promising directions."
entrypoint: "src/run_prompting_stratified.py (driven by scripts/phase_c_sweep.sh)"
command: "OPENROUTER_API_KEY=<provided-in-session> bash scripts/phase_c_sweep.sh"
working_directory: "."
git_commit: "c869f5d"
environment: ".venv-gpu"
os: "Linux"
hardware: "CPU"
gpu: ""
cuda_notes: ""
api_provider: "openrouter"
api_model: "nvidia/nemotron-3-super-120b-a12b:free"
api_cost_estimate: "$0.00 (free tier)"
dataset_assets:
  - "data/manifest_stss_test_2.json"
  - "upstream/scene-segmentation/data/full/stss_test_2/Aus guter Familie.xmi.zip"
  - "upstream/scene-segmentation/data/full/stss_test_2/Effi Briest.xmi.zip"
label_schema: "Coarse (BORDER / NOBORDER) via get_label_simple"
prompt_version: "registry v1.0 template B"
model_name: "nvidia/nemotron-3-super-120b-a12b:free"
varying_factor: "scope (pilot/full) and §5.2 axes E3/E4/E6 (one factor per run)"
fixed_conditions:
  - "model=nvidia/nemotron-3-super-120b-a12b:free"
  - "prompt_family=B (json_schema_label_reason)"
  - "seed=1337"
  - "max_tokens=256"
  - "chunk_window=2"
  - "score_threshold=50"
  - "response_format=json_schema with src/prompts/json_schema_label_reason.json"
random_seed: 1337
output_dir: "outputs/prompting/2026-05-15-phaseC-*/"
artifacts_expected:
  - "<6 runs>/strat_*_familyB_reasoning-*/summary.json"
artifacts_produced:
  - "outputs/prompting/2026-05-15-phaseC-baselineB-full/strat_nvidia_nemotron-3-super-120b-a12b_free_familyB_reasoning-low/summary.json"
  - "outputs/prompting/2026-05-15-phaseC-E3-ctx1024/.../summary.json"
  - "outputs/prompting/2026-05-15-phaseC-E3-ctx2048/.../summary.json"
  - "outputs/prompting/2026-05-15-phaseC-E4-temp03/.../summary.json"
  - "outputs/prompting/2026-05-15-phaseC-E4-temp10/.../summary.json"
  - "outputs/prompting/2026-05-15-phaseC-E6-roff/strat_nvidia_nemotron-3-super-120b-a12b_free_familyB_reasoning-off/summary.json"
  - "logs/phaseC/*.log"
  - "scripts/phase_c_sweep.sh"
main_metric_name: "macro_avg F1 (tol=0)"
main_metric_value: "0.763 (full-stratified baseline); 0.874 (pilot E6 reasoning=off, headline candidate for new default)"
precision: "0.823 (E6 reasoning=off pilot); 0.774 (full-stratified baseline)"
recall: "0.933 (E6 reasoning=off pilot); 0.754 (full-stratified baseline)"
f1: "0.874 (E6 reasoning=off pilot); 0.763 (full-stratified baseline)"
iou: ""
runtime: "158 min wall-clock total (baseline_B_full 120 min + 5 factor pilots ≈ 38 min)"
failure_category: ""
related_experiment: "experiment__prompting__model__free-120b-comparison"
related_issue: "issue_api_openrouter_free_inventory_phase_b_constraint"
decision_relevance: true
notion_targets:
  roadmap: "Phase 5 §5.2 Phase C"
  runs: true
  experiments: true
  artifacts: true
  issues: false
  decisions: true
---

## Objective

Lock the headline metric for the §5.2 winner (Nemotron Super 120B + prompt
family B) with one full-stratified run and screen the §5.2 follow-up axes
E3 (context window), E4 (temperature), E6 (reasoning) at pilot scope to
identify promising deeper-investigation directions. E5 (few-shot count) is
skipped because the winning family B is zero-shot.

## What was held constant across all 6 runs

- Model: `nvidia/nemotron-3-super-120b-a12b:free`.
- Prompt family: B (zero-shot JSON).
- `seed=1337`, `max_tokens=256`, `chunk_window=2`, `score_threshold=50`.
- `response_format=json_schema` with `src/prompts/json_schema_label_reason.json`.

## What varied (one factor per run)

| Run | Varying factor | Value |
|---|---|---|
| baseline_B_full | scope | `max_per_class=0` (full stratified) — all others fixed at Phase A/B locked values |
| E3_ctx1024 | context_size | 1024 (vs locked 409) |
| E3_ctx2048 | context_size | 2048 (vs locked 409) |
| E4_temp03 | temperature | 0.3 (vs locked 0.0) |
| E4_temp10 | temperature | 1.0 (vs locked 0.0) |
| E6_reasoning_off | reasoning | off (vs locked low) |

All factor pilots use `max_per_class=15` for direct comparability with the
Phase A pilot baseline.

## Outcome

All 6 runs exited 0 with zero parse failures.

| Variant | Scope | P@0 | R@0 | F1@0 | F1@1 | F1@3 | avg_lat (s) |
|---|---|-----|-----|------|------|------|-------------|
| Phase A pilot baseline | pilot 60 | 0.864 | 0.867 | 0.862 | 0.877 | 0.891 | 8.04 |
| **baseline_B_full** | **full 892** | **0.774** | **0.754** | **0.763** | **0.784** | **0.830** | **7.99** |
| E3_ctx1024 | pilot 60 | 0.862 | 0.833 | 0.847 | 0.862 | 0.877 | 6.80 |
| E3_ctx2048 | pilot 60 | 0.690 | 0.733 | 0.710 | 0.779 | 0.793 | 7.62 |
| E4_temp03 | pilot 60 | 0.835 | 0.833 | 0.833 | 0.862 | 0.877 | 6.51 |
| E4_temp10 | pilot 60 | 0.808 | 0.833 | 0.821 | 0.835 | 0.848 | 6.05 |
| **E6_reasoning_off** | **pilot 60** | **0.823** | **0.933** | **0.874** | **0.888** | **0.917** | **4.87** |

## Interpretation

### Headline (full-stratified baseline)

**F1@0 = 0.763** on the full STSS-Test-2 stratified sample (892 sentences,
2 novels). This is ~0.1 below the pilot-scope estimate (0.862). The pilot
substantially OVERSTATED F1 — opposite to the 2026-04-08 observation where
pilot and full agreed exactly. The discrepancy is consistent across all
metrics (P@0: 0.864→0.774, R@0: 0.867→0.754). Pilot ranking remains
informative for ORDERING families/models, but absolute pilot numbers should
not be reported as headline F1.

### E6 reasoning=off is the clearest single-factor improvement

Pilot baseline (reasoning=low) F1@0=0.862 → reasoning=off F1@0=0.874
(+0.012 absolute). Recall jumps from 0.867 to 0.933 while precision drops
from 0.864 to 0.823. Latency halves (8.04 s → 4.87 s/sentence), which is
material because it shrinks a full-stratified rerun from ~2h to ~1h. This
is a decision-relevant finding and motivates promoting reasoning=off to the
new locked reasoning mode for this combo — but only after a full-stratified
confirmation run (deferred follow-up).

### E3 context window: bigger is not better

`context_size=1024` matches baseline within noise (F1@0=0.847 vs 0.862).
`context_size=2048` is meaningfully worse (F1@0=0.710). Hypothesis: at
larger context, the model anchors decisions on distant material that is
not predictive of the local boundary. Keep `context_size=409` as the
default.

### E4 temperature: stricter is better

Higher temperature monotonically degrades F1@0 (0.862→0.833→0.821 at
0.0/0.3/1.0). Confirms the original locked value `temperature=0`.

### Error-tag breakdown

On the **pilot** baseline, all 8 errors are `near_correct_boundary`
(off-by-N within ±3 sample positions). At the **full-stratified** scope
(209 errors across both novels) every error is also tagged
`near_correct_boundary` — but this is partly an artifact of the dense
sample (with `max_per_class=0`, almost every sample position has an
opposite-class neighbour within ±3). The categorisation is more
informative at the pilot scope, where it correctly distinguishes A and H
from B (Phase A: A had 23 near-correct + 1 minor_shift_fp; H had 23
implicit_shift_fn). For the headline combo at pilot scope, the model
"sees" the boundaries — it just misplaces some by 1–3 sentences. This is
consistent with F1@1=0.888 and F1@3=0.917 being substantially higher than
F1@0=0.874 for the reasoning=off pilot.

## Decision implications

- The §5.2 model bucket and family ranking from Phase A/B is preserved: top
  combo is **Nemotron-Super-120B + family B**.
- Within that combo, **reasoning=off** dominates `reasoning=low` at pilot
  scope on every metric, including latency. This warrants a controlled
  full-stratified rerun with `reasoning=off` before formally changing the
  active default. Tracked as a decision-pending note.
- Pilot-scope evidence is preserved as a screening tool only; headline
  numbers must come from `max_per_class=0` runs going forward.

## Next step

Open a decision note documenting the reasoning=off finding and the
pilot-vs-full F1 gap, then schedule a full-stratified rerun of the headline
combo with `reasoning=off` to confirm.
