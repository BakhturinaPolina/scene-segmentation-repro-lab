---
note_type: decision
decision_id: decision_pilot_vs_full_and_reasoning_off_candidate
title: "Pilot stratified is a screener only; reasoning=off is the leading candidate default for Nemotron Super + family B"
date: 2026-05-15
decision_type: experimental-default
status: provisional
decision_statement: "Pilot stratified results (max_per_class=15) are no longer treated as proxies for headline F1. Headline F1 reporting now requires --max_per_class 0 (full stratified). Within the §5.2 winning combo (nvidia/nemotron-3-super-120b-a12b:free + prompt family B with json_schema_label_reason.json), reasoning=off is the leading candidate for the new locked reasoning mode, pending a full-stratified confirmation run."
reasoning_summary: "Phase C produced (a) a 0.099 F1@0 gap between the pilot estimate (0.862) and the full-stratified rerun (0.763) for the same headline combo, refuting the assumption that pilot matches full F1; and (b) a pilot-scope finding that reasoning=off improves F1@0 from 0.862 to 0.874 with R=0.933 and ~half the latency, on identical controls."
related_experiments:
  - "experiment__prompting__model__free-120b-comparison"
related_runs:
  - "run_20260515_stss2_prompting_phase_a_family_sweep_nemotron"
  - "run_20260515_stss2_prompting_phase_b_2models_pinned"
  - "run_20260515_stss2_prompting_phase_c_baseline_and_factors"
  - "run_20260408_prompting_nemotron_stratified"
related_artifacts: []
evidence_strength: "moderate (single full-stratified run for the headline combo; reasoning=off finding only at pilot scope)"
follow_up_action: "Run one full-stratified confirmation of (Nemotron-Super, family B, reasoning=off) at --max_per_class 0 with all other controls locked. If F1@0 confirms ≥ the locked-low full-stratified baseline (0.763), update decision__default-openrouter-free-model with reasoning=off as the default reasoning mode for this combo."
notion_targets:
  decisions: true
  runs: true
  artifacts: false
  experiments: true
---

## Context

The §5.2 prompting campaign on STSS-Test-2 ran Phase A (10-family sweep at
pilot stratified scope), Phase B (top-3 families × free-model bucket), and
Phase C (full-stratified baseline + factor pilots E3/E4/E6) on the same
locked controls and the pinned model `nvidia/nemotron-3-super-120b-a12b:free`.
Family B (zero-shot JSON with `json_schema_label_reason.json`) was the
clear winner at every screening stage.

## Evidence

### Pilot vs full stratified — same combo, same locked controls

| Scope | Sentences | P@0 | R@0 | F1@0 | F1@1 | F1@3 |
|---|---|-----|-----|------|------|------|
| Pilot (`max_per_class=15`) | ~60 | 0.864 | 0.867 | 0.862 | 0.877 | 0.891 |
| Full (`max_per_class=0`) | 892 | 0.774 | 0.754 | **0.763** | 0.784 | 0.830 |

F1@0 dropped by 0.099 absolute. Every metric (precision, recall, all
tolerances) moved consistently. The pilot exaggerated headline quality
across the board — this contradicts the 2026-04-08 nemotron-stratified
observation (pilot F1 exactly matched full F1) and removes the prior
justification for using pilot numbers as headline reporting.

### Reasoning mode (E6 axis, pilot scope)

| reasoning | P@0 | R@0 | F1@0 | F1@1 | F1@3 | avg_lat (s) |
|---|-----|-----|------|------|------|-------------|
| low (locked) | 0.864 | 0.867 | 0.862 | 0.877 | 0.891 | 8.04 |
| off (E6 pilot) | 0.823 | 0.933 | **0.874** | 0.888 | 0.917 | **4.87** |

Pilot improvement of +0.012 F1@0 with substantially higher recall and ~40%
lower per-sentence latency. Latency matters because it changes a
full-stratified rerun from ~2h to ~1h, making the confirmation run cheap.

### Other Phase C factor evidence

E3 context_size=1024 was within pilot noise of the baseline; ctx=2048
hurt (F1@0=0.710). E4 temperature=0.3 and temperature=1.0 both degraded
F1@0 monotonically (0.833, 0.821). E5 was not run because the winning
family is zero-shot.

## Decision

1. **Headline reporting standard**: all future "headline F1" numbers for
   the §5.2 protocol must come from `--max_per_class 0` (full stratified)
   runs. Pilot (`max_per_class=15`) runs remain valid for screening and
   ranking but must be labelled as such.
2. **Provisional candidate default**: `reasoning=off` is the leading
   candidate replacement for `reasoning=low` in the locked controls when
   used with `nvidia/nemotron-3-super-120b-a12b:free` + family B. The
   active `decision__default-openrouter-free-model` is unchanged until a
   full-stratified confirmation is run; this decision is recorded as
   **provisional**.

## Why this is the current standard

The pilot/full gap discovered in Phase C invalidates the working
assumption that pilot numbers approximate headline numbers. Continuing to
treat them as interchangeable would let provisional decisions propagate on
unreliable evidence.

`reasoning=off` is provisional rather than active because: (a) the
evidence is pilot-scope only; (b) the full-stratified baseline confirmed
that pilot numbers can be 0.1 F1 too optimistic; (c) one quick
confirmation run (~1h) settles the question cleanly.

## Consequences

- Run notes and aggregate dashboards should call out the eval scope
  explicitly (pilot vs full) wherever F1 is reported.
- Pre-existing decision notes referencing pilot F1 as a "validated"
  proxy (`decision__default-openrouter-free-model` follow-up section) need
  a soft amendment noting the new evidence.
- The active locked controls for any active sweep stay at `reasoning=low`
  until the confirmation run validates `reasoning=off`.

## Follow-up

Single full-stratified run command for the confirmation (the proven script
already supports it):

```bash
OPENROUTER_API_KEY=... .venv-gpu/bin/python src/run_prompting_stratified.py \
  --model nvidia/nemotron-3-super-120b-a12b:free \
  --prompt_family B \
  --max_per_class 0 \
  --reasoning off \
  --temperature 0 --top_p 1.0 --seed 1337 --max_tokens 256 \
  --response_format json_schema --schema_file src/prompts/json_schema_label_reason.json \
  --date 2026-05-16-phaseC-E6-roff-full
```

If F1@0 ≥ 0.763 (the locked-low full-stratified baseline), promote
`reasoning=off` to active default and amend the model-default decision.
Otherwise close this provisional decision as not-supported.
