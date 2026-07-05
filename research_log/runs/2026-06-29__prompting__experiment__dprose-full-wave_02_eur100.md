---
note_type: run
run_id: run_20260629_dprose_full_wave02
title: "dProse full corpus wave 02 (55 books, €100 budget cap)"
date: 2026-06-29
track: prompting
run_type: experiment
status: partial
goal: "Continue resumable full-corpus dProse prompting after Wave 1; process next ~55 books within €100 budget cap with incremental artifacts and rich logs."
entrypoint: "src/runners/run_dprose_batch_corpus.py"
command: "bash scripts/sweeps/run_dprose_wave.sh data/manifests/waves/wave_02_eur100.json 113.78"
working_directory: "."
git_commit: "c6e83ab5b17d485d3b3ac87c436e98edff53ba32"
environment: ".venv + google-genai"
os: "Linux"
hardware: "CPU"
gpu: ""
cuda_notes: ""
api_provider: "google_gemini_batch"
api_model: "gemini-2.5-pro"
api_cost_estimate: "91.89 USD planned (effective cap $92.39)"
dataset_assets:
  - "data/manifests/dprose_full.json"
  - "data/manifests/waves/wave_02_eur100.json"
  - "data/raw/dprose/ (327 CSVs)"
label_schema: "prediction-only BORDER/NOBORDER (no gold labels)"
prompt_version: "family B + json_schema_label_reason"
model_name: "gemini-2.5-pro"
varying_factor: "wave budget (€100 vs Wave 1 €25)"
fixed_conditions:
  - "Gemini Batch API file mode, one job per book"
  - "temperature=0, thinking_budget=-1, context_sentences=12, max_output_tokens=2048"
  - "Resume from corpus_progress.json + on-disk predictions + in-flight job_meta"
random_seed: ""
output_dir: "outputs/runs/dprose_batch/dprose-full-corpus"
artifacts_expected:
  - "corpus_progress.json"
  - "books/<slug>/predictions.jsonl"
  - "books/<slug>/book_review.txt"
  - "logs/dprose/wave_wave_02_eur100_2026-06-29.log"
artifacts_produced: []
main_metric_name: "parse_ok_rate"
main_metric_value: ""
precision: ""
recall: ""
f1: ""
iou: ""
runtime: ""
failure_category: ""
related_experiment: "run_20260628_dprose_full_wave01"
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

Run Wave 2 of the dProse full-corpus batch pipeline (~55 books, ~20,654 sentences) after Wave 1 completed 18/327 books.

## What was held constant

Same validated pilot config (Gemini 2.5 Pro batch, Family B, 2048 max output tokens, thinking_budget=-1, context_sentences=12).

## What changed

- New wave manifest: `wave_02_eur100.json` (55 books from `dprose_161` onward, numeric ID order).
- Budget cap raised to **$113.78 cumulative** ($21.39 Wave 1 + $92.39 Wave 2 effective USD).
- Orchestrator: resume from on-disk `predictions.jsonl` if complete; atomic JSONL write for predictions; richer session/progress logging.

## Pre-flight

```bash
.venv/bin/python scripts/data/plan_dprose_waves.py \
  --full_manifest data/manifests/dprose_full.json \
  --budget_eur 100 \
  --output data/manifests/waves/wave_02_eur100.json

DRY_RUN=1 bash scripts/sweeps/run_dprose_wave.sh \
  data/manifests/waves/wave_02_eur100.json 113.78
```

## Execution

```bash
bash scripts/sweeps/run_dprose_wave.sh data/manifests/waves/wave_02_eur100.json 113.78
```

**Monitor:** `tail -f logs/dprose/wave_wave_02_eur100_2026-06-29.log`  
**Progress:** `outputs/runs/dprose_batch/dprose-full-corpus/corpus_progress.json`

## Resume points

| Failure mode | Recovery |
|--------------|----------|
| Ctrl+C mid-poll | Re-run same command; resumes via `job_meta.json` |
| Crash after predictions, before progress | Re-run; skips API if `predictions.jsonl` complete |
| Parse OK < 95% | Book marked `blocked`; investigate, then `--retry_failed` |
| Budget cap hit | Top up, generate Wave 3 or raise cap |

## Outcome

*(Update when wave completes or pauses.)*

## Next step

Spot-check outliers per `docs/corpora/DPROSE_CORPUS_SPOT_CHECKS.md`; plan Wave 3 with `--budget_eur 100 --exclude_completed`.
