# Excel Prompting Experiment Report (2026-05-30)

## Scope

This report documents today’s prompting experiments on two new Excel-derived texts:

- `data/raw/Gaensemagd_sentence level.xlsx`
- `data/raw/Kleist_sentence level.xlsx`

Goal: run the winning prompting configuration (family B, reasoning off, non-free Nemotron) with the same stratified runner used in the project report pipeline, compare against gold scene-border labels, and investigate why results differ from `docs/PROMPTING_RESULTS_REPORT.md`.

## What Was Implemented

1. Added preprocessing for Excel inputs:
   - `scripts/prepare_excel_prompting_inputs.py`
   - Produces:
     - `data/processed/excel_prompting/*__sheet1.csv`
     - `data/processed/excel_prompting/*__for_prompting.txt`
     - `data/processed/excel_prompting/*__for_prompting.jsonl`
     - `data/processed/excel_prompting/*__gold_labels.csv`
     - `data/processed/manifest_excel_prompting.json`

2. Added direct scoring against Excel gold:
   - `scripts/score_prompting_vs_excel_gold.py`

3. Added FP analysis utilities:
   - `scripts/export_top_fp_review_table.py`

4. Extended report runner path:
   - `src/run_prompting_stratified.py`
   - New input mode: `--excel_manifest data/processed/manifest_excel_prompting.json`
   - Enables upstream-style prompt/context construction for Excel-manifest data.

5. Added normalization what-if tool:
   - `scripts/normalization_what_if.py`
   - Scenarios:
     - `baseline`
     - `burst_collapse`
     - `min_scene_len_3`
     - `burst_collapse_plus_min_scene_len_3`

## Main Commands Run

### Full-eval stratified runner on Excel manifest

```bash
OPENROUTER_API_KEY="$OPENROUTER_API_KEY" PYTHONUNBUFFERED=1 .venv/bin/python -u src/run_prompting_stratified.py \
  --excel_manifest data/processed/manifest_excel_prompting.json \
  --model nvidia/nemotron-3-super-120b-a12b \
  --prompt_family B \
  --full_eval \
  --reasoning off \
  --temperature 0 \
  --top_p 1.0 \
  --seed 1337 \
  --max_tokens 256 \
  --response_format json_schema \
  --schema_file src/prompts/json_schema_label_reason.json \
  --date 2026-05-30-excel-full-eval
```

Primary output directory:

- `outputs/prompting/2026-05-30-excel-full-eval/full_nvidia_nemotron-3-super-120b-a12b_familyB_reasoning-off/`

### Gold-vs-pred scoring

Produced:

- `score_vs_gold_gaensemagd.json`
- `score_vs_gold_kleist.json`
- `score_vs_gold_aggregate.json`

### FP analysis

Produced:

- `fp_analysis_summary.json`
- `top_fp_review_table.csv`
- `top_fp_review_table.json`

### Normalization what-if

Produced:

- `normalization_what_if.json`
- `normalization_what_if.csv`

## Results Summary

### A) Full-eval run (before normalization)

From `score_vs_gold_*.json`:

- Gaensemagd: P=0.1034, R=0.4286, F1=0.1667, Acc=0.5775
- Kleist: P=0.0595, R=0.3571, F1=0.1020, Acc=0.6408
- Aggregate: P=0.0708, R=0.3810, F1=0.1194, Acc=0.6266

### B) Comparison vs baseline-runner TXT path

From `comparison_vs_baseline_runner.json`:

- Aggregate delta (new stratified-runner full-eval minus old baseline-runner):
  - Precision: +0.0218
  - Recall: +0.0477
  - F1: +0.0340
  - Accuracy: +0.1013

Interpretation: using `run_prompting_stratified.py` improves results, but precision remains low due to high FP volume.

### C) FP proximity profile

From `fp_analysis_summary.json`:

- Gaensemagd: 26 FPs; 19.23% within +-1 of gold boundary; 42.31% within +-3
- Kleist: 79 FPs; 17.72% within +-1; 32.91% within +-3

Interpretation: many false positives are not immediate near-boundary shifts; over-segmentation remains substantial.

### D) Normalization what-if

From `normalization_what_if.csv` (aggregate rows):

- Baseline: P=0.0714, R=0.3810, F1=0.1203, tol3_F1=0.3889, tol5_F1=0.4468
- Burst collapse: P=0.0595, R=0.2381, F1=0.0952, tol3_F1=0.4615, tol5_F1=0.5122
- Min scene len 3: P=0.0794, R=0.2381, F1=0.1190, tol3_F1=0.5316, tol5_F1=0.5833
- Burst collapse + min scene len 3: P=0.0833, R=0.2381, F1=0.1235, tol3_F1=0.5455, tol5_F1=0.6000

Interpretation:

- Strict exact-recall drops under stronger normalization (expected).
- Relaxed metrics (`tol3`, `tol5`) improve materially after smoothing, indicating many predicted boundaries are near-but-fragmented placements.

## Why This Still Differs From PROMPTING_RESULTS_REPORT

Runtime evidence collected today indicates:

1. Different data regime:
   - Report pipeline evaluates STSS-Test-2 XMI texts (`~11k` sentences total).
   - Current experiment uses two Excel-derived texts (`316` sentences total).

2. Different boundary structure:
   - STSS border rates observed in runner profile:
     - `Aus guter Familie`: 0.0436
     - `Effi Briest`: 0.0384
   - Excel-derived border rates:
     - `gaensemagd`: 0.0986
     - `kleist`: 0.0571

3. Evaluation mode matters:
   - Full-eval (natural imbalance) vs stratified balancing materially changes precision/recall behavior.

4. Parser/config drift is not primary:
   - Prompt family, model, reasoning, response format, and context budget were held aligned for comparison runs.

## Cross-Run Comparison (Latest Update)

### E) Controlled one-factor post-processing sweep (Nemotron, full_eval)

From `outputs/review/excel_controlled_sweep/comparison/normalization_what_if.csv` (aggregate):

- `none`: P=0.0583, R=0.3333, F1=0.0993, tol3_F1=0.3604, tol5_F1=0.4242
- `min_scene_len_3`: P=0.0597, R=0.1905, F1=0.0909, tol3_F1=0.5063, tol5_F1=0.5676
- `min_scene_len_5`: P=0.0652, R=0.1429, F1=0.0896, tol3_F1=0.5373, tol5_F1=0.6667

Interpretation:

- Stronger smoothing improves tolerant boundary quality (`tol3`, `tol5`) but reduces strict exact recall/F1.
- For tolerance-oriented evaluation, `min_scene_len_5` is best among tested rules.

### F) Apples-to-apples stratified comparison (same model/prompt/scorer)

Compared:

- STSS: `outputs/prompting/2026-05-16-phaseC-E6-roff-full/strat_nvidia_nemotron-3-super-120b-a12b_familyB_reasoning-off/summary.json`
- Excel: `outputs/prompting/2026-05-30-debug-stratified-compare/strat_nvidia_nemotron-3-super-120b-a12b_familyB_reasoning-off/summary.json`

Micro-averaged metrics:

- tol0 F1: STSS `0.7730` vs Excel `0.7442` (delta `-0.0288`)
- tol1 F1: STSS `0.7936` vs Excel `0.7619` (delta `-0.0317`)
- tol3 F1: STSS `0.8301` vs Excel `0.7805` (delta `-0.0496`)

Interpretation:

- When evaluation protocol is aligned (`stratified` vs `stratified`), Excel is worse but not catastrophically worse than STSS.
- The very large degradation seen elsewhere is primarily tied to `full_eval` class imbalance and resulting FP pressure.

### G) Premium model sweep and ranking on Excel full_eval

From:

- `outputs/prompting/2026-05-30-excel-3model-sweep/comparison_3model_full_eval.csv`
- `outputs/prompting/2026-05-30-excel-opus4/full_anthropic_claude-opus-4_familyB_reasoning-off/summary.json`
- `outputs/prompting/2026-05-31-excel-gemini-reasoning-on/full_google_gemini-2.5-pro_familyB_reasoning-on/summary.json`

Model ranking (higher is better):

| Rank | Model | Reasoning | macro tol0 F1 | macro tol3 F1 |
| --- | --- | --- | --- | --- |
| 1 | `google/gemini-2.5-pro` | on | 0.4981 | 0.7617 |
| 2 | `google/gemini-2.5-pro` | low | 0.4949 | 0.7184 |
| 3 | `anthropic/claude-opus-4` | off | 0.4365 | 0.6134 |
| 4 | `openai/gpt-4.1` | off | 0.4190 | 0.6160 |
| 5 | `anthropic/claude-sonnet-4` | off | 0.3506 | 0.4965 |

### H) Gemini reasoning mode delta (`on` vs `low`)

Compared:

- `outputs/prompting/2026-05-31-excel-gemini-reasoning-on/full_google_gemini-2.5-pro_familyB_reasoning-on/summary.json`
- `outputs/prompting/2026-05-30-excel-3model-sweep/full_google_gemini-2.5-pro_familyB_reasoning-low/summary.json`

Delta (`on` minus `low`):

- macro tol0 F1: `+0.0032` (0.4981 vs 0.4949)
- macro tol1 F1: `+0.0422` (0.6779 vs 0.6357)
- macro tol3 F1: `+0.0433` (0.7617 vs 0.7184)
- avg latency: slightly lower for `on` (`3.434s` vs `3.505s`)
- parse failures: unchanged at `0`

Notes:

- `google/gemini-2.5-pro` does not accept `reasoning=off`; minimum working setting is `reasoning=low`.
- On this Excel full_eval set, `reasoning=on` is currently the best-performing tested configuration.

## Next Recommended Step

Choose one of two objectives and lock it in a decision note:

1. **Strict exact boundary objective**  
   Prioritize tol0/exact metrics and continue with model-side improvements (or milder smoothing).

2. **Tolerance-oriented boundary objective**  
   Use `min_scene_len_5` and the current top model candidate (`google/gemini-2.5-pro`, `reasoning=on`) as the starting point, then validate on additional Excel-derived texts.

In either case, keep a single canonical scorer path for final headline numbers to avoid minor script-to-script exact-metric drift.

