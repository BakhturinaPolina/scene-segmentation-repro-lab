---
note_type: run
run_id: run_20260515_stss2_prompting_phase_a_family_sweep_nemotron
title: "STSS-Test-2 Phase A prompt-family sweep (A–J) on Nemotron Super 120B"
date: 2026-05-15
track: prompting
run_type: experiment
status: success
goal: "Run §5.2 Phase A prompt-family screening (A–J) on STSS-Test-2 with gold-label scoring, using a single pinned free model per user direction, in pilot stratified mode (max_per_class=15)."
entrypoint: "src/run_prompting_stratified.py (driven by scripts/phase_a_sweep.sh)"
command: "OPENROUTER_API_KEY=<provided-in-session> bash scripts/phase_a_sweep.sh"
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
prompt_version: "registry v1.0 templates A..J at src/prompts/"
model_name: "nvidia/nemotron-3-super-120b-a12b:free"
varying_factor: "prompt_family (A..J)"
fixed_conditions:
  - "model=nvidia/nemotron-3-super-120b-a12b:free"
  - "max_per_class=15"
  - "reasoning=low"
  - "temperature=0.0"
  - "top_p=1.0"
  - "seed=1337"
  - "max_tokens=256"
  - "context_size=409 (default 512*0.8)"
  - "chunk_window=2 (H/I)"
  - "score_threshold=50 (I)"
  - "response_format=json_schema with src/prompts/json_schema_label_reason.json for B,C,D,E,F,G,J"
  - "response_format=json_schema with src/prompts/json_schema_score_array.json for I"
  - "response_format=none for A and H"
random_seed: 1337
output_dir: "outputs/prompting/2026-05-15-phaseA/"
artifacts_expected:
  - "strat_<model>_family{A..J}_reasoning-low/{command.txt,config.json,cache_*.json,results_*.json,review_*.jsonl,review_schema.json,summary.json}"
artifacts_produced:
  - "outputs/prompting/2026-05-15-phaseA/strat_nvidia_nemotron-3-super-120b-a12b_free_family{A..J}_reasoning-low/summary.json (10 dirs)"
  - "logs/phaseA/family_{A..J}.log"
  - "logs/phase_a_driver.log"
  - "scripts/phase_a_sweep.sh"
  - "src/prompts/json_schema_score_array.json (new schema for family I)"
main_metric_name: "macro_avg F1 (tol=0)"
main_metric_value: "0.862 (family B winner)"
precision: "0.864 (family B)"
recall: "0.867 (family B)"
f1: "0.862 (family B)"
iou: ""
runtime: "~92 min wall-clock for 10 families (driver 22:32 → 00:04)"
failure_category: ""
related_experiment: "experiment__prompting__model__free-120b-comparison"
related_issue: ""
decision_relevance: false
notion_targets:
  roadmap: "Phase 5 §5.2 Phase A"
  runs: true
  experiments: true
  artifacts: true
  issues: false
  decisions: false
---

## Objective

Execute §5.2 Phase A on STSS-Test-2: screen prompt families A–J for scene boundary detection on a stratified pilot (max_per_class=15) using the pinned moving baseline `nvidia/nemotron-3-super-120b-a12b:free`. Per user direction this Phase A uses a single model rather than the planned two-model pair.

## What was held constant

- Single model: `nvidia/nemotron-3-super-120b-a12b:free` (decision-pinned).
- Decode: `temperature=0.0`, `top_p=1.0`, `seed=1337`, `max_tokens=256`, `reasoning=low`.
- Stratified pilot scope: `max_per_class=15` per novel × 2 novels.
- Context window: default 409 tokens.
- Chunk families: `chunk_window=2`, `score_threshold=50`.
- Structured output: family-specific. B,C,D,E,F,G,J use `json_schema_label_reason.json`. I uses the new `json_schema_score_array.json`. A and H stay free-form (their parsers handle plain tokens).

## What changed

Only `prompt_family` varied across the 10 runs (this is a screening grid per §5.2, not a single-factor controlled experiment).

## Outcome

All 10 family runs exited 0. Aggregate parse failure rate: 0/all (json_schema enforcement held).

Family ranking by `macro_avg_tol_0.f1` (tie-break recall):

| Rank | Family | Style | F1@0 | P@0 | R@0 | F1@1 | F1@3 | parse_fail | avg_chars | avg_lat (s) |
|------|--------|-------|------|-----|-----|------|------|------------|-----------|-------------|
| 1 | B | zero-shot JSON | 0.862 | 0.864 | 0.867 | 0.877 | 0.891 | 0.000 | 286.8 | 8.04 |
| 2 | E | few-shot contrastive | 0.821 | 0.887 | 0.767 | 0.852 | 0.868 | 0.000 | 119.5 | 6.60 |
| 3 | D | few-shot balanced | 0.747 | 0.677 | 0.833 | 0.772 | 0.794 | 0.000 | 112.8 | 7.46 |
| 4 | G | visible CoT rubric | 0.729 | 0.804 | 0.667 | 0.792 | 0.808 | 0.000 | 219.6 | 7.45 |
| 5 | C | zero-shot rubric JSON | 0.712 | 0.896 | 0.600 | 0.727 | 0.741 | 0.000 | 230.0 | 7.66 |
| 6 | A | zero-shot label only | 0.692 | 0.562 | 0.900 | 0.733 | 0.771 | 0.000 | 873.1 | 9.22 |
| 7 | I | scoring chunk | 0.621 | 0.643 | 0.600 | 0.655 | 0.691 | 0.000 | 144.6 | 7.92 |
| 8 | F | hidden rationale rubric | 0.586 | 0.917 | 0.433 | 0.586 | 0.598 | 0.000 | 273.0 | 7.16 |
| 9 | J | classify-after-analysis | 0.548 | 0.900 | 0.400 | 0.548 | 0.558 | 0.000 | 287.6 | 9.58 |
| 10 | H | localization chunk | 0.111 | 0.333 | 0.067 | 0.111 | 0.118 | 0.000 | 1010.2 | 9.47 |

## Interpretation

- **B (zero-shot JSON)** is the clear Phase A winner with the most balanced precision/recall (P=0.864, R=0.867). Strict JSON output without rubric or examples beats every more elaborate variant.
- **E (few-shot contrastive)** shows that minimal-pair examples nudge precision up at moderate recall cost; cheap on tokens (avg 120 chars vs 287 for B).
- **D (few-shot balanced)** trades precision for the highest recall in the JSON-output families (0.833) — useful as a recall-leaning Phase B comparator.
- **High-precision/low-recall pattern** dominates the rubric/CoT/two-stage families (C, F, J). They prune confidently but miss many borders.
- **A (label-only)** has the highest raw recall (0.900) but precision collapses (0.562); its `avg_chars=873` reveals the model emitting rationale despite the label-only instruction.
- **H (localization chunk)** with `chunk_window=2` is essentially broken (F1=0.111). The narrow chunk + free-form sentence-id output discards too much signal.
- **No parse failures across any family** — `json_schema` enforcement is reliable on this provider/model combo.

Picked for Phase B (top 3 per §5.2 keep/drop rule): **B, E, D**.

## Next step

Phase B: pick 3–5 pinned free models and run families {B, E, D} on each (still `--max_per_class 15`).
