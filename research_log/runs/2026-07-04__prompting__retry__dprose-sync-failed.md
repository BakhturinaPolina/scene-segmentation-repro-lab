---
note_type: run
run_id: run_20260704_dprose_sync_retry_failed
title: "dProse full corpus — sync API retry on 58 parse-fail keys"
date: 2026-07-04
track: prompting
run_type: experiment
status: partial
goal: "Re-run remaining 58 parse-failed keys via Gemini sync API (non-batch) with thinking_budget=1024 and max_output_tokens=8192."
entrypoint: "src/runners/run_dprose_sync_retry.py"
command: "bash scripts/sweeps/retry_dprose_sync_failed.sh"
working_directory: "."
git_commit: ""
environment: ".venv + google-genai"
os: "Linux"
hardware: "CPU"
gpu: ""
cuda_notes: ""
api_provider: "google_gemini_sync"
api_model: "gemini-2.5-pro"
api_cost_estimate: "~$0.30 USD (58 keys, sync pricing)"
dataset_assets:
  - "data/manifests/dprose_sync_retry_keys.json"
  - "data/manifests/dprose_full.json"
label_schema: "prediction-only BORDER/NOBORDER (no gold labels)"
prompt_version: "family B + json_schema_label_reason"
model_name: "gemini-2.5-pro"
varying_factor: "sync API + thinking_budget=1024 + safety BLOCK_NONE + max_output_tokens=8192"
fixed_conditions:
  - "temperature=0, context_sentences=12, 1s sleep, 3x retry on 503"
random_seed: ""
output_dir: "outputs/runs/dprose_batch/dprose-full-corpus"
artifacts_expected:
  - "books/<slug>/predictions.jsonl (merged)"
  - "books/<slug>/book_review.json"
  - "logs/dprose/sync_retry_failed_2026-07-04.log"
artifacts_produced:
  - "data/manifests/dprose_sync_retry_keys.json"
  - "books/<slug>/predictions.jsonl (merged, 18 keys cleared)"
  - "logs/dprose/sync_retry_failed_2026-07-04.log"
main_metric_name: "parse_ok_rate"
main_metric_value: "18/58 recovered; 40 keys remain (36 PROHIBITED_CONTENT blocks)"
runtime: "~6m 19s"
failure_category: ""
related_experiment: "run_20260704_dprose_corpus_retry_failed"
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

Targeted sync re-run after batch `--retry_failed` left **58 keys** (mostly API null responses). Sync mode avoids batch dropouts; `thinking_budget=0` prevents thinking-token overflow.

## Pre-flight

```bash
DRY_RUN=1 bash scripts/sweeps/retry_dprose_sync_failed.sh
```

## Execution

```bash
bash scripts/sweeps/retry_dprose_sync_failed.sh
```

## Progress tracking

- Log: `logs/dprose/sync_retry_failed_2026-07-04.log`
- Keys manifest: `data/manifests/dprose_sync_retry_keys.json`

## Outcome

**Partial** — finished 2026-07-05T00:01:53Z.

| Metric | Before sync | After sync |
|--------|-------------|------------|
| Failed keys | 58 | **40** |
| Books with failures | 24 | **16** |
| Recovered this run | — | **18** |
| Blocked (PROHIBITED_CONTENT) | — | **36** |

Note: `thinking_budget=0` is invalid for Gemini 2.5 Pro (requires thinking mode); used **1024** with relaxed safety settings.

Remaining 40 keys are mostly sync API content blocks on literary context — neighbor-consensus patch is the next step (`scripts/evaluation/patch_failed_predictions.py`; suggestions in `patch_suggestions.json`).

## Follow-up

Patch suggestions exported 2026-07-04: 40 keys. **Applied** same day — 37 medium+ then 3 low (second pass) → **100% parse OK**, 40 `manual_fix` rows.
