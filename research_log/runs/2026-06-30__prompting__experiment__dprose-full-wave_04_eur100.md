---
note_type: run
run_id: run_20260630_dprose_full_wave04
title: "dProse full corpus wave 04 (55 books, €100 budget cap)"
date: 2026-06-30
track: prompting
run_type: experiment
status: success
goal: "Continue resumable full-corpus dProse prompting after Wave 3; process next ~55 books within €100 budget cap."
entrypoint: "src/runners/run_dprose_batch_corpus.py"
command: "bash scripts/sweeps/run_dprose_wave.sh data/manifests/waves/wave_04_eur100.json 287.47"
working_directory: "."
git_commit: ""
environment: ".venv + google-genai"
os: "Linux"
hardware: "CPU"
gpu: ""
cuda_notes: ""
api_provider: "google_gemini_batch"
api_model: "gemini-2.5-pro"
api_cost_estimate: "92.25 USD planned (cumulative cap $287.47)"
dataset_assets:
  - "data/manifests/dprose_full.json"
  - "data/manifests/waves/wave_04_eur100.json"
label_schema: "prediction-only BORDER/NOBORDER (no gold labels)"
prompt_version: "family B + json_schema_label_reason"
model_name: "gemini-2.5-pro"
varying_factor: "wave budget (€100 wave 4)"
fixed_conditions:
  - "Gemini Batch API file mode, one job per book"
  - "temperature=0, thinking_budget=-1, context_sentences=12, max_output_tokens=2048"
random_seed: ""
output_dir: "outputs/runs/dprose_batch/dprose-full-corpus"
artifacts_expected:
  - "corpus_progress.json"
  - "books/<slug>/predictions.jsonl"
  - "logs/dprose/wave_wave_04_eur100_2026-06-30.log"
artifacts_produced: []
main_metric_name: "parse_ok_rate"
main_metric_value: ""
precision: ""
recall: ""
f1: ""
iou: ""
runtime: ""
failure_category: ""
related_experiment: "run_20260630_dprose_full_wave03"
related_issue: ""
decision_relevance: false
notion_targets:
  roadmap: "dProse full-corpus prompting"
  runs: true
  experiments: true
  artifacts: true
  issues: false
  decisions: false
---

## Objective

Run Wave 4 after Wave 3 completion (124/327 books). Manifest: `dprose_1040` … (55 books, ~20,735 sentences).

## Pre-flight

```bash
.venv/bin/python scripts/data/plan_dprose_waves.py \
  --budget_eur 100 \
  --exclude_completed outputs/runs/dprose_batch/dprose-full-corpus/corpus_progress.json \
  --output data/manifests/waves/wave_04_eur100.json

DRY_RUN=1 bash scripts/sweeps/run_dprose_wave.sh \
  data/manifests/waves/wave_04_eur100.json 287.47
```

Cumulative cap: $195.08 prior API spend + $92.39 wave headroom = **$287.47**.

## Execution

```bash
bash scripts/sweeps/run_dprose_wave.sh data/manifests/waves/wave_04_eur100.json 287.47
```

## Outcome

Wave 4 **complete** (2026-07-01). 55/55 books processed; corpus **179/327** books, **67,704/120,369** sentences, **$286.20** cumulative spend (under $287.47 cap).

- Tail resume (9 books) succeeded after transient Gemini 503s on upload/poll; in-flight resume for `dprose_1506` worked.
- Parse: 54/55 books at 100%; `dprose_1535` at 99.5% (2 failed keys: `:173`, `:251`) — passes ≥95% gate.
- Log: `logs/dprose/wave_wave_04_eur100_2026-06-30.log` + `logs/dprose/wave_wave_04_eur100_2026-07-01.log`
