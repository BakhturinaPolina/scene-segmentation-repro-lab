---
note_type: run
run_id: run_20260628_dprose_full_wave01_dryrun
title: "dProse full corpus wave 01 dry-run (15 books, €25 budget cap)"
date: 2026-06-28
track: prompting
run_type: dry-run
status: success
goal: "Validate resumable per-book corpus orchestrator, wave manifest, and budget cap before spending Wave 1 API credits (~€25 balance)."
entrypoint: "src/runners/run_dprose_batch_corpus.py"
command: "DRY_RUN=1 bash scripts/sweeps/run_dprose_wave.sh data/manifests/waves/wave_01_eur25.json 23"
working_directory: "."
git_commit: "30e1c496891ffddbfad61461c4415f103138a403"
environment: ".venv + google-genai"
os: "Linux"
hardware: "CPU"
gpu: ""
cuda_notes: ""
api_provider: "google_gemini_batch"
api_model: "gemini-2.5-pro"
api_cost_estimate: "21.71 USD planned (0 USD spent; dry-run)"
dataset_assets:
  - "data/manifests/dprose_full.json"
  - "data/manifests/waves/wave_01_eur25.json"
  - "data/raw/dprose/ (327 CSVs)"
label_schema: "prediction-only BORDER/NOBORDER (no gold labels)"
prompt_version: "family B + json_schema_label_reason"
model_name: "gemini-2.5-pro"
varying_factor: "corpus orchestration (per-book batch jobs vs pilot monolith)"
fixed_conditions:
  - "Gemini Batch API file mode, one job per book"
  - "temperature=0, thinking_budget=-1, context_sentences=12, max_output_tokens=2048"
  - "Pilot trio seeded from 2026-06-20-dprose-batch-pilot-2048"
random_seed: ""
output_dir: "outputs/runs/dprose_batch/dprose-full-corpus"
artifacts_expected:
  - "corpus_progress.json"
  - "books/<slug>/predictions.jsonl"
  - "books/<slug>/book_review.txt"
  - "logs/dprose/wave_wave_01_eur25_2026-06-28.log"
artifacts_produced:
  - "outputs/runs/dprose_batch/dprose-full-corpus/corpus_progress.json"
  - "outputs/runs/dprose_batch/dprose-full-corpus/books/dprose_100/predictions.jsonl"
  - "outputs/runs/dprose_batch/dprose-full-corpus/books/dprose_806/predictions.jsonl"
  - "outputs/runs/dprose_batch/dprose-full-corpus/books/dprose_2158/predictions.jsonl"
  - "logs/dprose/wave_wave_01_eur25_2026-06-28.log"
main_metric_name: "planned_wave_cost_usd"
main_metric_value: 21.71
precision: ""
recall: ""
f1: ""
iou: ""
runtime: "instant (dry-run)"
failure_category: ""
related_experiment: "run_20260620_dprose_batch_pilot_2048"
related_issue: ""
decision_relevance: true
notion_targets:
  roadmap: "dProse full-corpus prompting"
  runs: true
  experiments: true
  artifacts: false
  issues: false
  decisions: false
---

## Objective

Implement and validate the budget-safe dProse full-corpus pipeline before Wave 1 API execution on ~€25 credit.

## Prep (local, no API)

```bash
.venv/bin/python scripts/data/prepare_dprose_prompting_inputs.py \
  --all --manifest_out data/manifests/dprose_full.json

.venv/bin/python scripts/data/plan_dprose_waves.py \
  --full_manifest data/manifests/dprose_full.json \
  --budget_eur 24.94 \
  --output data/manifests/waves/wave_01_eur25.json
```

Full manifest: **327 books, 120,369 sentences**.

## Dry-run outcome

| Item | Value |
|------|-------|
| Wave books | 15 (`dprose_51` … `dprose_151`) |
| Wave sentences | 4,880 |
| Planned cost | **$21.71** |
| Budget cap | $23.00 (session spend excl. pilot seed) |
| Pilot books seeded | 3 (989 sentences, no new API calls) |

## Execute Wave 1 (when ready)

```bash
set -a && source .env && set +a
bash scripts/sweeps/run_dprose_wave.sh data/manifests/waves/wave_01_eur25.json 23
```

Per-book review prints after each batch job completes. Re-run the same command to resume after interruption.

## Next step

Run Wave 1 live; after completion, generate Wave 2 with `--budget_eur 100 --exclude_completed`.
