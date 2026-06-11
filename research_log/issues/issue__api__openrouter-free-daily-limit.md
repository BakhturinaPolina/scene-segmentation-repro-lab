---
note_type: issue
issue_id: issue_openrouter_free_daily_limit
title: "OpenRouter free-model daily rate limit blocks full_eval prompt sweep"
date_opened: 2026-06-08
category: API
severity: medium
status: open
first_seen_in_run: run_20260608_precision_full_sweep
environment: ".venv, OpenRouter nvidia/nemotron-3-super-120b-a12b:free"
track: prompting
probable_cause: "Daily quota exhausted: free-models-per-day-high-balance (2000/day, remaining=0)"
attempted_fixes:
  - "Automatic 429 backoff + 180s cooldown; process still blocked at daily cap"
blocking: true
related_runs:
  - run_20260608_precision_full_sweep
notion_targets:
  issues: true
  runs: true
  roadmap: false
---

## Symptom

Full prompt sweep (`FULL_EVAL=1`, families B/K/L/M) aborted after ~63 min. Family B
stalled at sentence 492/5025 on *Aus guter Familie* with repeated 429 errors:
`Rate limit exceeded: free-models-per-day-high-balance`.

## Context

Sweep started 2026-06-08 18:45 UTC with date tag `2026-06-08-precision-full`.
Background shell terminated while family L was starting; B and K were interrupted
mid-run.

## Evidence

- `logs/precision/family_B.log`: 492/5025 cached, then daily-limit 429s
- Cache: `outputs/runs/prompting/2026-06-08-precision-full/.../cache_Aus_guter_Familie.json` (492 entries)
- Family K output dir created but no meaningful cache before termination

## Attempted fixes

Runner's built-in rate-limit retries and 180s burst cooldown; insufficient once
daily quota is zero.

## Current best understanding

Cannot continue free Nemotron full_eval until the daily limit resets (header
`X-RateLimit-Reset` on 429 responses). At ~500 calls/day effective throughput,
completing one novel (~5k sentences) may take multiple days on the free tier.

## Next fix to try

1. Resume family B only when quota resets (cache auto-resumes):
   ```bash
   FULL_EVAL=1 DATE_TAG=2026-06-08-precision-full \
     .venv/bin/python src/runners/run_prompting_stratified.py \
       --prompt_family B --reasoning off --response_format json_object \
       --context_size 409 --temperature 0 --top_p 1.0 --seed 1337 --max_tokens 256 \
       --date 2026-06-08-precision-full
   ```
2. After B completes both novels, run K/L/M individually (not the full sweep loop
   until B is done).
3. Alternative: switch to a paid low-cost model for the sweep, or use pilot scope
   (`--max_per_class 15`) to screen variants within daily quota.
