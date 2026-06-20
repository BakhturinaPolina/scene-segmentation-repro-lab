# Excel False-Positive Reduction — OFAT Experiment Plan

**Date:** 2026-06-14  
**Track:** prompting  
**Corpus:** Gänsemagd + Kleist ([`data/manifests/excel_prompting.json`](../../data/manifests/excel_prompting.json))  
**Baseline report:** [`docs/prompting/EXCEL_EXPERIMENTS_COMPARISON_REPORT.md`](../prompting/EXCEL_EXPERIMENTS_COMPARISON_REPORT.md)  
**Experiment note:** [`research_log/experiments/experiment__prompting__excel-fp-ofat__openrouter-sweep.md`](../../research_log/experiments/experiment__prompting__excel-fp-ofat__openrouter-sweep.md)

---

## Goal

Raise **relaxed F1@3 (f3)** on the two Excel-annotated texts while reducing **false-positive over-prediction** (models marking far too many scene borders). Each stage changes **one factor** only.

| Metric | Current best | Target |
|--------|-------------:|-------:|
| F3 (tol3) | 0.76 (Gemini 2.5 Pro) | ≥ **0.80** |
| Over-prediction ratio | ~5–6× gold | ≤ **2×** (≤ 42 predicted borders) |

**Side metric (every run):** `overprediction_ratio = n_predicted_BORDER / n_gold_BORDER`

---

## Progress snapshot (updated 2026-06-16)

**Status:** Gemini B **stability rerun complete** — macro F3@3 **0.771** (May **0.762**, Δ+0.009); recall and parse rate stable. **Canonical anchor confirmed** for dProse / post-process next steps.

| Target | Goal | Best so far | Met? |
|--------|-----:|------------:|:----:|
| F3@3 | ≥ 0.80 | **0.762** (Gemini 2.5 Pro + B, reasoning on) | ✗ |
| Over-prediction | ≤ 2× gold | **0.71×** (Laguna M + Q) / **0.90×** (Nemotron Super + Q) | ✓ (free+Q) |
| Stage gate F3 | ≥ 0.76 | **0.762** (Gemini B) | ✗ (close) |

**Key findings:**

1. Family **B** on free models over-predicts heavily (3–15× gold) with recall≈1.0.
2. Family **Q** fixes over-segmentation on **weak/free** models (Nemotron Super + Q → F3 **0.604**, over **0.90×**) but caps below Gemini B.
3. **Gemini + Q rejected (early stop):** Gänsemagd complete — same **15** raw BORDER preds as Gemini B (**2.14×** gold), F3@3 **0.667 vs 0.824** (−0.16), R@3 **0.86 vs 1.0**. Kleist aborted at **49/245** with same miss pattern (idx 1 FN). Q shifts errors; it does not improve the premium model.
4. Two-pass verify and min-gap post-process did not raise F3 on Q caches.

**Blocker:** OpenRouter free-tier day quota (Laguna XS + O, context w32). Paid Gemini path unaffected.

| Stage | Status | Comment |
|-------|--------|---------|
| 0 Prep | ✓ Done | Manifest, gold labels, smoke (`2026-06-14-excel-ofat-smoke`), API key in use |
| 1 Model sweep (Family B) | ⚠ Partial | **8/14 complete**, 6 incomplete (rate limits / no summary). No complete run met F3 gate. |
| 2 Decoding | — Not started | Waiting on Stage-1 winner; Q prompt superseded model-only path |
| 3 Prompt wording | ⚠ Partial | **Q done** (4 free models); **Gemini+Q stopped early** (reject); **O partial**; **N/P not run** |
| 4 Context window | ⚠ Blocked | w32 started on Nemotron+Q; aborted on day quota (`2026-06-14-excel-ofat-context-w32`) |
| 5 Post-process | ⚠ Partial | Offline `min_gap` on Laguna XS Kleist Q cache only (+0.03 F3 doc-level) |
| 6 Two-pass verify | ✓ Done | 0 borders rejected on Q caches — no F3 change |
| 7 Discourse rules | — Not started | |
| 8 Tiny LoRA | — Not started | |

**Artifacts:** `review/excel_ofat_stage1_*_summary.csv`, `review/excel_ofat_pipeline_candidates.json`, `review/excel_ofat_pipeline_status.md`, logs in `logs/excel_ofat/`, runs under `outputs/runs/prompting/2026-06-14-excel-ofat-*`.

---

## Gemini B stability rerun (2026-06-16)

**Goal:** Reproduce the May premium baseline on the same two Excel texts with identical controls (Family B, reasoning on, seed 1337) using the current runner and manifest.

| | May baseline | Stability rerun |
|--|--------------|-----------------|
| Date tag | `2026-05-31-excel-gemini-reasoning-on` | `2026-06-16-excel-gemini-familyB-stability` |
| Manifest | `data/processed/manifest_excel_prompting.json` (legacy) | `data/manifests/excel_prompting.json` (same corpus) |
| Runner | `src/run_prompting_stratified.py` | `src/runners/run_prompting_stratified.py` |
| Macro F3@3 | **0.762** | **0.771** |
| Macro R@3 | **1.00** | **1.00** |
| Over-pred (raw) | ~2.3× (49/21) | **2.24×** (47/21) |
| Parse failures | 0% | 0% |

**Verdict:** ✓ Stable within ±0.02 gate. Gänsemagd F3@3 unchanged (0.824); Kleist +0.018 (0.700 → 0.718).

**Command:**

```bash
OPENROUTER_API_KEY="$OPENROUTER_API_KEY" PYTHONUNBUFFERED=1 .venv/bin/python -u \
  src/runners/run_prompting_stratified.py \
  --excel_manifest data/manifests/excel_prompting.json \
  --model google/gemini-2.5-pro \
  --prompt_family B --full_eval --reasoning on \
  --temperature 0 --top_p 1.0 --seed 1337 --max_tokens 256 \
  --response_format json_schema \
  --schema_file src/prompts/json_schema_label_reason.json \
  --context_size 409 \
  --date 2026-06-16-excel-gemini-familyB-stability
```

**Outputs:** `outputs/runs/prompting/2026-06-16-excel-gemini-familyB-stability/full_google_gemini-2.5-pro_familyB_reasoning-on/` · Log: `logs/excel_ofat/gemini_B_stability_rerun.log`

**Pass criterion:** macro F3@3 within **±0.02** of May (0.74–0.78) and same qualitative profile (R@3 ≈ 1.0, over-pred ~2×).

---

## Stage 1 results — Family B (model only)

Run root: `outputs/runs/prompting/2026-06-14-excel-ofat-s1` · Aggregator: `review/excel_ofat_stage1_B_summary.csv`

| Model | Complete | F3@3 | P@3 | R@3 | Over-pred | Pred borders |
|-------|:--------:|-----:|----:|----:|----------:|-------------:|
| nex-n2-pro:free | partial (Gänsemagd only) | 0.609 | 0.44 | 1.00 | 3.3× | 23 |
| gemma-4-26b (paid) | ✓ | 0.544 | 0.37 | 1.00 | 3.5× | 73 |
| qwen3.5-flash (paid) | ✓ | 0.477 | 0.50 | 0.46 | **0.95×** | 20 |
| laguna-m.1:free | ✓ | 0.393 | 0.25 | 1.00 | 6.5× | 137 |
| nemotron-super:free | ✓ | 0.370 | 0.23 | 1.00 | 6.8× | 143 |
| laguna-xs.2:free | ✓ | 0.338 | 0.21 | 0.93 | 7.6× | 159 |
| owl-alpha | ✓ | 0.293 | 0.17 | 1.00 | 9.5× | 199 |
| llama-3.1-8b (paid) | ✓ | 0.250 | 0.15 | 1.00 | 13.4× | 281 |
| nemotron-nano:free | ✓ | 0.232 | 0.13 | 1.00 | 14.5× | 304 |
| llama-3.3-70b, ultra, gpt-oss×3 | ✗ incomplete | — | — | — | — | — |

**Stage 1 decision:** No Family B model passes F3 ≥ 0.76. Paid Qwen3.5-Flash alone hits the over-pred target (0.95×) but with low recall. Pivoted to Family **Q** on top free models before finishing remaining Stage-1 models.

---

## Stage 3 results — Family Q (precision-fixed prompt, early pivot)

Run root: `outputs/runs/prompting/2026-06-14-excel-ofat-s1-Q` · Prompt: [`Q_zero_shot_json_precision_fixed.txt`](../../src/prompts/Q_zero_shot_json_precision_fixed.txt) · Aggregator: `review/excel_ofat_stage1_Q_summary.csv`

| Model | F3@3 | P@3 | R@3 | Over-pred | Comment |
|-------|-----:|----:|----:|----------:|---------|
| **nemotron-super:free** | **0.604** | 0.64 | 0.57 | 0.90× | **Current best macro F3**; under-predicts slightly |
| laguna-xs.2:free | 0.591 | 0.53 | 0.68 | 1.48× | Best recall among Q runs |
| laguna-m.1:free | 0.458 | 0.55 | 0.39 | 0.71× | Lowest over-pred; recall drop |
| nemotron-nano:free | 0.279 | 0.16 | 1.00 | 10.3× | Q prompt ineffective on nano |

Per-document (Nemotron Super + Q): Gänsemagd F3=0.615 R=0.57; Kleist F3=0.593 R=0.57.

---

## Stage 3 results — Family O (German fairy few-shot)

Run root: `outputs/runs/prompting/2026-06-14-excel-ofat-O` · Aggregator: `review/excel_ofat_stage1_O_summary.csv`

| Model | Complete | F3@3 | R@3 | Over-pred | Comment |
|-------|:--------:|-----:|----:|----------:|---------|
| nemotron-super:free | ✓ | 0.425 | 0.86 | 4.3× | 31% parse failures on Kleist; recall↑ vs Q, over-pred↑ |
| laguna-xs.2:free | ✗ (2/316) | — | — | — | Guardrail abort — day quota |

**Gänsemagd-only signal (O vs Q, Nemotron Super):** O F3=0.429 R=0.86 over=4.1× vs Q F3=0.615 R=0.57 over=1.0× — confirms O trades precision for recall.

---

## Improvement pipeline (post-Q)

Script: [`scripts/evaluation/excel_ofat_improve_pipeline.py`](../../scripts/evaluation/excel_ofat_improve_pipeline.py) · Status: [`review/excel_ofat_pipeline_status.md`](../../review/excel_ofat_pipeline_status.md)

| Step | Action | Result |
|------|--------|--------|
| 2 Verify Q | yes/no verifier on Nemotron + Laguna XS Q caches | 19 + 31 borders checked; **0 rejected**; F3 unchanged (0.604 / 0.591) |
| 3 min_gap | Offline on Laguna XS **Kleist** Q cache | gap 2–3: F3 **0.545** (+0.03 vs raw 0.514), 19 pred borders |
| 4 Context w32 | Nemotron Super + Q, `--sentence_window 32` | **Blocked** — day quota at start (`logs/excel_ofat/context_w32_*.log`) |

---

## Stage 0 — Fixed baseline

| Control | Value |
|---------|-------|
| Prompt family | **B** — [`src/prompts/B_zero_shot_json.txt`](../../src/prompts/B_zero_shot_json.txt) |
| Decoding | `temperature=0`, `top_p=1.0`, `seed=1337`, `max_tokens=256` |
| Context | token-budget **409** (default) |
| Evaluator | [`evaluate_sampled`](../../src/runners/run_prompting_stratified.py) at tol 0/1/3 |
| Manifest | `--excel_manifest data/manifests/excel_prompting.json --full_eval` |

Corpus: **316 sentences**, **21 gold borders** (6.7%).

---

## Paid-model cost table (316 sentences, Family B, reasoning off)

| Component | Tokens/request | × 316 |
|-----------|---------------:|------:|
| Input | ~620 | 195,920 |
| Output | ~85 | 26,860 |

| Model | Slug | In $/1M | Out $/1M | **Est. run cost** |
|-------|------|--------:|---------:|------------------:|
| Llama 3.1 8B | `meta-llama/llama-3.1-8b-instruct` | $0.02 | $0.03 | **$0.005** |
| gpt-oss-20b | `openai/gpt-oss-20b` | $0.029 | $0.14 | **$0.009** |
| gpt-oss-120b | `openai/gpt-oss-120b` | $0.039 | $0.18 | **$0.012** |
| Qwen3.5-Flash | `qwen/qwen3.5-flash-02-23` | $0.065 | $0.26 | **$0.020** |
| Gemma 4 26B | `google/gemma-4-26b-a4b-it` | $0.06 | $0.33 | **$0.021** |

All other Stage-1 models are **free**. Full paid sweep ≈ **$0.07**.

---

## Model capability matrix (OpenRouter, June 2026)

Profiles live in [`src/core/openrouter_model_profiles.json`](../../src/core/openrouter_model_profiles.json).

| Model | Context | Free | Recommended profile |
|-------|--------:|:----:|---------------------|
| [Llama 3.3 70B](https://openrouter.ai/meta-llama/llama-3.3-70b-instruct:free) | 131K | ✓ | `json_object`, reasoning off |
| [Laguna XS.2](https://openrouter.ai/poolside/laguna-xs.2:free) | 262K | ✓ | `json_object`, reasoning off |
| [Laguna M.1](https://openrouter.ai/poolside/laguna-m.1:free) | 262K | ✓ | `json_object`, reasoning off |
| [Owl Alpha](https://openrouter.ai/openrouter/owl-alpha) | 1M | ✓ | `json_schema`, reasoning off |
| [Nex-N2-Pro](https://openrouter.ai/nex-agi/nex-n2-pro:free) | 262K | ✓ | `json_schema`, reasoning off |
| [Nemotron 3 Ultra](https://openrouter.ai/nvidia/nemotron-3-ultra-550b-a55b:free) | 1M | ✓ | `json_object`, reasoning off |
| [Nemotron 3 Super](https://openrouter.ai/nvidia/nemotron-3-super-120b-a12b:free) | 1M | ✓ | `json_schema`, reasoning off |
| [Nemotron 3 Nano](https://openrouter.ai/nvidia/nemotron-3-nano-30b-a3b:free) | 256K | ✓ | `json_object`, reasoning off |
| [gpt-oss-120b free](https://openrouter.ai/openai/gpt-oss-120b:free) | 131K | ✓ | `json_object`, reasoning off |
| Llama 3.1 8B (paid) | 131K | — | `json_schema` |
| gpt-oss-20b/120b (paid) | 131K | — | `json_schema` |
| Qwen3.5-Flash (paid) | 1M | — | `json_schema` |
| Gemma 4 26B (paid) | 262K | — | `json_schema` |

---

## Execution checklist

### Stage 0 — Prep

- [x] Gold labels: `data/processed/excel_prompting/*__gold_labels.csv`
- [x] Manifest: `data/manifests/excel_prompting.json`
- [x] `export OPENROUTER_API_KEY=...`
- [x] Smoke: `--dry_run 4` on one free model (`2026-06-14-excel-ofat-smoke`)

### Stage 1 — Model sweep (OFAT: model only)

**Status:** 8/14 complete · **Gate not met** · See [Stage 1 results](#stage-1-results--family-b-model-only) above.

```bash
bash scripts/sweeps/excel_ofat_stage1_models.sh
python scripts/evaluation/summarize_excel_ofat.py \
  --run_root outputs/runs/prompting/2026-06-14-excel-ofat-s1 \
  --out review/excel_ofat_stage1_summary.csv
```

Pick **top-2** by F3, then precision. Gate: F3 ≥ 0.76 or materially lower over-prediction.

**Resume incomplete models:** `DATE_TAG=2026-06-14-excel-ofat-s1 RESUME=1 bash scripts/sweeps/excel_ofat_stage1_models.sh`

### Stage 2 — Decoding (best model from Stage 1)

**Status:** Not started (Q prompt pivot took priority).

| ID | Variable |
|----|----------|
| 2-A | `temperature=0.2` |
| 2-B | `top_p=0.9`, `temperature=0` |
| 2-C | `presence_penalty=1.0` (if supported) |

### Stage 3 — Prompt wording

**Status:** Q complete (4 models); O partial; N/P pending.

| ID | Family | Template | Status |
|----|--------|----------|--------|
| 3-A | N | rarity prior (~7% borders) | Not run |
| 3-B | O | German fairy few-shot | Nemotron ✓; Laguna XS blocked |
| 3-C | P | anti-example | Not run |
| — | **Q** | precision-fixed (added) | **4 models complete** — best path so far |

Family Q rerun (top Stage-1 models):
```bash
bash scripts/sweeps/excel_ofat_stage1_fixed_prompt.sh   # PROMPT_FAMILY=Q
```

Family O on top-2 Q models:
```bash
DATE_TAG=2026-06-14-excel-ofat-O RESUME=1 bash scripts/sweeps/excel_ofat_prompt_O_top2.sh
```

### Stage 4 — Context window

**Status:** w32 blocked on API quota; w64/w16 not run.

Requires `--context_mode sentences`:

| ID | `--sentence_window` | `--sentence_stride` |
|----|--------------------:|--------------------:|
| 4-A | 64 | 48 |
| 4-B | 32 | 24 |
| 4-C | 16 | 8 |

Baseline token mode: `--context_mode tokens --context_size 409`.

Resume:
```bash
python scripts/evaluation/excel_ofat_improve_pipeline.py --step context
```

### Stage 5 — Post-processing

**Status:** Offline min_gap on one doc only; full scenario sweep not run.

```bash
python src/postprocess/run_postprocess.py \
  --cache outputs/runs/prompting/.../cache_<stem>.json \
  --scenario all --tolerances 0 1 3
```

New scenarios: `min_scene_len_2`, `_4`, `_6`, `n_per_k_15` (1 border per 15 sentences).

### Stage 6 — Two-pass verify (if F3 < 0.80)

**Status:** ✓ Done on Q caches — no precision gain (0 rejected).

```bash
python src/runners/run_two_stage_verify.py \
  --excel_manifest data/manifests/excel_prompting.json \
  --run_dir outputs/runs/prompting/<date>/full_<model>_familyB_reasoning-off \
  --verify_style yes_no --context_window 3 --dry_run
```

### Stage 7 — Discourse rules

**Status:** Not started.

Scenario `discourse_plus_min_scene_len_3` (spaCy `de_core_news_sm` or regex fallback).

### Stage 8 — Tiny LoRA (last resort)

**Status:** Not started.

See [`docs/planning/F3_IMPROVEMENT_PLAN.md`](F3_IMPROVEMENT_PLAN.md) — train on 316-sentence Excel corpus.

---

## Next steps (priority order)

1. **Complete Gemini B stability rerun** — compare `summary.json` to May; if stable, lock as canonical anchor for post-process experiments.
2. **Post-process on Gemini B cache** (`min_scene_len_5`, `min_gap`) if over-pred remains ~2×.
3. **Wait for OpenRouter day-quota reset**, then resume Laguna XS + O and context w32/w64 (free-tier path).
4. **Run Family N and P** on Nemotron Super + Laguna XS (optional; unlikely to beat Gemini B).
5. **Discourse rules** (Stage 7) if post-process alone insufficient.

---

## Representative Stage-1 command

```bash
python src/runners/run_prompting_stratified.py \
  --excel_manifest data/manifests/excel_prompting.json \
  --model "<SLUG>" --prompt_family B --full_eval \
  --apply_model_profile \
  --temperature 0 --top_p 1.0 --seed 1337 --max_tokens 256 \
  --context_size 409 \
  --date 2026-06-14-excel-ofat-s1
```

`--apply_model_profile` reads [`openrouter_model_profiles.json`](../../src/core/openrouter_model_profiles.json) and sets `reasoning`, `response_format`, and schema file per model.

---

## Research logging

After each stage: run note in `research_log/runs/`, artifact note for comparison tables. See [`rule.md`](../../rule.md).

---

## Code map

| Component | Path | Added/updated |
|-----------|------|---------------|
| Model profiles | `src/core/openrouter_model_profiles.json` | updated |
| Profile loader | `src/core/prompt_runtime.py` | updated |
| Sentence context | `src/core/context_builder.py` | **new** (Stage 4) |
| Stage-1 sweep | `scripts/sweeps/excel_ofat_stage1_models.sh` | **new** |
| Family Q rerun | `scripts/sweeps/excel_ofat_stage1_fixed_prompt.sh` | **new** |
| Family O top-2 | `scripts/sweeps/excel_ofat_prompt_O_top2.sh` | **new** |
| Pipeline resume | `scripts/sweeps/excel_ofat_resume_pipeline.sh` | **new** |
| Results aggregator | `scripts/evaluation/summarize_excel_ofat.py` | **new** |
| Improve pipeline | `scripts/evaluation/excel_ofat_improve_pipeline.py` | **new** (verify / min_gap / context) |
| Prompts N/O/P/Q | `src/prompts/N_*.txt`, `O_*.txt`, `P_*.txt`, `Q_*.txt` | **new** |
| Post-process | `src/postprocess/postprocess.py`, `discourse_filters.py` | updated / **new** |
| Verifier | `src/runners/run_two_stage_verify.py` | updated |
