---
note_type: issue
issue_id: issue_api_openrouter_free_inventory_phase_b_constraint
title: "OpenRouter free inventory infeasible for §5.2 Phase B model bucket at locked controls"
date: 2026-05-15
category: api
severity: medium
related_runs:
  - "run_20260515_stss2_prompting_phase_b_2models_pinned"
related_decisions:
  - "decision_default_openrouter_free_model"
status: open
notion_targets:
  issues: true
---

## Symptom

When running §5.2 Phase B (kept families × 3–5 pinned free models, locked controls
`temperature=0`, `top_p=1.0`, `seed=1337`, `max_tokens=256`, `reasoning=low`,
`response_format=json_schema`) on STSS-Test-2, only 2 of 10 currently-listed
OpenRouter free models complete a 60-sample stratified pilot in under 30 minutes:

| Model | Outcome at locked controls | Provider |
|---|---|---|
| `nvidia/nemotron-3-super-120b-a12b:free` | works (~10 min/family) | Nvidia |
| `openai/gpt-oss-120b:free` | works (~25 min/family) | OpenAI |
| `meta-llama/llama-3.3-70b-instruct:free` | sustained HTTP 429 | Venice |
| `qwen/qwen3-next-80b-a3b-instruct:free` | sustained HTTP 429 | Venice |
| `nousresearch/hermes-3-llama-3.1-405b:free` | sustained HTTP 429 | Venice |
| `meta-llama/llama-3.2-3b-instruct:free` | sustained HTTP 429 | Venice |
| `nvidia/nemotron-nano-9b-v2:free` | reasoning saturates 256 token budget; ~10 retries/sentence; ~100s/sentence | Nvidia |
| `z-ai/glm-4.5-air:free` | reasoning saturates 256 token budget; >200s/sentence | Z.AI |
| `google/gemma-4-31b-it:free` | sustained HTTP 429 | Google AI Studio |
| `arcee-ai/trinity-large-thinking:free` | thinking model; expected to saturate tokens (not run) | Arcee |

## Failure mode A — Venice provider 429

Models routed via the Venice provider (Llama 3.x-instruct, Qwen3-Next-80B-instruct,
Hermes-3-405B) return `HTTP 429 — temporarily rate-limited upstream` on the very
first chat completion request, with `Retry-After` of 2–30 s. Repeating the call
after the suggested wait reproduces the 429 immediately. Smoke calls were tried
on 2026-05-15 between ~22:30 and ~02:15 with no successful response.

## Failure mode B — reasoning content saturating max_tokens

Reasoning-capable models (Nemotron-nano-9b-v2, GLM-4.5-Air, and presumably
Trinity-large-thinking) respect `reasoning.effort=low` but still emit
`completion_tokens_details.reasoning_tokens` that consume the full
`max_tokens=256` budget, leaving `message.content` as `null` or `""`. The
runner's `parse_family_output` then marks parse failure and the runner retries
up to 15 times; some retries eventually succeed with non-empty content, but
mean per-sentence latency is 100–220 s instead of the ~7–10 s observed for
non-reasoning models.

## Failure mode C — Google AI Studio rate limit

Free `google/gemma-4-*-it` models smoke-call return HTTP 200, but a sustained
sweep with the runner's 5 s polling interval triggers HTTP 429 from the Google
AI Studio free tier on every subsequent call.

## Impact

§5.2 specifies 3–5 pinned free models in Phase B and a model-bucket spec that
includes "one free reasoning-capable model". With the current free inventory and
the campaign's locked controls, that requirement cannot be satisfied without one
of: (a) bumping `max_tokens` above ~512 specifically for reasoning models —
which violates one-factor-at-a-time within the phase; (b) attaching an
"openrouter/integrations" key for Venice provider routing; (c) waiting hours
for upstream rate limits to drain.

## Workaround for this campaign

Phase B proceeded with 2 pinned free models (Nemotron Super 120B,
gpt-oss-120b). Below the §5.2 spec but the only practically-comparable subset
at the locked controls. Documented inline in
`research_log/runs/2026-05-15__prompting__experiment__stss2-phase-b-2models-pinned.md`.

## Possible remediations (deferred)

- Phase D-style follow-up: rerun reasoning models with `max_tokens=1024` and
  treat `max_tokens` as a controlled factor (E factor not in current §5.2
  follow-up axes; would need a new axis E7).
- Add a small wrapper that detects empty `message.content` and immediately
  retries without exponential backoff, instead of treating it as a parse
  failure with the retry budget burned on backoff.
- Periodically re-snapshot free inventory and look for non-Venice providers
  for the Llama and Qwen lineages.
