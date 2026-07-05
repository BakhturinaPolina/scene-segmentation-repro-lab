---
note_type: run
run_id: run_20260702_dprose_full_wave06
title: "dProse full corpus wave 06 (58 books, €100 budget cap)"
date: 2026-07-02
track: prompting
run_type: experiment
status: success
goal: "Continue resumable full-corpus dProse prompting after Wave 5; process next ~58 books within €100 budget cap."
entrypoint: "src/runners/run_dprose_batch_corpus.py"
command: "bash scripts/sweeps/run_dprose_wave.sh data/manifests/waves/wave_06_eur100.json 467.35"
working_directory: "."
git_commit: "e9dede3"
environment: ".venv + google-genai"
os: "Linux"
hardware: "CPU"
gpu: ""
cuda_notes: ""
api_provider: "google_gemini_batch"
api_model: "gemini-2.5-pro"
api_cost_estimate: "90.46 USD planned (cumulative cap $467.35)"
dataset_assets:
  - "data/manifests/dprose_full.json"
  - "data/manifests/waves/wave_06_eur100.json"
label_schema: "prediction-only BORDER/NOBORDER (no gold labels)"
prompt_version: "family B + json_schema_label_reason"
model_name: "gemini-2.5-pro"
varying_factor: "wave budget (€100 wave 6)"
fixed_conditions:
  - "Gemini Batch API file mode, one job per book"
  - "temperature=0, thinking_budget=-1, context_sentences=12, max_output_tokens=2048"
random_seed: ""
output_dir: "outputs/runs/dprose_batch/dprose-full-corpus"
artifacts_expected:
  - "corpus_progress.json"
  - "books/<slug>/predictions.jsonl"
  - "logs/dprose/wave_wave_06_eur100_2026-07-02.log"
artifacts_produced: []
main_metric_name: "parse_ok_rate"
main_metric_value: ""
precision: ""
recall: ""
f1: ""
iou: ""
runtime: ""
failure_category: ""
related_experiment: "run_20260701_dprose_full_wave05"
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

Run Wave 6 after Wave 5 completion (238/327 books). Manifest: `dprose_1983` … `dprose_2312` (58 books, ~20,333 sentences).

## Pre-flight

```bash
.venv/bin/python scripts/data/plan_dprose_waves.py \
  --budget_eur 100 \
  --exclude_completed outputs/runs/dprose_batch/dprose-full-corpus/corpus_progress.json \
  --output data/manifests/waves/wave_06_eur100.json

DRY_RUN=1 bash scripts/sweeps/run_dprose_wave.sh \
  data/manifests/waves/wave_06_eur100.json 467.35
```

Cumulative cap: $374.96 prior API spend + $92.39 wave headroom = **$467.35**.

## Execution

```bash
bash scripts/sweeps/run_dprose_wave.sh data/manifests/waves/wave_06_eur100.json 467.35
```

## Progress tracking

- Log: `logs/dprose/wave_wave_06_eur100_2026-07-02.log`
- Progress artifact: `outputs/runs/dprose_batch/dprose-full-corpus/corpus_progress.json`
- Spot-check doc: `docs/corpora/DPROSE_CORPUS_SPOT_CHECKS.md`

## Outcome

**Success** — completed 2026-07-03 (~4.4h session).

| Metric | Value |
|--------|-------|
| Books processed | 58 / 58 |
| Corpus after wave | 296 / 327 books, 108,523 / 120,369 sentences |
| Wave spend | ~$88.90 ($463.86 − $374.96 prior) |
| Budget cap | $467.35 — **not hit** |
| Log | `logs/dprose/wave_wave_06_eur100_2026-07-02.log` |

All batch jobs succeeded (exit 0). No upload throttling; no API incidents.
