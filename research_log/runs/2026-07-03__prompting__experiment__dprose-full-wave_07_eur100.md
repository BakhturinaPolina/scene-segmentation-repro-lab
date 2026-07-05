---
note_type: run
run_id: run_20260703_dprose_full_wave07
title: "dProse full corpus wave 07 (31 books, €100 budget cap — final wave)"
date: 2026-07-03
track: prompting
run_type: experiment
status: success
goal: "Complete remaining dProse corpus books after Wave 6; process final 31 books within €100 budget cap."
entrypoint: "src/runners/run_dprose_batch_corpus.py"
command: "bash scripts/sweeps/run_dprose_wave.sh data/manifests/waves/wave_07_eur100.json 556.25"
working_directory: "."
git_commit: "e9dede3"
environment: ".venv + google-genai"
os: "Linux"
hardware: "CPU"
gpu: ""
cuda_notes: ""
api_provider: "google_gemini_batch"
api_model: "gemini-2.5-pro"
api_cost_estimate: "52.70 USD planned (cumulative cap $556.25)"
dataset_assets:
  - "data/manifests/dprose_full.json"
  - "data/manifests/waves/wave_07_eur100.json"
label_schema: "prediction-only BORDER/NOBORDER (no gold labels)"
prompt_version: "family B + json_schema_label_reason"
model_name: "gemini-2.5-pro"
varying_factor: "wave budget (€100 wave 7 — final)"
fixed_conditions:
  - "Gemini Batch API file mode, one job per book"
  - "temperature=0, thinking_budget=-1, context_sentences=12, max_output_tokens=2048"
random_seed: ""
output_dir: "outputs/runs/dprose_batch/dprose-full-corpus"
artifacts_expected:
  - "corpus_progress.json"
  - "books/<slug>/predictions.jsonl"
  - "logs/dprose/wave_wave_07_eur100_2026-07-03.log"
artifacts_produced:
  - "corpus_progress.json (327/327 complete)"
  - "books/dprose_2317 … dprose_2505/predictions.jsonl"
  - "logs/dprose/wave_wave_07_eur100_2026-07-02.log"
main_metric_name: "parse_ok_rate"
main_metric_value: "99.81% parse OK (11,823/11,846 wave); corpus 327/327 complete"
precision: ""
recall: ""
f1: ""
iou: ""
runtime: ""
failure_category: ""
related_experiment: "run_20260702_dprose_full_wave06"
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

Run Wave 7 after Wave 6 completion (296/327 books). Manifest: `dprose_2317` … `dprose_2505` (31 books, ~11,846 sentences). **Final wave** — completes full corpus.

## Pre-flight

```bash
.venv/bin/python scripts/data/plan_dprose_waves.py \
  --budget_eur 100 \
  --exclude_completed outputs/runs/dprose_batch/dprose-full-corpus/corpus_progress.json \
  --output data/manifests/waves/wave_07_eur100.json

DRY_RUN=1 bash scripts/sweeps/run_dprose_wave.sh \
  data/manifests/waves/wave_07_eur100.json 556.25
```

Cumulative cap: $463.86 prior API spend + $92.39 wave headroom = **$556.25**.

## Execution

```bash
bash scripts/sweeps/run_dprose_wave.sh data/manifests/waves/wave_07_eur100.json 556.25
```

## Progress tracking

- Log: `logs/dprose/wave_wave_07_eur100_2026-07-03.log`
- Progress artifact: `outputs/runs/dprose_batch/dprose-full-corpus/corpus_progress.json`

## Outcome

**Success** — completed 2026-07-03 (~2.5h session). **Full corpus complete.**

| Metric | Value |
|--------|-------|
| Books processed | 31 / 31 |
| Corpus final | **327 / 327** books, **120,369 / 120,369** sentences |
| Wave parse OK | 11,823 / 11,846 (99.81%) — 23 keys across 13 books |
| Wave BORDER rate | 23.5% |
| Max consecutive BORDER | 10 (`dprose_2386`) |
| Wave spend | ~$49.95 ($513.81 − $463.86 prior) |
| Budget cap | $556.25 — **not hit** |
| Log | `logs/dprose/wave_wave_07_eur100_2026-07-02.log` |

All batch jobs succeeded (exit 0). Last book: `dprose_2505` — 278/279 parse (99.6%), 21.9% BORDER.

## Post-wave remediation

Corpus-wide parse-failure cleanup on 2026-07-04 cleared 90 of 130 remaining keys. See `docs/corpora/DPROSE_CORPUS_SPOT_CHECKS.md` § Parse failure remediation and run notes:

- `research_log/runs/2026-07-04__prompting__retry__dprose-corpus-failed.md` (batch retry)
- `research_log/runs/2026-07-04__prompting__retry__dprose-sync-failed.md` (sync retry)

Wave 7 books after remediation: **11 keys / 6 books** remain (`dprose_2320`, `dprose_2323`, `dprose_2325`, `dprose_2348`, `dprose_2443`, `dprose_2444`).
