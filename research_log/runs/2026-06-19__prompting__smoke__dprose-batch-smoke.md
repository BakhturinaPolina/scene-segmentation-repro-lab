---
note_type: run
run_id: run_20260619_dprose_batch_smoke
title: "dProse Gemini Batch API smoke (5 sentences, inline)"
date: 2026-06-19
track: prompting
run_type: smoke
status: success
goal: "Validate direct Gemini Batch API integration, Prompt Family B + JSON schema, and token consumption on 5 dProse sentences before the ~989-sentence pilot."
entrypoint: "src/runners/run_dprose_batch_pilot.py"
command: "set -a && source .env && set +a && PYTHONUNBUFFERED=1 .venv/bin/python -u src/runners/run_dprose_batch_pilot.py --manifest data/manifests/dprose_pilot.json --mode inline --max_sentences 5 --model gemini-2.5-pro --prompt_family B --schema_file src/prompts/json_schema_label_reason.json --context_sentences 12 --temperature 0 --max_output_tokens 1024 --thinking_budget -1 --verbose --date 2026-06-19-dprose-batch-smoke-v2"
working_directory: "."
git_commit: "7317bd26636ebfa45ad967ae39191ce79e2610ca"
environment: ".venv + google-genai==2.9.0"
os: "Linux"
hardware: "CPU"
gpu: ""
cuda_notes: ""
api_provider: "google_gemini_batch"
api_model: "gemini-2.5-pro"
api_cost_estimate: "0.0193 USD (batch pricing, from pilot_summary.json)"
dataset_assets:
  - "data/manifests/dprose_pilot.json"
  - "data/processed/dprose/dprose_100/dprose_100__for_prompting.jsonl"
label_schema: "prediction-only BORDER/NOBORDER (no gold labels)"
prompt_version: "family B (src/prompts/B_zero_shot_json.txt) + json_schema_label_reason"
model_name: "gemini-2.5-pro"
varying_factor: "none (smoke); max_output_tokens raised to 1024 after v1 failure at 256"
fixed_conditions:
  - "Gemini Batch API inline mode"
  - "temperature=0, thinking_budget=-1 (dynamic)"
  - "context_sentences=12"
random_seed: ""
output_dir: "outputs/runs/dprose_batch/2026-06-19-dprose-batch-smoke-v2"
artifacts_expected:
  - "batch_requests.jsonl"
  - "predictions.jsonl"
  - "pilot_summary.json"
  - "job_meta.json"
artifacts_produced:
  - "outputs/runs/dprose_batch/2026-06-19-dprose-batch-smoke-v2/batch_requests.jsonl"
  - "outputs/runs/dprose_batch/2026-06-19-dprose-batch-smoke-v2/predictions.jsonl"
  - "outputs/runs/dprose_batch/2026-06-19-dprose-batch-smoke-v2/pilot_summary.json"
  - "outputs/runs/dprose_batch/2026-06-19-dprose-batch-smoke-v2/job_meta.json"
main_metric_name: "parse_ok_rate"
main_metric_value: 1.0
precision: ""
recall: ""
f1: ""
iou: ""
runtime: "~96 s wall (batch job batches/rdtcyrdwjje4p4i4lspho3uvyjp5sliwznmy)"
failure_category: ""
related_experiment: ""
related_issue: ""
decision_relevance: true
notion_targets:
  roadmap: "dProse full-corpus prompting"
  runs: true
  experiments: ""
  artifacts: true
  issues: false
  decisions: false
---

## Objective

Confirm GEMINI_API_KEY, Batch API job lifecycle, structured JSON output, and per-request token accounting on a 5-sentence inline batch before scaling to the 989-sentence file pilot.

## What was held constant

- Prompt Family B + `json_schema_label_reason.json`
- Model `gemini-2.5-pro`, batch pricing tier
- `context_sentences=12`, `temperature=0`, dynamic thinking (`thinking_budget=-1`)

## What changed

- Initial attempt (`2026-06-19-dprose-batch-smoke`, `max_output_tokens=256`) failed parse (0/5): thinking consumed the output budget, leaving no visible JSON.
- Successful rerun (`smoke-v2`) used `max_output_tokens=1024`.

## Outcome

| Metric | Value |
|--------|-------|
| parse_ok_rate | 1.0 (5/5) |
| avg_input_tokens | 1292.8 |
| avg_output_tokens | 64.6 |
| avg_thought_tokens | 545.2 |
| label_counts | BORDER=3, NOBORDER=2 |
| estimated cost | $0.019 |

Smoke pass criteria met: job `JOB_STATE_SUCCEEDED`, parse_ok_rate ≥ 0.95, labels in {BORDER, NOBORDER}.

## Interpretation

Direct Gemini Batch API works with the existing prompt stack. Input tokens (~1293) exceed the cost-estimate assumption (~620) because `context_sentences=12` produces longer prompts than the Excel token-budget builder. `max_output_tokens` must account for thinking tokens on Gemini 2.5 Pro (256 is insufficient).

## Next step

Run the 989-sentence file-mode pilot (`2026-06-19-dprose-batch-pilot`).
