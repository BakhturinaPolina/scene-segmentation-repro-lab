# Scripts index

Helper scripts grouped by purpose. Run from the repository root unless noted.

```
scripts/
├── data/           # prepare inputs and manifests
├── evaluation/     # scoring, what-if analysis, review tables
├── export/         # export annotated workbooks
└── sweeps/         # Phase A/B/C shell sweep drivers
```

## Common commands

| Task | Command |
|------|---------|
| Prepare Excel prompting inputs | `python scripts/data/prepare_excel_prompting_inputs.py` |
| Score vs Excel gold | `python scripts/evaluation/score_prompting_vs_excel_gold.py …` |
| Post-processing what-if | `python scripts/evaluation/normalization_what_if.py …` |
| Phase A family sweep | `bash scripts/sweeps/phase_a_sweep.sh` |

Prompt templates and runners live under `src/` (see `src/README.md`).
