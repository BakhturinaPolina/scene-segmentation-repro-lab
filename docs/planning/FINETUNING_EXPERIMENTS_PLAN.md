# Fine-Tuning Experiments Plan (Hugging Face, minimal extra cost)

**Date:** 2026-06-09 (revised 4)
**Changelog:** Cloud-only Jobs default; Kaggle removed; Pilot 0 status; synced code gaps.
**Goal:** Reproduce and then improve the paper's fine-tuned Llama baseline for scene-boundary
detection, using Hugging Face Hub for data and artifacts, and close the fine-tuning reproducibility gap in
[`../reproducibility/REPRODUCIBILITY_GAP_REVIEW.md`](../reproducibility/REPRODUCIBILITY_GAP_REVIEW.md).

**Primary metric:** relaxed F1 at tolerance t=3 (the paper headline; see
[`../reference/2025.naacl-long.500.md`](../reference/2025.naacl-long.500.md) line 171), macro-averaged
over texts. Also track precision/recall at tolerance 0/1/3.

**Budget:** HF Pro ($9/month) + prepaid Jobs credits (~$34–45 for the full matrix). All GPU work runs
on HF Jobs (`COMPUTE=jobs`, default in `submit_job.sh`). Data build stays on local CPU (~10 min).

---

## 0. What costs money

| Item | Cost | Notes |
|------|------|-------|
| HF Pro | **$9/mo** | Private datasets + Jobs API |
| HF Jobs `t4-small` | **$0.40/hr** | 3B QLoRA (prepaid credits; not included in Pro) |
| HF Jobs `t4-medium` | **$0.60/hr** | 8B stretch (E8) |
| Private dataset + public adapters | **$0** | Within Pro quotas |

Add prepaid credits at [hf.co/settings/billing](https://huggingface.co/settings/billing) before submitting Jobs.

**Serial GPU estimate** (3B, 1 epoch, in-job eval; ±30% wall-clock):

| Phase | GPU-h | Est. cost |
|-------|-------|-----------|
| Pilot (E0 smoke + both folds) | ~7.5–10 h | ~$3–4 |
| Core matrix (~12 × 3B) | ~66–84 h | ~$26–34 |
| Stretch E8 (8B, `test_full`) | ~8–12 h | ~$5–7 |
| **Total** | **~82–106 h** | **~$34–45** |

Per 3B experiment: ~5.5–7 h (~$2.20–2.80). Use `FLAVOR=t4-small`, one experiment per submission,
`eval_limit` for E0 smoke.

---

## 1. What "fine-tuning" means here (plain language)

We take a small open chat model (e.g. Llama-3.2-3B) and teach it, from examples, to look at one
sentence in a German story (with a few sentences of context) and answer whether a NEW SCENE starts at
that sentence. We use **QLoRA** — freeze the base model, train tiny adapter layers only.

The paper's main lesson: **Llama fine-tuning only works when the task is framed as explicit
scene-change reasoning**, not simple True/False classification. No-CoT fine-tuning reaches 0.09 relaxed
F1 on Test-Full; CoT-List reaches 0.62 (paper best BERT: 0.68).

Example prompt/response:

```
... previous sentences ...
<sentence>the target sentence</sentence>
... following sentences ...
Question: does a new scene start at the target sentence? Answer with JSON.

→ a) there is a significant change in narrative action,
  b) there is no significant change in location,
  ...
  e) therefore, the sentence starts a new scene.
  {"label": "BORDER", "confidence": 0.9}
```

The JSON `{"label": "BORDER"}` object is our equivalent of the safer `Final label: BORDER` format.

---

## 2. Paper baseline and reference numbers

From [`../reference/2025.naacl-long.500.md`](../reference/2025.naacl-long.500.md) (sections 4.2, 6.3, 7.2,
appendix A.2/A.4):

| Item | Paper choice |
|------|--------------|
| Base model | `unsloth/llama-3-8b-Instruct-bnb-4bit` (4-bit) |
| Method | QLoRA via Unsloth; LoRA r=16, alpha=16, dropout=0, standard 7 target modules |
| Training data | **Train-Full** = 32 texts (Table 6); per-sentence samples |
| Context | surrounding text up to **512 tokens total**, balanced by sentence count, `<sentence>` markup |
| Class balance | keep **all BORDER** + **10% of NOBORDER** (training only); eval uses every sentence |
| Target format | **No-CoT** ("True/False, because...") vs **CoT-List** ("a)..e)..") |
| Scoring | relaxed F1, t=3, averaged per text |
| Result (Test-Full) | **No-CoT = 0.09**, **CoT-List = 0.62**; on STSS-Test-2 CoT-List = **0.63** |
| Not reported | learning rate, epochs, batch size, hardware (we choose our own; see defaults below) |

Reference numbers to beat / approach:

| System | F1@3 (STSS-Test-2) | F1@3 (Test-Full) | Source |
|--------|--------------------|--------------------|--------|
| Paper Llama3:8b CoT-List (fine-tuned) | 0.63 | 0.62 | Table 3 |
| Paper GBERT-Large + Half-Stride (best supervised) | 0.66 | 0.68 | Table 1 |
| Paper GPT-4o zero-shot prompting | - | 0.45 | Table 2 |
| Our prompting, true natural distribution + post-processing (partial) | ~0.51 | - | `../../research_log/experiments/experiment__improvement__f3-precision-campaign.md` |

Our prompting peaked at F1@3 = 0.83 on a **stratified** sample, but that number is inflated by 50/50
class balancing (see [`PROGRESS_REPORT.md`](PROGRESS_REPORT.md) lines 68-95). On the real ~4%-border
distribution, prompting is closer to ~0.5. Fine-tuning targets the 0.55–0.63 range.

---

## 3. Splits, data, and usage policy

Split membership from paper Table 6:
[`../../data/manifests/finetune_splits.json`](../../data/manifests/finetune_splits.json):

| Split | Texts | Role |
|-------|-------|------|
| `train_full` | 32 | Training set (main train split) |
| `train_with_high` | 25 | Smaller train split (ablation) |
| `stss_train` | 20 | Smallest train split (ablation) |
| `stss_test_2` | 2 (Aus guter Familie, Effi Briest) | **Main eval** (high literature; locally available) |
| `stss_test_1` | 4 | Dime-novel test |
| `ood_test` | 3 | Out-of-distribution test (Harry Potter, fairy tale) |
| `test_full` | 9 | All test sets combined (paper headline) |

**Assumption:** full 41-text corpus on disk as `"<Text Name>.xmi.zip"` under
[`../../upstream/scene-segmentation/data/full/`](../../upstream/scene-segmentation/data/full).
Builder discovers zips recursively and matches by file name; missing texts are skipped (partial start OK).

### Scenes vs segments (data caveat)

Our XMI parser extracts only `Szene Ebene 1` elements, so gold BORDER = first sentence of each **scene**.
The paper also treats **non-scenes** as segments. STSS-Test-2: 317 scene borders vs 446 segment borders.
Whether to label non-scene starts as borders is an open decision (needs a decision note if changed).
Current scene-only definition matches our prompting baselines, so comparisons stay fair.

### What we have today

| Manifest | Files | Format | Source |
|----------|-------|--------|--------|
| [`stss_test_2.json`](../../data/manifests/stss_test_2.json) | Aus guter Familie, Effi Briest | `.xmi.zip` (gold scene annotations) | LSX-UniWue scene-segmentation |
| [`excel_prompting.json`](../../data/manifests/excel_prompting.json) | Gänsemagd, Kleist | `.txt` (sentence-level prompting) | LSX-UniWue scene-segmentation |

**Enough for pipeline debugging only** — not paper-comparable fine-tuning. The paper uses 41 texts,
one sample per sentence, all BORDER kept, 10% NOBORDER retained.

| Goal | Valid with current data? |
|------|--------------------------|
| Pipeline debug, prompt testing, tiny sanity eval, E0 smoke/overfit test | Yes — tag runs **`debug`** |
| Reported performance, paper comparison, generalization claims | **No** |

**Hard rules:**

- **STSS-Test-2 is a test set** — never train on it for paper-comparable runs.
- **Folds mode** (`fold_A` / `fold_B` in [`build_sft_dataset.py`](../../src/finetune/build_sft_dataset.py)):
  trains on one STSS novel, evals on the other — **debugging only**; never quote scores as performance.
- **Excel prompting texts** (Gänsemagd, Kleist): qualitative prompt-debugging only, not training data.

### Current stage (2026-06): STSS-Test-2 only

**Active scope:** both novels in [`stss_test_2.json`](../../data/manifests/stss_test_2.json) — *Aus guter Familie*,
*Effi Briest* — under `upstream/scene-segmentation/data/full/stss_test_2/`.

| Setting | Value |
|---------|-------|
| `DATA_SCOPE` | `stss_test_2` (default in `submit_job.sh`; `pilot` is an alias) |
| Build | `--mode folds --fold both --stss_only --context_mode tokens512 --negative_mode paper10pct` |
| Jobs | `fold_A`, `fold_B` (leave-one-novel-out) |
| Tag | **`debug`** on all runs; do not report F1 as model performance |
| E1+ gate | Full 41-text corpus on disk **and** Pilot 0 complete |

**Stage workflow:**

1. Build + verify folds data (Step 1 below, folds command).
2. E0 smoke (`stss_test_2/E0_smoke.json`, `fold_A`, `eval_limit=200`).
3. E0 full (`stss_test_2/E0_full.json`, both folds, full eval).
4. Factor sweeps (E3/E4/E5): same `DATA_SCOPE=stss_test_2`, change `BUILD_ARGS` one factor at a time.
5. When corpus arrives: switch to `DATA_SCOPE=corpus` for E1 anchor.

Decision note: [`decision__finetune-stss-test-2-stage.md`](../../research_log/decisions/decision__finetune-stss-test-2-stage.md).

### Pilot 0 — required gate before E1+

Do **not** start serious fine-tuning until Pilot 0 passes. E1+ requires full 41-text corpus on disk **and**
a completed Pilot 0 report.

| Stage | What | Key checks |
|-------|------|------------|
| **1 — Prompting** | All 4 texts (2 XMI + 2 Excel) | % parseable outputs, valid final label, malformed count, CoT fields a–e present |
| **2 — Tiny eval** | 2 XMI files only | strict F1 (t=0), relaxed F1 (t=1, t=3), P/R, predicted vs gold border counts |
| **3 — Smoke train** | E0 folds (one novel → other) | Code runs; **do not interpret scores** (text-specific overfitting) |

**Deliverable:** short report covering parseability, border counts, P/R/F1 on 2 XMI files, manual
inspection of 20 FP + 20 FN, and comparison of No-CoT vs CoT-List vs stricter final-label format.

**Status (2026-06-09):** Pilot 0 **not complete** — E1+ remains gated.

| Stage | Status | Evidence |
|-------|--------|----------|
| **Prereq — folds data build** | Not done | No `data/processed/finetune/*/verification.json` logged |
| **1 — Prompting (4 texts)** | Partial | JSON-schema runs: Excel [`2026-05-30__excel-*`](../../research_log/runs/2026-05-30__prompting__experiment__excel-controlled-postprocessing-sweep.md); XMI stratified [`2026-05-15/16 stss2`](../../research_log/runs/2026-05-15__prompting__experiment__stss2-phase-a-family-sweep-nemotron.md). Missing: cot_list a–e checks, format comparison, unified 4-text report |
| **2 — Tiny eval (natural distribution)** | Partial | [`2026-06-06 nemotron-full-eval-stss2`](../../research_log/runs/2026-06-06__prompting__baseline__nemotron-full-eval-stss2.md): ~16% of Aus guter Familie; Effi Briest not started; blocked by [OpenRouter limit](../../research_log/issues/issue__api__openrouter-free-daily-limit.md) |
| **3 — E0 smoke train** | Not done | [`train_results.json`](../../train_results.json): prior `SFTConfig` error; fixed in [`train_job.py`](../../src/finetune/hf_jobs/train_job.py) but not re-run |
| **Deliverable report** | Not done | No consolidated Pilot 0 note |

---

## 4. Tools and code gaps

| File | What it does |
|------|--------------|
| [`../../src/finetune/build_sft_dataset.py`](../../src/finetune/build_sft_dataset.py) | Turns gold XMI/Excel into `train.jsonl` + `eval.jsonl` per job, plus `verification.json`. |
| [`../../src/finetune/hf_jobs/train_job.py`](../../src/finetune/hf_jobs/train_job.py) | Train + eval script (HF Jobs via UV). |
| [`../../src/finetune/hf_jobs/submit_job.sh`](../../src/finetune/hf_jobs/submit_job.sh) | Builds data, uploads private HF dataset, submits Jobs (`COMPUTE=jobs` default). |
| [`../../src/finetune/hf_jobs/configs/`](../../src/finetune/hf_jobs/configs/) | Per-experiment JSON configs (`E0_smoke`, `E0_pilot_full`, `E1_anchor`, …). |
| [`../../requirements-finetune.txt`](../../requirements-finetune.txt) | Pinned fine-tuning deps (CUDA torch installed separately). |
| [`../../src/finetune/eval_finetuned.py`](../../src/finetune/eval_finetuned.py) | Standalone re-eval of an adapter (e.g. after train-only cloud run). |

**Training defaults** (E0/E1 configs): `batch_size=1`, `grad_accum=8`, `eval_batch_size=8` (Jobs `t4-small`).

Key builder options (one factor each):
- `--target_format {cot_list,json,no_cot}` — assistant answer style (all end with a JSON label).
- `--negative_mode {ratio,paper10pct,hard,pct}` — how NOBORDER training rows are chosen.
- `--context_mode {sentences,tokens512}` with `--context N` / `--token_budget 512`.
- `--train_split` / `--eval_split` (corpus mode), `--fold` (folds mode).
- `--val_fraction 0.1` — validation holdout for E10.

### Code gaps

| Gap | Blocks | Priority | Status |
|-----|--------|----------|--------|
| E1b contrast config (`completion_only_loss: false` on E1) | E1b | **Highest** | **Done** — see `E1_anchor.json` vs `E1b_completion_only.json` |
| Completion-only loss mechanism | E1b | **Highest** | **Done** — `train_on_responses_only()` in `train_job.py` |
| Percentage negative sweep automation | E4 | High | **Partial** — `scripts/sweeps/e4_negative_sweep.sh`; manual `pct` works |
| Near-border hard negatives | E4 | High | **Done** — `--negative_mode hard --hard_window 3` |
| `max_seq_len` ↔ `--token_budget` coupling | E5 | Medium | **Done** — `meta.json` + `recommended_max_seq_len` |
| Cluster-merge post-processing | E7 | Medium | **Done** — `postprocess.py` + in-job eval |
| Val split + eval-during-training + early stop | E10 | Medium | **Partial** — callback + config; needs `--val_fraction` at build |
| Two-stage verifier on finetune eval | E8 | Stretch | **Partial** — `run_two_stage_verify.py` not wired to finetune output |
| 4-way boundary-type labels | E9 | Stretch | **Code TODO (deferred)** — [`decision__finetune-four-way-labels.md`](../../research_log/decisions/decision__finetune-four-way-labels.md) |

---

## 5. Step-by-step

### Step 0 — One-time setup (~15 min)

1. HF Pro account active; `hf auth login` with a **write** token.
2. Locally: `pip install huggingface_hub unsloth trl` (or use project venv).
3. Set `export HF_USER=RuthonField` (or your username).
4. Add ~$35–45 prepaid credits at [hf.co/settings/billing](https://huggingface.co/settings/billing).

Verify: `hf auth whoami` prints your username without error.

### Step 1 — Pilot 0: build data and verify pipeline (~10 min, no GPU)

Folds mode (**current stage — STSS-Test-2 only**):

```bash
source .venv/bin/activate
python src/finetune/build_sft_dataset.py --mode folds --fold both --stss_only \
  --target_format cot_list --negative_mode paper10pct --context_mode tokens512
```

Corpus mode (paper-comparable; **after full corpus on disk**):

```bash
python src/finetune/build_sft_dataset.py --mode corpus \
  --train_split train_full --eval_split stss_test_2 \
  --target_format cot_list --negative_mode paper10pct
```

Expect: per-job `train=... eval=...`, then `[verify] OK` with sentence/border counts matching manifest
(`MISMATCH` = fix before training). Outputs in `data/processed/finetune/<job>/` + `verification.json`.
Complete Pilot 0 Stages 1–2 before Step 2.

### Step 2 — E0 smoke + full folds (HF Jobs; STSS-Test-2 stage)

```bash
# Smoke (fold_A, 200 eval rows)
HF_USER=RuthonField DATA_SCOPE=stss_test_2 \
  RUN_CONFIG=src/finetune/hf_jobs/configs/stss_test_2/E0_smoke.json \
  COMPUTE=jobs FLAVOR=t4-small TIMEOUT=2h \
  bash src/finetune/hf_jobs/submit_job.sh

# Full LOO folds (both directions, full eval)
HF_USER=RuthonField DATA_SCOPE=stss_test_2 \
  RUN_CONFIG=src/finetune/hf_jobs/configs/stss_test_2/E0_full.json \
  COMPUTE=jobs FLAVOR=t4-small TIMEOUT=8h BUILD_MODE=skip \
  bash src/finetune/hf_jobs/submit_job.sh
```

(`BUILD_MODE=skip` reuses Step 1 data.) Expect adapters at
`https://huggingface.co/$HF_USER/scene-seg-llama-3-2-3b-instruct-fold_{A,B}` + `metrics_*.json`.
Tag run notes **`debug`** — LOO fold scores are not reportable performance.

### Step 3 — Experiment matrix (one factor at a time)

**Gate:** E1+ only after full 41-text corpus verified **and** STSS-Test-2 stage complete.

Fixed controls unless a row changes them: train = `train_full`, eval = `stss_test_2`, seed 1337,
LoRA r=16/alpha=16, 1 epoch, LR 2e-4, target = `cot_list`, context = 4 sentences each side,
negatives = `paper10pct`.

**Recommended order:** E1 → E1b → E4 → E5 → E3 → E9 (stretch) → E2. Highest-priority improvements after
baseline repro: completion-only loss, hard near-border negatives, longer context, JSON final labels.

| Exp | Factor under test | How | Status | Why |
|-----|-------------------|-----|--------|-----|
| **E0** | pipeline smoke | folds mode, `E0_smoke.json` | Supported | Pilot 0 Stage 3; debugging only |
| **E1** | anchor baseline | `E1_anchor.json`, corpus, CoT-List, paper10pct, tokens512 | Supported | Paper-comparable anchor all later runs beat |
| **E1b** | completion-only loss | `E1b_completion_only.json` vs E1 (`completion_only_loss: false`) | Supported | One-factor ablation via config flag |
| **E2** | base model family | swap `models` in config | Supported | Format / class balance may matter more than size |
| **E3** | target format | `E3_json.json` / `E3_no_cot.json` + `--target_format` rebuild | Supported | Paper: biggest single factor (0.62 vs 0.09) |
| **E4** | negative sampling | `E4_*.json` + `--negative_mode hard\|pct`; `e4_negative_sweep.sh` | Partial | Hard mode done; sweep script added |
| **E5** | context length | `E5_budget*.json` + `--token_budget {768…2048}`; `e5_context_sweep.sh` | Partial | Coupling done; sweep configs added |
| **E6** | capacity | `E6_epochs2.json`, `E6_lora32.json` | Supported | Cheap probe for more learning |
| **E7** | post-processing | in-job `min_scene_len_3`, `confidence+minlen`, cluster-merge | Supported | All scenarios scored in metrics |
| **E8** | stretch repro | `E8_8b_test_full.json`; `FLAVOR=t4-medium` | Partial | 8B + test_full runnable; verifier not wired |
| **E9** | scene/non-scene types | 4-way labels; collapse to binary for eval | Code TODO (deferred) | Blocked by four-way-labels decision |
| **E10** | validation selection | `E10_validation.json` + `--val_fraction 0.1` | Partial | Callback done; val split at build time |

**E2 model candidates:** `unsloth/Llama-3.2-3B-Instruct` (default), `unsloth/Meta-Llama-3.1-8B-Instruct-bnb-4bit`
(E8), Qwen2.5-7B / Qwen3-8B, Mistral-7B-v0.3. German encoder (GBERT) tracked separately.

**E4 tuning rules:** too many predicted borders → increase negative fraction or `hard` mode; missed borders →
decrease fraction or oversample hard positives.

**Commands:**

```bash
# E1 anchor (paper-comparable)
HF_USER=RuthonField DATA_SCOPE=corpus COMPUTE=jobs FLAVOR=t4-small TIMEOUT=8h \
  RUN_CONFIG=src/finetune/hf_jobs/configs/E1_anchor.json \
  bash src/finetune/hf_jobs/submit_job.sh

# E10 validation (requires val split at build)
HF_USER=RuthonField DATA_SCOPE=corpus COMPUTE=jobs FLAVOR=t4-small TIMEOUT=8h \
  BUILD_ARGS="--val_fraction 0.1" \
  RUN_CONFIG=src/finetune/hf_jobs/configs/E10_validation.json \
  bash src/finetune/hf_jobs/submit_job.sh

# E8 stretch (8B, test_full eval)
HF_USER=RuthonField DATA_SCOPE=corpus COMPUTE=jobs FLAVOR=t4-medium TIMEOUT=12h \
  BUILD_ARGS="--eval_split test_full" JOBS=train_full__to__test_full \
  RUN_CONFIG=src/finetune/hf_jobs/configs/E8_8b_test_full.json \
  bash src/finetune/hf_jobs/submit_job.sh
```

Data-side factors (E3/E4/E5/E9): rerun `build_sft_dataset.py`, then `submit_job.sh`.
Training-side factors (E1b/E2/E6/E10): edit config and/or `train_job.py`.

Compare `scenarios.none.tol_3.macro_f1` (raw) and post-processed variants against E1. Always report P/R
alongside F1, especially for E4.

### Success criteria

- **Pilot 0:** parseability > 95%; expected I/O structure; manual FP/FN inspection complete.
- **Must (E1+):** beat prompting natural-distribution baseline (F1@3 ~ 0.51 post-processed).
- **Target:** F1@3 >= 0.55 on STSS-Test-2 with a 3B model.
- **Stretch:** paper's 0.62–0.63 range.

---

## 6. Time estimate

| Phase | Work | Wall-clock (serial Jobs) | Cost |
|-------|------|--------------------------|------|
| Setup (Step 0) | HF auth + prepaid credits | ~15 min | $9/mo Pro + credits |
| Pilot 0 Stages 1–2 | prompting + tiny eval (API-bound) | ~1–2 days | ~$0 GPU |
| Step 1 data build | local CPU | ~10 min/factor | $0 |
| E0 smoke (Stage 3) | 1 × t4-small job | ~1–1.5 h | ~$0.40–0.60 |
| E0 full folds | 2 jobs | ~6.5–8.5 h | ~$2.60–3.40 |
| Per 3B experiment (E1+) | train + in-job eval | ~5.5–7 h each | ~$2.20–2.80 each |
| Core matrix (~12 runs) | serial Jobs | ~66–84 h (~3–4 days 24/7) | ~$26–34 |
| Stretch E8–E9 | 8B GPU + E9 blocked | ~8–12 h GPU + data work | ~$5–7 |

Serial cloud is the default. Parallel Jobs submissions reduce wall-clock but not credit spend.

---

## 7. Logging (per [`../../rule.md`](../../rule.md))

- Experiment note:
  [`../../research_log/experiments/experiment__finetune__hf-jobs-qlora-campaign.md`](../../research_log/experiments/experiment__finetune__hf-jobs-qlora-campaign.md).
- One run note per submission in `research_log/runs/`; record config, Job URL (if cloud), adapter repo,
  and `metrics_*.json` numbers.
- **Pilot 0 / E0 / folds-mode runs:** tag `debug`; never quote F1 as model performance.
- Artifact note for each adapter + metrics file in `research_log/artifacts/`.
- Decision note for compute platform:
  [`../../research_log/decisions/decision__finetune-compute-hf-jobs.md`](../../research_log/decisions/decision__finetune-compute-hf-jobs.md)
  (supersedes [`decision__finetune-compute-hf-local.md`](../../research_log/decisions/decision__finetune-compute-hf-local.md)).
- Decision note required before E9 (scene/non-scene label definition change).
