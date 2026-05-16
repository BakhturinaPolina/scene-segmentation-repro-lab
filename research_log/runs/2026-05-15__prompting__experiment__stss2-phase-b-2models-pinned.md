---
note_type: run
run_id: run_20260515_stss2_prompting_phase_b_2models_pinned
title: "STSS-Test-2 Phase B model search (2 pinned free models × kept families B/E/D)"
date: 2026-05-15
track: prompting
run_type: experiment
status: partial
goal: "Run §5.2 Phase B: kept families {B, E, D} on pinned free models; below-spec model count due to free-inventory constraints documented in issue__api__openrouter-free-inventory-phase-b-constraint."
entrypoint: "src/run_prompting_stratified.py (driven by scripts/phase_b_sweep.sh)"
command: "OPENROUTER_API_KEY=<provided-in-session> bash scripts/phase_b_sweep.sh"
working_directory: "."
git_commit: "c869f5d"
environment: ".venv-gpu"
os: "Linux"
hardware: "CPU"
gpu: ""
cuda_notes: ""
api_provider: "openrouter"
api_model: "openai/gpt-oss-120b:free (carry-over: nvidia/nemotron-3-super-120b-a12b:free)"
api_cost_estimate: "$0.00 (free tier)"
dataset_assets:
  - "data/manifest_stss_test_2.json"
  - "upstream/scene-segmentation/data/full/stss_test_2/Aus guter Familie.xmi.zip"
  - "upstream/scene-segmentation/data/full/stss_test_2/Effi Briest.xmi.zip"
label_schema: "Coarse (BORDER / NOBORDER) via get_label_simple"
prompt_version: "registry v1.0 templates B, E, D at src/prompts/"
model_name: "openai/gpt-oss-120b:free + carry-over nvidia/nemotron-3-super-120b-a12b:free"
varying_factor: "model (nemotron-super-120b vs gpt-oss-120b) × prompt_family (B,E,D)"
fixed_conditions:
  - "max_per_class=15"
  - "reasoning=low"
  - "temperature=0.0"
  - "top_p=1.0"
  - "seed=1337"
  - "max_tokens=256"
  - "context_size=409 (default 512*0.8)"
  - "chunk_window=2 (H/I)"
  - "score_threshold=50 (I)"
  - "response_format=json_schema with src/prompts/json_schema_label_reason.json (B, E, D)"
random_seed: 1337
output_dir: "outputs/prompting/2026-05-15-phaseB/ (gpt-oss only) + outputs/prompting/2026-05-15-phaseA/ (nemotron carry-over)"
artifacts_expected:
  - "strat_<model>_family{B,E,D}_reasoning-low/{command.txt,config.json,cache_*.json,results_*.json,review_*.jsonl,review_schema.json,summary.json}"
artifacts_produced:
  - "outputs/prompting/2026-05-15-phaseB/strat_openai_gpt-oss-120b_free_family{B,E,D}_reasoning-low/summary.json (3 dirs)"
  - "outputs/prompting/2026-05-15-phaseA/strat_nvidia_nemotron-3-super-120b-a12b_free_family{B,E,D}_reasoning-low/ (carry-over)"
  - "logs/phaseB/*.log"
  - "logs/phase_b_driver.log"
  - "research_log/issues/issue__api__openrouter-free-inventory-phase-b-constraint.md"
main_metric_name: "macro_avg F1 (tol=0)"
main_metric_value: "0.862 (Nemotron Super + family B winner)"
precision: "0.864"
recall: "0.867"
f1: "0.862"
iou: ""
runtime: "~78 min wall-clock for gpt-oss-120b × 3 families; reruns of nemotron-super used Phase A cache (3 min total)"
failure_category: "api inventory constraint (3 swap attempts blocked)"
related_experiment: "experiment__prompting__model__free-120b-comparison"
related_issue: "issue_api_openrouter_free_inventory_phase_b_constraint"
decision_relevance: false
notion_targets:
  roadmap: "Phase 5 §5.2 Phase B"
  runs: true
  experiments: true
  artifacts: true
  issues: true
  decisions: false
---

## Objective

Execute §5.2 Phase B: run the kept prompt families from Phase A ({B, E, D}) on
3–5 pinned free OpenRouter models at the same locked controls used in Phase A,
to identify the top 1–2 (model, family) combinations.

## What was held constant

Same locked controls as Phase A:
- `max_per_class=15`, `reasoning=low`, `temperature=0.0`, `top_p=1.0`, `seed=1337`,
  `max_tokens=256`, `context_size=409`, `chunk_window=2`, `score_threshold=50`.
- `response_format=json_schema` with `src/prompts/json_schema_label_reason.json`
  for all three kept families (B, E, D).

## What changed

- Model varied across {`nvidia/nemotron-3-super-120b-a12b:free` (carry-over from
  Phase A), `openai/gpt-oss-120b:free`}.
- Prompt family varied across {B, E, D}.

## Inventory swap attempts (all dropped)

The plan specified 3–5 pinned free models. Three swap attempts were dropped at
the locked controls before settling on the 2-model bucket. Full root-cause
matrix is in
[issue__api__openrouter-free-inventory-phase-b-constraint](../issues/issue__api__openrouter-free-inventory-phase-b-constraint.md):

- `meta-llama/llama-3.3-70b-instruct:free`, `qwen/qwen3-next-80b-a3b-instruct:free`,
  `nousresearch/hermes-3-llama-3.1-405b:free` — sustained Venice provider HTTP 429.
- `nvidia/nemotron-nano-9b-v2:free`, `z-ai/glm-4.5-air:free` — reasoning content
  saturates `max_tokens=256`; ~10–20 retries per sentence; 100–220 s/sentence.
- `google/gemma-4-31b-it:free` — sustained Google AI Studio rate-limit on the
  runner's polling cadence.

## Outcome

All 6 (model, family) runs in the 2-model bucket finished with exit=0. Aggregate
parse failure rate: 0.

| Rank | Model | Family | F1@0 | P@0 | R@0 | F1@1 | F1@3 | parse_fail | avg_lat (s) |
|------|-------|--------|------|-----|-----|------|------|------------|-------------|
| 1 | nemotron-super-120b | B | 0.862 | 0.864 | 0.867 | 0.877 | 0.891 | 0.000 | 8.04 |
| 2 | nemotron-super-120b | E | 0.821 | 0.887 | 0.767 | 0.852 | 0.868 | 0.000 | 6.60 |
| 3 | gpt-oss-120b | B | 0.769 | 0.909 | 0.667 | 0.823 | 0.823 | 0.000 | 31.84 |
| 4 | gpt-oss-120b | D | 0.763 | 0.840 | 0.700 | 0.815 | 0.829 | 0.000 | 24.97 |
| 5 | gpt-oss-120b | E | 0.757 | 0.885 | 0.667 | 0.785 | 0.785 | 0.000 | 18.60 |
| 6 | nemotron-super-120b | D | 0.747 | 0.677 | 0.833 | 0.772 | 0.794 | 0.000 | 7.46 |

## Interpretation

- **Nemotron Super 120B sweeps the top 2 slots.** Family B (zero-shot JSON) is
  the headline winner with the best F1@0 in the entire campaign so far
  (0.862, balanced P/R).
- **gpt-oss-120b is the precision specialist.** All three of its kept-family
  rows show P ≥ 0.840 but R ≈ 0.667 — consistent with its prior characterization
  in `experiment__prompting__model__free-120b-comparison.md` ("pure
  under-detection" mode).
- **Latency split**: gpt-oss-120b is ~3–4× slower than Nemotron Super at the
  same controls (provider differences in reasoning trace handling).
- **Family D is recall-friendly for Nemotron** but recall-neutral for gpt-oss,
  suggesting the few-shot balanced examples interact with the generative style
  of each model differently.
- **Inventory constraint is real**: only 2 models in the current free inventory
  are practical at the §5.2 locked controls. The §5.2 spec calls for one
  reasoning-capable model, but every reasoning model in the inventory exhausts
  the 256-token budget on chain-of-reasoning content. Recorded as an open
  issue; may motivate adding a new factor axis E7 (max_tokens) in a follow-up.

## Selection for Phase C

Top 1–2 (model, family) combos per §5.2 keep/drop rule:

1. **nemotron-super-120b + family B** — F1@0=0.862, P=0.864, R=0.867.
2. **nemotron-super-120b + family E** — F1@0=0.821, P=0.887, R=0.767 (precision
   variant retained for Phase C contrast).

Both promote into Phase C.

## Next step

Phase C: rerun the two surviving combos with `--max_per_class 0` (full
stratified, ~892 sentences/run) to lock headline numbers, then run §5.2
follow-up axes E3/E4/E5/E6 one factor at a time.
