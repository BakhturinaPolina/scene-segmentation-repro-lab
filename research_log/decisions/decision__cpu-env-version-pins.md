---
note_type: decision
decision_id: decision_cpu_env_version_pins
title: "Pin torch, torchvision, transformers, langchain for CPU environment"
date: 2026-03-31
decision_type: baseline
status: active
decision_statement: "Pin torch==2.5.1+cpu, torchvision==0.20.1+cpu, transformers==4.46.3, langchain==0.1.9 in requirements-basic.txt"
reasoning_summary: "These specific versions are the minimum set that resolves all three import-time compatibility issues discovered during smoke testing"
related_experiments: []
related_runs:
  - "run_20260331_initial_import_tests"
  - "run_20260331_post_dep_install_imports"
  - "run_20260331_strict_upstream_install"
  - "run_20260331_cpu_pinned_final"
related_artifacts:
  - "art_cpu_pinned_requirements"
evidence_strength: "strong"
follow_up_action: "Do not change these pins unless a new compatibility issue or upstream refactor requires it"
notion_targets:
  decisions: true
  runs: true
  artifacts: true
  experiments: false
---

## Context

Four sequential smoke test runs explored different dependency configurations. Each run revealed or resolved specific compatibility issues.

## Evidence

| Run | Config | Result |
|-----|--------|--------|
| initial_import_tests | no peft/langchain/wuenlp | all fail (missing packages) |
| post_dep_install | peft+langchain+wuenlp, transformers unpinned | fail (dataclass TypeError, langchain.adapters) |
| strict_upstream_install | full upstream reqs, no torch pin | fail (torchvision::nms, langchain.adapters) |
| cpu_pinned_final | explicit pins | ssc.model PASS, prompting.classify PASS |

The pinned versions are the only configuration tested that produces passing imports for both SSC model and prompting modules.

## Decision

Lock the following in `requirements-basic.txt`:

```
torch==2.5.1+cpu
torchvision==0.20.1+cpu
transformers==4.46.3
langchain==0.1.9
```

## Why this is the current standard

Each pin resolves exactly one issue:
- `torch==2.5.1+cpu` + `torchvision==0.20.1+cpu` → resolves `torchvision::nms` mismatch
- `transformers==4.46.3` → resolves `SSCModelConfig` dataclass error
- `langchain==0.1.9` → resolves `langchain.adapters` missing

## Consequences

- The CPU environment cannot use newer transformers features
- The CPU environment cannot use newer langchain features
- Any upgrade requires re-running the full smoke test suite

## Follow-up

Re-evaluate pins if upstream code is modified to support newer dependency versions.
