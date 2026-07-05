---
note_type: run
run_id: run_20260704_dprose_corpus_retry_failed
title: "dProse full corpus — retry_failed on 130 parse-fail keys"
date: 2026-07-04
track: prompting
run_type: experiment
status: success
goal: "Retry all remaining parse-failed sentence keys across the completed dProse corpus to maximize parse OK rate before merge/post-processing."
entrypoint: "src/runners/run_dprose_batch_corpus.py"
command: "bash scripts/sweeps/retry_dprose_corpus_failed.sh"
working_directory: "."
git_commit: "e9dede3"
environment: ".venv + google-genai"
os: "Linux"
hardware: "CPU"
gpu: ""
cuda_notes: ""
api_provider: "google_gemini_batch"
api_model: "gemini-2.5-pro"
api_cost_estimate: "~$0.52 USD (130 keys × ~$0.004/sentence)"
dataset_assets:
  - "data/manifests/dprose_full.json"
label_schema: "prediction-only BORDER/NOBORDER (no gold labels)"
prompt_version: "family B + json_schema_label_reason"
model_name: "gemini-2.5-pro"
varying_factor: "retry_failed pass (max_output_tokens=4096 vs 2048 baseline)"
fixed_conditions:
  - "Gemini Batch API file mode, one mini-batch per book with failed keys only"
  - "temperature=0, thinking_budget=-1, context_sentences=12"
random_seed: ""
output_dir: "outputs/runs/dprose_batch/dprose-full-corpus"
artifacts_expected:
  - "books/<slug>/predictions.jsonl (merged)"
  - "books/<slug>/book_review.json"
  - "logs/dprose/retry_failed_2026-07-04.log"
artifacts_produced:
  - "books/<slug>/predictions.jsonl (merged, 72 keys cleared)"
  - "books/<slug>/book_review.json"
  - "logs/dprose/retry_failed_2026-07-04.log"
main_metric_name: "parse_ok_rate"
main_metric_value: "99.95% parse OK (120,311/120,369); 58 keys remain after pass"
runtime: "~2h 52m (03:00–05:52 UTC)"
failure_category: ""
related_experiment: "run_20260703_dprose_full_wave07"
related_issue: ""
decision_relevance: false
notion_targets:
  roadmap: "dProse full-corpus prompting"
  runs: true
  experiments: false
  artifacts: true
  issues: false
  decisions: false
---

## Objective

Corpus-wide `--retry_failed` after full corpus completion (327/327 books). Target: **75 books**, **130 sentence-keys** with initial parse failures (prose/thinking instead of JSON).

## Pre-flight

```bash
DRY_RUN=1 bash scripts/sweeps/retry_dprose_corpus_failed.sh
```

Uses `max_output_tokens=4096` (up from 2048) per prior retry passes.

## Execution

```bash
bash scripts/sweeps/retry_dprose_corpus_failed.sh
```

**Live run (2026-07-04):** PID `852548` — `.venv/bin/python` with 75 books, `--retry_failed --resume --max_output_tokens 4096`. Dry-run est: **$0.58** (130 keys). Monitor appends to log every 2 min.

## Progress tracking

- Log: `logs/dprose/retry_failed_2026-07-04.log`
- Monitor: `bash scripts/sweeps/monitor_dprose_retry.sh logs/dprose/retry_failed_2026-07-04.log 852548 120`
- Re-check: `book_review.json` failed_keys count per book

### Snapshot (launch)

| Metric | Value |
|--------|-------|
| Books with failures | 75 |
| Failed keys | 130 |
| In-flight (03:04 UTC) | `dprose_293` (1 key), `dprose_435` (6 keys) |

## Outcome

**Success** — retry finished 2026-07-04T05:51:54Z (PID 852548 exit 0).

| Metric | Before | After |
|--------|--------|-------|
| Failed keys | 130 | **58** |
| Books with failures | 75 | **24** |
| Keys cleared | — | **72** (55%) |
| Parse OK rate | 99.89% | **99.95%** (120,311/120,369) |

Worst remaining: `dprose_2234` (7), `dprose_2443` (6), `dprose_435`/`dprose_555` (6 each). All 327 books still pass ≥95% gate.

## Follow-up

Sync retry pass (`run_20260704_dprose_sync_retry_failed`) cleared 18 more keys → **40** remain. Neighbor-consensus patch exported in `patch_suggestions.json`; **applied** 2026-07-04 (40 keys total → 100% parse OK).
