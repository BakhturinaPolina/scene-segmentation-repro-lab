# Excel Prompting Experiments Comparison Report

Date: 2026-06-01  
Track: prompting  
Scope: Excel-derived sentence-level scene-boundary experiments on:
- `data/raw/Gaensemagd_sentence level.xlsx`
- `data/raw/Kleist_sentence level.xlsx`

---

## 1) Objective

This report consolidates all completed experiments that compare prompting-based boundary labels against gold labels derived from the two Excel files above. It also provides:
- a minimal file set to share on GitHub for colleague review;
- a reviewer-friendly strategy to write model outputs back into Excel workbooks.

Primary prior references:
- `docs/EXCEL_PROMPTING_2026-05-30_REPORT.md`
- `research_log/runs/2026-05-30__prompting__experiment__excel-manifest-familyb-full-eval-and-whatif.md`
- `research_log/runs/2026-05-30__prompting__experiment__excel-controlled-postprocessing-sweep.md`
- `research_log/experiments/experiment__prompting__post-processing__excel-controlled-sweep.md`

---

## 2) Data and Label Construction

The preprocessing pipeline in `scripts/prepare_excel_prompting_inputs.py` converts each workbook into:
- sentence text for prompting (`*_for_prompting.txt`, `*_for_prompting.jsonl`);
- gold labels (`*_gold_labels.csv`);
- a manifest (`data/processed/manifest_excel_prompting.json`).

Gold label rule:
- `BORDER` when current `scene_id` differs from previous sentence scene_id;
- otherwise `NOBORDER`.

Resulting corpus profile:
- Gaensemagd: 71 evaluated rows, 7 gold borders (9.86%)
- Kleist: 245 evaluated rows, 14 gold borders (5.71%)
- Aggregate: 316 rows, 21 gold borders (6.65%)

---

## 3) Experiment Inventory

## 3.1 Baseline Excel-manifest full-eval run

Run note: `research_log/runs/2026-05-30__prompting__experiment__excel-manifest-familyb-full-eval-and-whatif.md`

Configuration:
- Model: `nvidia/nemotron-3-super-120b-a12b`
- Prompt family: `B` (`src/prompts/B_zero_shot_json.txt`)
- Decoding: `temperature=0`, `top_p=1.0`, `seed=1337`, `max_tokens=256`
- Output schema: `src/prompts/json_schema_label_reason.json`
- Eval mode: full_eval on `data/processed/manifest_excel_prompting.json`

Exact aggregate metrics (score vs gold):
- Precision: 0.0708
- Recall: 0.3810
- F1: 0.1194
- Accuracy: 0.6266

Interpretation:
- recall is moderate, but precision is low due to many false positives (over-segmentation).

## 3.2 Controlled one-factor post-processing sweep

Experiment note: `research_log/experiments/experiment__prompting__post-processing__excel-controlled-sweep.md`  
Run note: `research_log/runs/2026-05-30__prompting__experiment__excel-controlled-postprocessing-sweep.md`  
Comparison artifact: `outputs/review/excel_controlled_sweep/comparison/normalization_what_if.csv`

Single varying factor:
- post-processing rule (`none`, `min_scene_len_3`, `min_scene_len_5`)

Aggregate outcomes:

| Scenario | Precision | Recall | F1 (exact) | tol3 F1 | tol5 F1 |
|---|---:|---:|---:|---:|---:|
| none | 0.0583 | 0.3333 | 0.0993 | 0.3604 | 0.4242 |
| min_scene_len_3 | 0.0597 | 0.1905 | 0.0909 | 0.5063 | 0.5676 |
| min_scene_len_5 | 0.0652 | 0.1429 | 0.0896 | 0.5373 | 0.6667 |

Interpretation:
- stronger smoothing decreases exact recall/F1;
- tolerant boundary quality improves substantially, especially at tol5.

## 3.3 Premium model sweep and reasoning comparison

Summarized in `docs/EXCEL_PROMPTING_2026-05-30_REPORT.md`.

Observed ranking on Excel full_eval (macro metrics):
1. `google/gemini-2.5-pro` (`reasoning=on`)
2. `google/gemini-2.5-pro` (`reasoning=low`)
3. `anthropic/claude-opus-4` (`reasoning=off`)
4. `openai/gpt-4.1` (`reasoning=off`)
5. `anthropic/claude-sonnet-4` (`reasoning=off`)

Best reported macro performance:
- tol0 F1: 0.4981
- tol3 F1: 0.7617

Interpretation:
- premium models significantly reduce the gap seen in Nemotron full_eval baseline.

## 3.4 Stratified-vs-full-eval comparability check

Also documented in `docs/EXCEL_PROMPTING_2026-05-30_REPORT.md`.

Finding:
- when protocol is aligned (`stratified` vs `stratified`), Excel is somewhat worse than STSS but not catastrophically worse;
- large observed degradation is mainly tied to `full_eval` class imbalance and false-positive pressure.

---

## 4) Error Shape and Diagnostic Findings

From FP diagnostics (`scripts/export_top_fp_review_table.py` and scenario FP tables):
- A meaningful fraction of FP predictions are near true boundaries (`+-1` or `+-3` sentences), indicating placement drift and fragmentation rather than fully unrelated boundaries.
- Persistent error mode is boundary over-triggering in narrative transition zones.
- Smoothing (`min_scene_len_3/5`) removes many clustered FPs and improves tolerant metrics.

Key numeric signals:
- Baseline aggregate predicted borders: 120 vs 21 gold borders (~5.7x overprediction).
- Tolerant F1 gains under min-scene-length filtering support a post-processing layer when tolerance-oriented review is acceptable.

---

## 5) Why Excel Results Differ from STSS Campaign Headline

Reference comparison report: `docs/PROMPTING_RESULTS_REPORT.md`

Major non-equivalences:
- different data regime (2 Excel-derived texts vs STSS corpus slice);
- different class balance and boundary density;
- protocol sensitivity (full_eval vs stratified);
- run context and model routing differences across campaign phases.

Conclusion:
- avoid direct headline-number comparison without protocol alignment;
- compare like-for-like (same scorer, mode, and split policy).

---

## 6) Recommended Reporting Position

Choose and document one primary objective before claiming a default configuration:

1. **Strict exact-boundary objective**  
   Optimize tol0/exact precision+recall and avoid aggressive smoothing.

2. **Tolerance-oriented objective**  
   Prefer boundary proximity quality (tol3/tol5), use smoothing (currently `min_scene_len_5`) and validate on additional Excel texts.

Current evidence favors:
- `min_scene_len_5` for tolerance-oriented review workflows;
- premium model candidates (especially Gemini 2.5 Pro) for stronger baseline quality.

---

## 7) Minimal GitHub Push Set for Colleague Review

Goal: enough for review and reproducibility, without output overload.

### 7.1 Recommended (push)

- `docs/EXCEL_PROMPTING_2026-05-30_REPORT.md` (existing detailed run report)
- `docs/EXCEL_EXPERIMENTS_COMPARISON_REPORT.md` (this consolidated report)
- `scripts/prepare_excel_prompting_inputs.py`
- `scripts/score_prompting_vs_excel_gold.py`
- `scripts/normalization_what_if.py`
- `scripts/export_top_fp_review_table.py`
- `data/processed/manifest_excel_prompting.json`
- `research_log/experiments/experiment__prompting__post-processing__excel-controlled-sweep.md`
- `research_log/runs/2026-05-30__prompting__experiment__excel-controlled-postprocessing-sweep.md`
- `research_log/runs/2026-05-30__prompting__experiment__excel-manifest-familyb-full-eval-and-whatif.md`
- `research_log/artifacts/artifact__excel-controlled-postprocessing-sweep__postprocessing-comparison-table.md`
- `research_log/artifacts/artifact__excel-controlled-postprocessing-sweep__scenario-fp-review-tables.md`

### 7.2 Avoid pushing by default

- `outputs/**` (large, regenerable, may overwhelm reviewers)
- per-run raw review JSONLs unless explicitly requested for forensic review
- broad historical logs unrelated to Excel prompting scope

---

## 8) Writing Results Back Into Excel for Easier Human Review

Recommended workflow:
- keep original raw workbooks unchanged;
- generate review copies (e.g., `data/review/*_with_predictions.xlsx`) with merged model outputs and evaluation annotations.

Suggested added columns:
- `predicted_label`
- `prediction_confidence`
- `prediction_reason`
- `eval_status` (`TP/FP/FN/TN`)
- `distance_to_nearest_gold`
- `normalized_label_min3`
- `normalized_label_min5`
- `normalized_status_min5`

Implementation script:
- `scripts/export_excel_with_predictions.py`

Benefits:
- reviewer sees original sentence rows and model decision side-by-side;
- exact-vs-smoothed behavior is visible directly in spreadsheet filters;
- no need to inspect JSONL/CSV artifacts manually.

---

## 9) Next Actions

1. Confirm primary objective (exact-first vs tolerance-first) and record decision note.
2. Export workbook review copies with merged predictions.
3. Run one confirmatory pass on additional Excel-derived texts before policy lock-in.
