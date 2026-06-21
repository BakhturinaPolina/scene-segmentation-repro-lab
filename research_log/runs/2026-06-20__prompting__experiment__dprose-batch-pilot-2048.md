---
note_type: run
run_id: run_20260620_dprose_batch_pilot_2048
title: "dProse Gemini Batch API pilot rerun (989 sentences, max_output_tokens=2048)"
date: 2026-06-20
track: prompting
run_type: experiment
status: success
goal: "Re-run full dProse batch pilot at max_output_tokens=2048 to fix 88% parse rate from 1024-token truncation; confirm parse rate ≥ 95% before full corpus."
entrypoint: "src/runners/run_dprose_batch_pilot.py"
command: "set -a && source .env && set +a && PYTHONUNBUFFERED=1 .venv/bin/python -u src/runners/run_dprose_batch_pilot.py --manifest data/manifests/dprose_pilot.json --mode file --model gemini-2.5-pro --prompt_family B --schema_file src/prompts/json_schema_label_reason.json --context_sentences 12 --temperature 0 --max_output_tokens 2048 --thinking_budget -1 --poll_interval 30 --date 2026-06-20-dprose-batch-pilot-2048"
working_directory: "."
git_commit: "1b7219d12b8c26e1153755da62a1b1df6d7eb217"
environment: ".venv + google-genai==2.9.0"
os: "Linux"
hardware: "CPU"
gpu: ""
cuda_notes: ""
api_provider: "google_gemini_batch"
api_model: "gemini-2.5-pro"
api_cost_estimate: "4.40 USD (batch pricing, from pilot_summary.json)"
dataset_assets:
  - "data/raw/dprose/dprose_100.csv"
  - "data/raw/dprose/dprose_806.csv"
  - "data/raw/dprose/dprose_2158.csv"
  - "data/manifests/dprose_pilot.json"
label_schema: "prediction-only BORDER/NOBORDER (no gold labels)"
prompt_version: "family B + json_schema_label_reason"
model_name: "gemini-2.5-pro"
varying_factor: "max_output_tokens (2048 vs 1024 baseline)"
fixed_conditions:
  - "Gemini Batch API file mode (JSONL upload)"
  - "temperature=0, thinking_budget=-1, context_sentences=12"
  - "Same manifest and prompt as 2026-06-19 pilot"
random_seed: ""
output_dir: "outputs/runs/dprose_batch/2026-06-20-dprose-batch-pilot-2048"
artifacts_expected:
  - "batch_requests.jsonl"
  - "predictions.jsonl"
  - "pilot_summary.json"
  - "job_meta.json"
artifacts_produced:
  - "outputs/runs/dprose_batch/2026-06-20-dprose-batch-pilot-2048/batch_requests.jsonl"
  - "outputs/runs/dprose_batch/2026-06-20-dprose-batch-pilot-2048/predictions.jsonl"
  - "outputs/runs/dprose_batch/2026-06-20-dprose-batch-pilot-2048/pilot_summary.json"
  - "outputs/runs/dprose_batch/2026-06-20-dprose-batch-pilot-2048/job_meta.json"
main_metric_name: "parse_ok_rate"
main_metric_value: 0.9990
precision: ""
recall: ""
f1: ""
iou: ""
runtime: "~4.8 h batch wall (job batches/0qof7m2muid5gha07qqdwu1gxs7v10chy818; queue delay)"
failure_category: "json_parse_truncation (1 residual)"
related_experiment: "run_20260619_dprose_batch_pilot"
related_issue: ""
decision_relevance: true
notion_targets:
  roadmap: "dProse full-corpus prompting"
  runs: true
  experiments: true
  artifacts: true
  issues: false
  decisions: false
---

## Objective

Resolve parse failures from the 2026-06-19 pilot (118/989 at max_output_tokens=1024) by re-running all 989 sentences at max_output_tokens=2048.

## What was held constant

- Same manifest, prompt Family B, model, temperature, thinking_budget, context window
- Batch file mode (989 requests)

## What changed

- `max_output_tokens`: 1024 → **2048** (only varying factor)
- New output tag: `2026-06-20-dprose-batch-pilot-2048`

## Outcome

| Metric | 1024 pilot | **2048 rerun** |
|--------|------------|----------------|
| request_count | 989 | 989 |
| parse_ok_rate | 88.07% (871/989) | **99.90% (988/989)** |
| fail_count | 118 | **1** |
| avg_input_tokens | 934.1 | 934.1 |
| avg_output_tokens | 65.4 | 72.8 |
| avg_thought_tokens | 692.6 | 701.0 |
| label_counts | NOBORDER=697, BORDER=174 | NOBORDER=753, BORDER=235 |
| estimated batch cost | $4.33 | **$4.40** |
| batch job | batches/8kqap0h1821rrmsnqu0d7n7rohjxw8qd44gm | batches/0qof7m2muid5gha07qqdwu1gxs7v10chy818 |

Single residual failure: `dprose_100:22` — thought_tokens=1973 exceeded 2048 ceiling; truncated `reason` string.

## Interpretation

Raising max_output_tokens from 1024 to 2048 fixes the truncation problem (118 → 1 failure). Parse rate exceeds the 95% bar. Config validated for full 120k corpus run. Residual edge case may need 4096 or thinking_budget cap on retry.

## Next step

Proceed to full corpus: chunk 327 files into ~10–20 JSONL batches (~6k–12k req each) at max_output_tokens=2048.
