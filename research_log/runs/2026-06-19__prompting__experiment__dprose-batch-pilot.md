---
note_type: run
run_id: run_20260619_dprose_batch_pilot
title: "dProse Gemini Batch API pilot (989 sentences, 3 files)"
date: 2026-06-19
track: prompting
run_type: experiment
status: success
goal: "Pilot dProse scene-boundary prediction via Gemini Batch API on 989 sentences (dprose_100, dprose_806, dprose_2158) to validate token costs, parse success rate, and output quality before full 120k corpus run."
entrypoint: "scripts/data/prepare_dprose_prompting_inputs.py + src/runners/run_dprose_batch_pilot.py"
command: "set -a && source .env && set +a && .venv/bin/python scripts/data/prepare_dprose_prompting_inputs.py --files dprose_100.csv dprose_806.csv dprose_2158.csv --manifest_out data/manifests/dprose_pilot.json && PYTHONUNBUFFERED=1 .venv/bin/python -u src/runners/run_dprose_batch_pilot.py --manifest data/manifests/dprose_pilot.json --mode file --model gemini-2.5-pro --prompt_family B --schema_file src/prompts/json_schema_label_reason.json --context_sentences 12 --temperature 0 --max_output_tokens 1024 --thinking_budget -1 --poll_interval 30 --date 2026-06-19-dprose-batch-pilot"
working_directory: "."
git_commit: "7317bd26636ebfa45ad967ae39191ce79e2610ca"
environment: ".venv + google-genai==2.9.0"
os: "Linux"
hardware: "CPU"
gpu: ""
cuda_notes: ""
api_provider: "google_gemini_batch"
api_model: "gemini-2.5-pro"
api_cost_estimate: "4.33 USD (batch pricing, from pilot_summary.json)"
dataset_assets:
  - "data/raw/dprose/dprose_100.csv"
  - "data/raw/dprose/dprose_806.csv"
  - "data/raw/dprose/dprose_2158.csv"
  - "data/manifests/dprose_pilot.json"
label_schema: "prediction-only BORDER/NOBORDER (no gold labels)"
prompt_version: "family B + json_schema_label_reason"
model_name: "gemini-2.5-pro"
varying_factor: "none (pilot baseline for dProse batch path)"
fixed_conditions:
  - "Gemini Batch API file mode (JSONL upload)"
  - "temperature=0, max_output_tokens=1024, thinking_budget=-1"
  - "context_sentences=12"
random_seed: ""
output_dir: "outputs/runs/dprose_batch/2026-06-19-dprose-batch-pilot"
artifacts_expected:
  - "batch_requests.jsonl"
  - "predictions.jsonl"
  - "pilot_summary.json"
  - "job_meta.json"
artifacts_produced:
  - "outputs/runs/dprose_batch/2026-06-19-dprose-batch-pilot/batch_requests.jsonl"
  - "outputs/runs/dprose_batch/2026-06-19-dprose-batch-pilot/predictions.jsonl"
  - "outputs/runs/dprose_batch/2026-06-19-dprose-batch-pilot/pilot_summary.json"
  - "outputs/runs/dprose_batch/2026-06-19-dprose-batch-pilot/job_meta.json"
main_metric_name: "parse_ok_rate"
main_metric_value: 0.8807
precision: ""
recall: ""
f1: ""
iou: ""
runtime: "~225 s batch wall (job batches/8kqap0h1821rrmsnqu0d7n7rohjxw8qd44gm)"
failure_category: "json_parse_truncation"
related_experiment: ""
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

Execute the DPROSE_COST_ESTIMATE.md pilot recommendation: 2–3 files (~1,000 sentences) via Gemini Batch API at 50% batch pricing, measuring token usage and parse reliability.

## What was held constant

- Same prompt/model/config as smoke-v2
- Batch file input (3.9 MB JSONL, 989 requests)

## What changed

- Mode switched from inline (smoke) to file upload for scale
- Results downloaded after `JOB_STATE_SUCCEEDED`; initial parse crashed on Pydantic validation (`usageMetadata.serviceTier`) — fixed in runner, resumed via `--resume job_meta.json`

## Outcome

| Metric | Value |
|--------|-------|
| request_count | 989 |
| parse_ok_rate | 88.07% (871/989) |
| fail_count | 118 |
| avg_input_tokens | 934.1 |
| avg_output_tokens | 65.4 |
| avg_thought_tokens | 692.6 |
| label_counts | NOBORDER=697, BORDER=174 |
| estimated batch cost | $4.33 |
| batch job | batches/8kqap0h1821rrmsnqu0d7n7rohjxw8qd44gm |

Failure breakdown: 59× `no_json_found`, 59× truncated/malformed JSON (mostly unterminated strings in `reason` field) — likely `max_output_tokens=1024` exhausted by long thinking on hard sentences.

## Interpretation

Batch path is viable at ~$4.4 per 1k sentences (below $10 pilot budget). Token averages differ from cost doc: input ~934 vs ~620 estimated; output+thinking ~758 vs ~700 estimated. Parse rate 88% is below the 95% smoke bar — recommend raising `max_output_tokens` (e.g. 2048) or capping `thinking_budget` before full corpus.

## Resolution

Parse failures resolved by full rerun at `max_output_tokens=2048` — see [2026-06-20 pilot rerun](2026-06-20__prompting__experiment__dprose-batch-pilot-2048.md) (99.90% parse rate, 988/989).

## Next step

Proceed to full 327-file corpus in chunked JSONL batches at max_output_tokens=2048.
