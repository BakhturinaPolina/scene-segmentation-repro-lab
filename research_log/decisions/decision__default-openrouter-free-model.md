---
note_type: decision
decision_id: decision_default_openrouter_free_model
title: "Set Nemotron free as default OpenRouter baseline model"
date: 2026-05-14
decision_type: baseline
status: active
decision_statement: "The default OpenRouter free baseline model for STSS-Test-2 prompting runs is `nvidia/nemotron-3-super-120b-a12b:free`."
reasoning_summary: "The previous default `qwen/qwen3.6-plus:free` is deprecated and caused 404 errors. Nemotron already has successful stratified evidence and stable wrapper integration."
related_experiments:
  - "experiment__prompting__model__free-120b-comparison"
related_runs:
  - "run_20260514_phase4_prompting_baseline_live"
  - "run_20260514_phase4_prompting_stratified_live"
  - "run_20260514_phase4_phase_a_family_a_live"
related_artifacts: []
evidence_strength: "moderate"
follow_up_action: "Run STSS-Test-2 smoke checks with Nemotron defaults and keep a periodic availability snapshot for free-tier model routing."
notion_targets:
  decisions: true
  runs: true
  artifacts: true
  experiments: true
---

## Context

Prompting baseline defaults relied on `qwen/qwen3.6-plus:free`, which was deprecated by provider routing and returned API 404 during Phase 4 live smoke runs.

## Evidence

- `research_log/issues/issue__api__openrouter-free-model-deprecated.md` captured the failure pattern.
- `research_log/experiments/experiment__prompting__model__free-120b-comparison.md` recorded Nemotron as the strongest free-tier model in the prior controlled comparison.
- Phase 4 live runs already succeeded with explicit non-deprecated model overrides.

## Decision

Use `nvidia/nemotron-3-super-120b-a12b:free` as the default OpenRouter free baseline in active prompting wrappers and reproducibility docs.

## Why this is the current standard

It avoids the removed Qwen free route and aligns defaults with a model that already has successful run evidence in this repository.

## Consequences

- Prompting commands run without requiring manual model override away from deprecated slugs.
- Historical run notes remain unchanged as immutable evidence of prior conditions.
- Future routing changes can still affect free-tier reproducibility and require periodic checks.

## Follow-up

During reproducibility sync blocks, add/update a short free-model availability snapshot and rerun minimal API smoke checks.
