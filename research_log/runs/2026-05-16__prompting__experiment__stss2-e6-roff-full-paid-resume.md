---
note_type: run
run_id: run_20260516_stss2_prompting_e6_roff_full_paid_resume
title: "STSS-Test-2 E6 reasoning=off full run completed via non-free Nemotron resume"
date: 2026-05-16
track: prompting
run_type: experiment
status: success
goal: "Finish the full-stratified E6 reasoning=off run after free-tier daily quota exhaustion, preserving prior cache progress and confirming full-scope metrics."
entrypoint: "src/run_prompting_stratified.py"
command: "OPENROUTER_API_KEY=<provided-in-session> PYTHONUNBUFFERED=1 .venv/bin/python -u src/run_prompting_stratified.py --model nvidia/nemotron-3-super-120b-a12b --prompt_family B --max_per_class 0 --reasoning off --temperature 0 --top_p 1.0 --seed 1337 --max_tokens 256 --response_format json_schema --schema_file src/prompts/json_schema_label_reason.json --chunk_window 2 --score_threshold 50 --date 2026-05-16-phaseC-E6-roff-full --request_delay 1.5 --max_consecutive_rate_limits 8 --rate_limit_burst_threshold 5 --rate_limit_cooldown 180"
working_directory: "."
git_commit: "c869f5d"
environment: ".venv"
os: "Linux"
hardware: "CPU"
gpu: ""
cuda_notes: ""
api_provider: "openrouter"
api_model: "nvidia/nemotron-3-super-120b-a12b (non-free)"
api_cost_estimate: "~$0.02 (estimated for the 192 uncached requests completed in paid mode)"
dataset_assets:
  - "data/manifest_stss_test_2.json"
  - "upstream/scene-segmentation/data/full/stss_test_2/Aus guter Familie.xmi.zip"
  - "upstream/scene-segmentation/data/full/stss_test_2/Effi Briest.xmi.zip"
label_schema: "Coarse (BORDER / NOBORDER) via get_label_simple"
prompt_version: "registry v1.0 template B"
model_name: "nvidia/nemotron-3-super-120b-a12b"
varying_factor: "provider tier/routing for completion path (free->non-free resume) with reasoning=off fixed"
fixed_conditions:
  - "prompt_family=B"
  - "reasoning=off"
  - "seed=1337"
  - "temperature=0.0"
  - "top_p=1.0"
  - "max_tokens=256"
  - "response_format=json_schema with src/prompts/json_schema_label_reason.json"
  - "max_per_class=0 (full stratified)"
random_seed: 1337
output_dir: "outputs/prompting/2026-05-16-phaseC-E6-roff-full/strat_nvidia_nemotron-3-super-120b-a12b_familyB_reasoning-off/"
artifacts_expected:
  - "summary.json"
  - "cache_Aus_guter_Familie.json"
  - "cache_Effi_Briest.json"
  - "command.txt"
  - "config.json"
artifacts_produced:
  - "outputs/prompting/2026-05-16-phaseC-E6-roff-full/strat_nvidia_nemotron-3-super-120b-a12b_familyB_reasoning-off/summary.json"
  - "outputs/prompting/2026-05-16-phaseC-E6-roff-full/strat_nvidia_nemotron-3-super-120b-a12b_familyB_reasoning-off/cache_Aus_guter_Familie.json"
  - "outputs/prompting/2026-05-16-phaseC-E6-roff-full/strat_nvidia_nemotron-3-super-120b-a12b_familyB_reasoning-off/cache_Effi_Briest.json"
  - "outputs/prompting/2026-05-16-phaseC-E6-roff-full/strat_nvidia_nemotron-3-super-120b-a12b_familyB_reasoning-off/command.txt"
  - "outputs/prompting/2026-05-16-phaseC-E6-roff-full/strat_nvidia_nemotron-3-super-120b-a12b_familyB_reasoning-off/config.json"
main_metric_name: "macro_avg F1 (tol=0)"
main_metric_value: 0.7733
precision: 0.7788
recall: 0.7718
f1: 0.7733
iou: ""
runtime: "11m38s (elapsed_ms=697827)"
failure_category: ""
related_experiment: "experiment__prompting__stss2-section52-campaign"
related_issue: "issue__api__openrouter-free-inventory-phase-b-constraint"
decision_relevance: true
notion_targets:
  roadmap: "Phase 5 §5.2 E6 full confirmation"
  runs: true
  experiments: true
  artifacts: true
  issues: false
  decisions: true
---

## Objective

Complete the full-stratified E6 (`reasoning=off`) STSS-Test-2 run after the free-tier route reached daily quota (`X-RateLimit-Remaining: 0`) and verify full-scope metrics.

## What was held constant

- Prompt family: `B` (zero-shot JSON).
- Decoding controls: `temperature=0.0`, `top_p=1.0`, `max_tokens=256`, `seed=1337`.
- Output schema: `response_format=json_schema` with `src/prompts/json_schema_label_reason.json`.
- Evaluation scope: STSS-Test-2 stratified full (`max_per_class=0`) on both novels.

## What changed

- Switched from `nvidia/nemotron-3-super-120b-a12b:free` to `nvidia/nemotron-3-super-120b-a12b` (non-free) to bypass daily free-tier quota exhaustion.
- Seeded the paid output directory with existing free-run caches, then resumed only uncached items.

## Outcome

- Run exited successfully (`exit_code: 0`).
- Final summary: `outputs/prompting/2026-05-16-phaseC-E6-roff-full/strat_nvidia_nemotron-3-super-120b-a12b_familyB_reasoning-off/summary.json`.
- Aggregate metrics:
  - `macro_avg_tol_0`: P=0.7788, R=0.7718, F1=0.7733
  - `macro_avg_tol_1`: P=0.8122, R=0.7808, F1=0.7940
  - `macro_avg_tol_3`: P=0.8601, R=0.8054, F1=0.8303
- Parse failure rates:
  - `Aus guter Familie`: 0.0%
  - `Effi Briest`: 1.32%

## Interpretation

- E6 (`reasoning=off`) is now confirmed at full scope with strong relaxed performance (`F1@3=0.8303`) and a small strict-metric gain over the prior full baseline (`F1@0` from 0.763 to 0.7733).
- The run demonstrates operational resilience: free-tier quota limits can be mitigated without losing progress by cache-preserving resume onto non-free routing.

## Next step

- Update `docs/PROMPTING_RESULTS_REPORT.md` to mark the E6 full confirmation complete and set the recommended default prompting config to family B + reasoning off.
- For raw TXT production inference (`data/manifest_raw_txt.json`), run non-free Nemotron with the same decode controls and structured JSON output, processing all manifest files (not only the first manifest entry).
