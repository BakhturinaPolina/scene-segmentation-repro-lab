# Outputs layout

Run artifacts grouped by purpose. Heavy directories are gitignored; selected review packages may be tracked.

```
outputs/
├── runs/                   # model runs (gitignored)
│   ├── ssc/                # sequential sentence classification
│   ├── llama/              # fine-tuning dry-runs and baselines
│   └── prompting/          # prompting baselines, sweeps, full eval
├── review/                 # human review artifacts
│   ├── markdown/           # render_review.py Markdown exports
│   ├── packages/           # bundled per-run review sets (jsonl, csv)
│   └── excel/              # Excel experiment tables and comparisons
├── analysis/               # ad-hoc profiling and scoring experiments
├── reproduction/           # STSS-Test-2 bounded reproduction manifests
└── artifacts/              # lightweight shared outputs
    ├── figures/
    ├── logs/
    └── predictions/
```

## Conventions

- Default run paths come from `src/workflow_runtime.py`:
  - `output_dir_for(root, track, date, slug)` → `outputs/runs/<track>/<date>/<slug>/`
  - `track=reproduction` → `outputs/reproduction/<date>/<slug>/`
  - `prompting_run_root(root, date)` → `outputs/runs/prompting/<date>/`
- Override with `--output_dir` on individual runners when needed.
- Reproducibility files in each run folder: `command.txt`, `config.json`, `summary.json`.
