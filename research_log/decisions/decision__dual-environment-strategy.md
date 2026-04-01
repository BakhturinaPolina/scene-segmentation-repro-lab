---
note_type: decision
decision_id: decision_dual_environment_strategy
title: "Use separate CPU and GPU virtual environments"
date: 2026-03-31
decision_type: architecture
status: active
decision_statement: "Maintain two virtual environments: .venv (CPU, pinned for smoke tests) and .venv-gpu (GPU, Unsloth stack)"
reasoning_summary: "SSC smoke tests require transformers==4.46.3; Unsloth requires transformers>=4.51.3. These are incompatible in a single environment."
related_experiments: []
related_runs:
  - "run_20260331_cpu_pinned_final"
  - "run_20260331_gpu_env_validation"
related_artifacts: []
evidence_strength: "strong"
follow_up_action: "Document environment activation in all future run notes"
notion_targets:
  decisions: true
  runs: true
  artifacts: false
  experiments: false
---

## Context

Early smoke testing revealed that the upstream `ssc` code requires `transformers==4.46.3` to avoid a dataclass field-ordering error in `SSCModelConfig`. Meanwhile, the Unsloth fine-tuning stack requires `transformers>=4.51.3` and pulls `torch 2.10.0+cu128`. These version requirements are mutually exclusive.

## Evidence

- `run_20260331_cpu_pinned_final`: ssc.model imports pass only with transformers==4.46.3
- `run_20260331_gpu_env_validation`: Unsloth installs transformers==4.52.4 and requires CUDA-enabled torch
- Attempting to satisfy both in one environment leads to either SSC import failure or Unsloth import failure

## Decision

Maintain two environments:

| Environment | Path | Purpose | torch | transformers |
|-------------|------|---------|-------|--------------|
| `.venv` | project root | CPU smoke tests, SSC/prompting validation | 2.5.1+cpu | 4.46.3 |
| `.venv-gpu` | project root | GPU training, Unsloth fine-tuning | 2.10.0+cu128 | 4.52.4 |

## Why this is the current standard

No single set of dependency versions can satisfy both the upstream SSC code pattern and the Unsloth training requirements. Dual environments are the minimal solution that avoids modifying upstream code.

## Consequences

- Every run note must specify which environment was used
- `requirements-basic.txt` governs `.venv`; Unsloth's resolver governs `.venv-gpu`
- Future dependency changes must be tested in the correct environment

## Follow-up

If the upstream SSC code is refactored to work with transformers 5.x, the two environments may be merged.
