# Source code layout

Python modules for data prep, workflow runners, review tools, and prompt templates.

```
src/
├── core/               # shared runtime (paths, prompting helpers)
│   ├── workflow_runtime.py
│   └── prompt_runtime.py
├── data/               # manifests, conversion, verification
├── runners/            # baselines, stratified eval, reproduction orchestrator
├── review/             # Markdown review renderer, error tagger
└── prompts/            # prompt families A–J + JSON schemas
```

## Entrypoints

| Track | Script |
|-------|--------|
| Prompting baseline | `python src/runners/run_prompting_baseline.py` |
| Stratified / full eval | `python src/runners/run_prompting_stratified.py` |
| Phase A sweep driver | `python src/runners/run_prompting_phase_a.py` |
| SSC baseline | `python src/runners/run_ssc_baseline.py` |
| LLaMA baseline | `python src/runners/run_llama_baseline.py` |
| STSS-Test-2 reproduction | `python src/runners/reproduce_stss_test_2.py` |
| Verify data manifest | `python src/data/verify_data_manifest.py` |
| Render human review MD | `python src/review/render_review.py` |

Output paths are defined in `src/core/workflow_runtime.py` (see `outputs/README.md`).
