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

- [ ] Gold labels: `data/processed/excel_prompting/*__gold_labels.csv`
- [ ] Manifest: `data/manifests/excel_prompting.json`
- [ ] `export OPENROUTER_API_KEY=...`
- [ ] Smoke: `--dry_run 4` on one free model

### Stage 1 — Model sweep (OFAT: model only)

```bash
bash scripts/sweeps/excel_ofat_stage1_models.sh
python scripts/evaluation/summarize_excel_ofat.py \
  --run_root outputs/runs/prompting/2026-06-14-excel-ofat-s1 \
  --out review/excel_ofat_stage1_summary.csv
```

Pick **top-2** by F3, then precision. Gate: F3 ≥ 0.76 or materially lower over-prediction.

### Stage 2 — Decoding (best model from Stage 1)

| ID | Variable |
|----|----------|
| 2-A | `temperature=0.2` |
| 2-B | `top_p=0.9`, `temperature=0` |
| 2-C | `presence_penalty=1.0` (if supported) |

### Stage 3 — Prompt wording

| ID | Family | Template |
|----|--------|----------|
| 3-A | N | rarity prior (~7% borders) |
| 3-B | O | German fairy few-shot |
| 3-C | P | anti-example |

### Stage 4 — Context window

Requires `--context_mode sentences`:

| ID | `--sentence_window` | `--sentence_stride` |
|----|--------------------:|--------------------:|
| 4-A | 64 | 48 |
| 4-B | 32 | 24 |
| 4-C | 16 | 8 |

Baseline token mode: `--context_mode tokens --context_size 409`.

### Stage 5 — Post-processing

```bash
python src/postprocess/run_postprocess.py \
  --cache outputs/runs/prompting/.../cache_<stem>.json \
  --scenario all --tolerances 0 1 3
```

New scenarios: `min_scene_len_2`, `_4`, `_6`, `n_per_k_15` (1 border per 15 sentences).

### Stage 6 — Two-pass verify (if F3 < 0.80)

```bash
python src/runners/run_two_stage_verify.py \
  --excel_manifest data/manifests/excel_prompting.json \
  --run_dir outputs/runs/prompting/<date>/full_<model>_familyB_reasoning-off \
  --verify_style yes_no --context_window 3 --dry_run
```

### Stage 7 — Discourse rules

Scenario `discourse_plus_min_scene_len_3` (spaCy `de_core_news_sm` or regex fallback).

### Stage 8 — Tiny LoRA (last resort)

See [`docs/planning/F3_IMPROVEMENT_PLAN.md`](F3_IMPROVEMENT_PLAN.md) — train on 316-sentence Excel corpus.

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

| Component | Path |
|-----------|------|
| Model profiles | `src/core/openrouter_model_profiles.json` |
| Profile loader | `src/core/prompt_runtime.py` |
| Sentence context | `src/core/context_builder.py` |
| Stage-1 sweep | `scripts/sweeps/excel_ofat_stage1_models.sh` |
| Results aggregator | `scripts/evaluation/summarize_excel_ofat.py` |
| Prompts N/O/P | `src/prompts/N_*.txt`, `O_*.txt`, `P_*.txt` |
| Post-process | `src/postprocess/postprocess.py`, `discourse_filters.py` |
| Verifier | `src/runners/run_two_stage_verify.py` |
