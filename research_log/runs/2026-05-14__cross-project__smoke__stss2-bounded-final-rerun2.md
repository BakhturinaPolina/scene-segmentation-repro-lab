---
note_type: run
run_id: run_20260514_stss2_bounded_final_rerun2
title: "STSS-Test-2 bounded full verification (final rerun2)"
date: 2026-05-14
track: cross-project
run_type: smoke
status: partial
goal: "Execute one full bounded STSS-Test-2 reproducibility run with live API-enabled prompting and fixed heavy-step timeout."
entrypoint: "src/reproduce_stss_test_2.py"
command: "OPENROUTER_API_KEY=*** python3 src/reproduce_stss_test_2.py --date 2026-05-14-final-rerun2 --heavy_timeout_seconds 1800"
working_directory: "."
git_commit: "dc1c3fb"
environment: ".venv-gpu"
os: "Linux"
hardware: "RTX 2070 8GB + CPU"
gpu: "RTX 2070 8GB"
cuda_notes: "Heavy steps bounded to 1800s by wrapper-level timeout."
api_provider: "openrouter"
api_model: "nvidia/nemotron-3-super-120b-a12b:free"
api_cost_estimate: ""
dataset_assets:
  - "upstream/scene-segmentation/data/full/stss_test_2/Aus guter Familie.xmi.zip"
  - "upstream/scene-segmentation/data/full/stss_test_2/Effi Briest.xmi.zip"
label_schema: "binary boundary (BORDER/NOBORDER)"
prompt_version: "Phase 4 smoke defaults"
model_name: "mixed (prompting + SSC bert-base-german-cased + LLaMA Phi-3-mini-4bit)"
varying_factor: "none"
fixed_conditions:
  - "Single orchestrator entrypoint: src/reproduce_stss_test_2.py"
  - "Heavy-step timeout fixed to 1800 seconds"
  - "Same STSS-Test-2 local dataset and manifest"
random_seed: ""
output_dir: "outputs/reproduction/2026-05-14-final-rerun2/stss_test_2/"
artifacts_expected:
  - "command.txt"
  - "config.json"
  - "manifest.json"
artifacts_produced:
  - "outputs/reproduction/2026-05-14-final-rerun2/stss_test_2/command.txt"
  - "outputs/reproduction/2026-05-14-final-rerun2/stss_test_2/config.json"
  - "outputs/reproduction/2026-05-14-final-rerun2/stss_test_2/manifest.json"
main_metric_name: "successful_steps"
main_metric_value: 5
precision: ""
recall: ""
f1: ""
iou: ""
runtime: "4379s total wall time (from terminal footer)"
failure_category: "mixed_timeout_and_runtime_error"
related_experiment: ""
related_issue: ""
decision_relevance: true
notion_targets:
  roadmap: "Phase 4 stabilization"
  runs: true
  experiments: ""
  artifacts: true
  issues: true
  decisions: true
---

## Objective

Run one complete bounded STSS-Test-2 verification pass and capture authoritative step status in a manifest.

## What was held constant

- Entrypoint and orchestration sequence in `src/reproduce_stss_test_2.py`.
- Dataset and manifest paths for STSS-Test-2.
- Heavy timeout cap fixed at 1800 seconds for SSC and LLaMA wrappers.

## What changed

- Prompting dependencies in `.venv-gpu` were aligned to run upstream prompting code (`langchain==0.1.9`, `openai` installed).
- A clean rerun was executed under date tag `2026-05-14-final-rerun2`.

## Outcome

Final manifest reports 7 steps total:

- Success: `verify_data_manifest`, `unit_tests`, `prompting_baseline_smoke`, `prompting_stratified_smoke`, `prompting_phase_a_smoke`
- Failed: `ssc_baseline` (`exit_code=124`, timeout at 1800s), `llama_baseline` (`exit_code=1`)

LLaMA failure root cause from stderr: fused loss path raised a shape mismatch (`Expected input batch_size (128) to match target batch_size (234)`).

## Interpretation

The end-to-end reproducibility orchestration is now operational and produces deterministic run artifacts and step statuses. Prompting reproducibility is live and successful under bounded execution, while heavy GPU training steps remain unstable/unfinished under the current runtime constraints and upstream stack behavior.

## Next step

Keep the heavy timeout cap fixed at 1800s in docs and future runs, then triage SSC/LLaMA heavy-step failures separately (timeout budget strategy for SSC, runtime-shape bug for LLaMA) without changing the bounded verification protocol.
