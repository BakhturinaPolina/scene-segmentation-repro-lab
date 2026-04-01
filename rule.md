# rule.md — Scene Segmentation Research Logging Rules (Strict YAML Version)

## Purpose

This repository must stay syncable with the Notion research hub.

Notion is the project memory.
Cursor is the active workbench.

Every meaningful action in Cursor must produce a structured markdown note with YAML frontmatter so it can be synced into Notion later without reconstruction from memory.

If a run, issue, artifact, or decision is not recorded in a structured note, it does not count as part of the research record.

---

## Required note types

The project uses these local note types:

- `run`
- `experiment`
- `artifact`
- `issue`
- `decision`
- `sync_note`

Each note must:
- live in the correct folder
- use the correct YAML schema
- have a stable file name
- be written immediately after the action, not later from memory

---

## Required folder structure

Use this structure:

- `research_log/runs/`
- `research_log/experiments/`
- `research_log/artifacts/`
- `research_log/issues/`
- `research_log/decisions/`
- `research_log/sync_notes/`

Optional:
- `research_log/templates/`

---

## Global rules

1. Use English only.
2. Use explicit file paths, commands, and names.
3. Do not use vague summaries like "tested some things".
4. Every important output must be linked to a run.
5. Every failed run with diagnostic value must still be logged.
6. Every important conclusion must become a decision note.
7. Controlled experiments must vary one factor at a time unless explicitly marked otherwise.
8. If a baseline changes, create a decision note explaining why.
9. Every note must be sync-ready for Notion.

---

## Naming rules

### Run note file name
`YYYY-MM-DD__track__run-type__short-name.md`

Examples:
- `2026-04-01__ssc__baseline__default-encoder.md`
- `2026-04-01__prompting__experiment__gpt4o-json-v2.md`
- `2026-04-01__llama__dry-run__unsloth-import-test.md`

### Experiment note file name
`experiment__track__factor__short-name.md`

### Artifact note file name
`artifact__run-short-name__artifact-type.md`

### Issue note file name
`issue__category__short-name.md`

### Decision note file name
`decision__short-name.md`

### Sync note file name
`sync__YYYY-MM-DD__short-name.md`

---

## Required YAML schema: run note

Every execution attempt that matters must create a run note.

Use this exact structure:

```yaml
---
note_type: run
run_id: run_YYYYMMDD_slug
title: "Short human-readable run title"
date: YYYY-MM-DD
track: ssc
run_type: baseline
status: success
goal: "What this run was trying to do"
entrypoint: "ssc/main.py"
command: "python -m ssc.main ..."
working_directory: "."
git_commit: "commit-hash-or-unknown"
environment: "scene-seg-basic"
os: "Linux"
hardware: "RTX 2070 / CPU / unknown"
gpu: "RTX 2070"
cuda_notes: ""
api_provider: ""
api_model: ""
api_cost_estimate: ""
dataset_assets:
  - "dev_split_v1"
label_schema: "binary_boundary_v1"
prompt_version: ""
model_name: "baseline-encoder-name"
varying_factor: "none"
fixed_conditions:
  - "dataset split fixed"
  - "evaluation unchanged"
random_seed: 42
output_dir: "outputs/ssc/2026-04-01/run_name/"
artifacts_expected:
  - "stdout.log"
  - "metrics.json"
artifacts_produced:
  - "outputs/.../stdout.log"
  - "outputs/.../metrics.json"
main_metric_name: "F1"
main_metric_value: 0.00
precision: 0.00
recall: 0.00
f1: 0.00
iou: ""
runtime: ""
failure_category: ""
related_experiment: ""
related_issue: ""
decision_relevance: false
notion_targets:
  roadmap: ""
  runs: true
  experiments: ""
  artifacts: true
  issues: false
  decisions: false
---
```

### Required run note body

After the YAML, include these sections:

```md
## Objective

## What was held constant

## What changed

## Outcome

## Interpretation

## Next step
```

---

## Required YAML schema: experiment note

Create an experiment note whenever you define a real comparison.

```yaml
---
note_type: experiment
experiment_id: exp_slug
title: "Experiment title"
date_opened: YYYY-MM-DD
track: prompting
status: active
factor_under_test: "LLM model"
baseline_run_id: "run_YYYYMMDD_slug"
hypothesis: "Instruction-following models may segment scenes better than the baseline model."
fixed_conditions:
  - "same dataset split"
  - "same prompt schema"
  - "same evaluation"
variants:
  - "model_a"
  - "model_b"
success_metric: "F1"
comparison_rule: "Highest F1 with acceptable cost"
related_runs: []
related_artifacts: []
notion_targets:
  experiments: true
  runs: true
  artifacts: true
  decisions: false
---
```

### Required experiment note body

```md
## Research question

## Baseline

## Constants

## Variants

## Evaluation rule

## Interim conclusion

## Final conclusion
```

---

## Required YAML schema: artifact note

Create an artifact note for every meaningful output.

```yaml
---
note_type: artifact
artifact_id: art_slug
title: "Artifact title"
date: YYYY-MM-DD
artifact_type: plot
produced_by_run: "run_YYYYMMDD_slug"
track: ssc
path: "outputs/.../plot.png"
url: ""
description: "What this artifact contains"
report_worthy: true
figure_or_table_candidate: "Figure"
related_experiment: ""
related_task: ""
notion_targets:
  artifacts: true
  runs: true
  decisions: false
---
```

### Required artifact note body

```md
## What this artifact is

## What it shows

## Why it matters

## Reuse notes
```

---

## Required YAML schema: issue note

Create an issue note for every blocking or informative failure.

```yaml
---
note_type: issue
issue_id: issue_slug
title: "Short issue title"
date_opened: YYYY-MM-DD
category: cuda
severity: high
status: open
first_seen_in_run: "run_YYYYMMDD_slug"
environment: "scene-seg-full"
track: llama
probable_cause: "Short probable cause"
attempted_fixes:
  - "fix attempt 1"
  - "fix attempt 2"
blocking: true
related_runs:
  - "run_YYYYMMDD_slug"
notion_targets:
  issues: true
  runs: true
  roadmap: true
---
```

### Required issue note body

```md
## Symptom

## Context

## Evidence

## Attempted fixes

## Current best understanding

## Next fix to try
```

---

## Required YAML schema: decision note

Create a decision note whenever you standardize something or reject an important option.

```yaml
---
note_type: decision
decision_id: decision_slug
title: "Decision title"
date: YYYY-MM-DD
decision_type: baseline
status: active
decision_statement: "What was decided"
reasoning_summary: "Short explanation"
related_experiments: []
related_runs: []
related_artifacts: []
evidence_strength: "moderate"
follow_up_action: "What to do next"
notion_targets:
  decisions: true
  runs: true
  artifacts: true
  experiments: true
---
```

### Required decision note body

```md
## Context

## Evidence

## Decision

## Why this is the current standard

## Consequences

## Follow-up
```

---

## Required YAML schema: sync note

At the end of every meaningful work block, create a sync note.

```yaml
---
note_type: sync_note
sync_id: sync_YYYYMMDD_slug
date: YYYY-MM-DD
title: "Short sync title"
track: cross-project
work_block_type: research
runs_created:
  - ""
artifacts_created:
  - ""
issues_created:
  - ""
decisions_created:
  - ""
experiments_updated:
  - ""
roadmap_updates:
  - ""
notion_sync_priority: high
---
```

### Required sync note body

```md
## What was done

## Main result

## What needs syncing to Notion

## What remains unresolved

## Next step
```

---

## When a run note is mandatory

You must create a run note whenever you:

* test imports
* start a script
* perform a smoke test
* run a baseline
* run evaluation
* run prompting/API inference
* run llama/fine-tuning code
* rerun after a fix
* generate comparable metrics
* produce a failure with diagnostic value

Do not skip run notes because the run "did not work".
Failure is still evidence.

---

## When an experiment note is mandatory

You must create or update an experiment note whenever:

* a comparison has a named hypothesis
* a baseline is defined
* one factor is being varied systematically
* results will be compared across runs

Do not treat random exploratory changes as an experiment unless you define:

* factor under test
* fixed conditions
* success metric

---

## Required local deliverables for every run

Each run folder should contain, whenever possible:

* `command.txt`
* `config.json` or `config.yaml`
* `stdout.log`
* `stderr.log`
* `metrics.json`
* `run_summary.md`

Optional:

* `predictions.*`
* `plots/`
* `samples/`
* `checkpoint/`

If a file is missing, state why in the run note.

---

## Baseline rule

There must be one clearly identified baseline per main track:

* one `ssc` baseline
* one `prompting` baseline
* one `llama` baseline

If a baseline changes:

1. create a decision note
2. update the relevant experiment note
3. mark the old baseline as superseded, not erased

---

## One-factor-at-a-time rule

For controlled experiments:

* vary one factor only
* state the factor explicitly in YAML
* list fixed conditions explicitly in YAML

Examples of valid factors:

* encoder checkpoint
* LLM model
* prompt schema
* label schema
* context window
* evaluation tolerance

Bad logging:

* "tested model and prompt changes"

Good logging:

* `factor_under_test: "LLM model"`
* `fixed_conditions: same prompt, same dataset, same evaluation`

---

## Reproducibility rule

Any result worth keeping must be reproducible from the run note.

A run note is incomplete if it lacks any of:

* command
* environment
* dataset
* output directory
* status
* summary of outcome

A strong run note should also include:

* git commit
* seed
* hardware
* metric values

---

## Mapping to Notion

Use these local note types to sync into Notion:

* `run` -> Runs database
* `experiment` -> Experiments database
* `artifact` -> Artifacts database
* `issue` -> Issues database
* `decision` -> Decisions database
* `sync_note` -> Roadmap updates + daily summary + sync staging

This matches the relational structure already used in the Notion hub, where database entries can be linked across runs, tasks, experiments, and artifacts.

---

## Minimal execution checklist

Before running:

* define track
* define goal
* define whether this is baseline or experiment
* define output folder
* define factor under test
* confirm environment

After running:

* save logs
* save config and command
* create run note
* create artifact note(s)
* create issue note if needed
* create decision note if the run changes project standards
* create sync note

---

## Default attitude

Be explicit.
Be conservative.
Be traceable.

Prefer:

* exact commands
* short factual summaries
* stable names
* one-factor-at-a-time comparisons
* evidence-linked decisions

Avoid:

* undocumented reruns
* vague "misc" outputs
* silent baseline changes
* conclusions without evidence
