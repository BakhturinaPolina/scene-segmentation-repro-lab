# Fine-Tuning Experiments Plan (Hugging Face, minimal extra cost)

**Date:** 2026-06-09 (revised 2)
**Changelog:** Added data-usage policy for locally available data (Pilot 0 gate), integrated 10
paper-derived improvement suggestions into the experiment matrix, and flagged code gaps as TODOs.
**Goal:** Reproduce and then improve the paper's fine-tuned Llama baseline for scene-boundary
detection, using Hugging Face Hub for data and artifacts, and close the fine-tuning reproducibility gap in
[`../reproducibility/REPRODUCIBILITY_GAP_REVIEW.md`](../reproducibility/REPRODUCIBILITY_GAP_REVIEW.md).

**Primary metric:** relaxed F1 at tolerance t=3 (the paper headline; see
[`../reference/2025.naacl-long.500.md`](../reference/2025.naacl-long.500.md) line 171), macro-averaged
over texts. We also track precision/recall at tolerance 0/1/3.

**Budget:** HF Pro ($9/month). GPU compute defaults to **your local RTX 2070 (8 GB)** — no extra charge.
Optional HF Jobs cloud GPUs use **prepaid credits** (not included in Pro); use only when local VRAM is
insufficient (e.g. 8B repro).

---

## 0. What costs money (and what does not)

| Item | Cost | Notes |
|------|------|-------|
| HF Pro subscription | **$9/mo** | Required for private datasets + Jobs API access |
| Private dataset storage (`scene-seg-sft`) | **$0** | Within Pro's 1 TB private quota |
| Public adapter repos (`scene-seg-*`) | **$0** | Unlimited public model repos |
| **Local train + eval** (default) | **$0** | RTX 2070 8 GB; slower but free |
| **HF Jobs** (`t4-small`) | **~$0.50–0.75/hr** | Prepaid credits only — Pro does **not** include GPU time |
| Inference Provider credits | N/A | Included in Pro; not used for fine-tuning |

**Cheapest full campaign (recommended):** run everything locally with `COMPUTE=local` in
`submit_job.sh`. Total extra cost beyond Pro: **$0**.

**When to use HF Jobs:** only if local 8 GB VRAM fails (8B model, OOM) or you want faster wall-clock
and are willing to add ~$10–15 prepaid credits at
[hf.co/settings/billing](https://huggingface.co/settings/billing).

**Cost-saving tactics if you use Jobs:**

1. Always `FLAVOR=t4-small` (cheapest GPU).
2. One experiment per submission (serial).
3. Use `eval_limit` for smoke (E0); full eval only on anchor runs.
4. Set `eval_after_train: false` in config, then re-eval locally with `eval_finetuned.py` (saves ~50%
   of cloud GPU time).

### Cloud cost estimates (HF Jobs, if you do NOT train locally)

Official Jobs/Spaces GPU list price: **Nvidia T4-small = $0.40/hr** ([HF pricing](https://huggingface.co/pricing)).
Estimates below use `FLAVOR=t4-small`, Llama-3.2-3B QLoRA, 1 epoch, in-job eval. Actual wall-clock
varies ±30%.

#### Phase A — Pilot / debugging (`DATA_SCOPE=pilot`, STSS-Test-2 only)

Uses [`stss_test_2.json`](../../data/manifests/stss_test_2.json) (2 XMI novels) + Excel prompting
texts in folds mode. **Not paper-comparable** — tag all run notes `debug`.

| Run | Config | Train rows | Eval rows | Est. GPU-h | Est. cost @ $0.40/hr |
|-----|--------|------------|-----------|------------|----------------------|
| E0 smoke | `E0_smoke.json` | 684 | 200 (limit) | ~1.0–1.5 h | **~$0.40–0.60** |
| E0 full fold_A | `E0_pilot_full.json` (one job) | 684 | 5,906 | ~3.5–4.5 h | **~$1.40–1.80** |
| E0 full fold_B | same (one job) | 796 | 5,025 | ~3.0–4.0 h | **~$1.20–1.60** |
| Both folds (2 jobs) | `E0_pilot_full.json` | — | — | ~6.5–8.5 h | **~$2.60–3.40** |

**Pilot cloud subtotal (recommended):** E0 smoke + both folds ≈ **$3–4** prepaid credits.

#### Phase B — Paper-comparable (`DATA_SCOPE=corpus`, full `data/` corpus)

Requires all 41 texts as `*.xmi.zip` under `upstream/scene-segmentation/data/full/`.
Train = `train_full` (32 texts), eval = `stss_test_2` (2 texts).

| Quantity | Value |
|----------|-------|
| Est. train rows (`paper10pct`) | **~8,503** (1,574 borders + 10% of 69,291 NOBORDER) |
| Eval rows (STSS-Test-2, full) | **10,931** sentences |
| Eval rows (`test_full`, stretch E8) | **21,164** sentences |

| Run type | Est. GPU-h per 3B experiment | Est. cost @ $0.40/hr |
|----------|------------------------------|----------------------|
| E1 anchor (train + full STSS-Test-2 eval) | ~5.5–7 h | **~$2.20–2.80** |
| E1 + `test_full` eval (stretch) | ~8–10 h | **~$3.20–4.00** |
| E8 paper 8B repro (`t4-medium` @ $0.60/hr) | ~8–12 h | **~$4.80–7.20** |

**Core matrix (E1, E1b, E2×2, E3×2, E4×2, E5, E6×2, E7, E10) ≈ 12 runs:**

| Scenario | GPU-h | Prepaid credits |
|----------|-------|-----------------|
| Serial 3B runs on `stss_test_2` eval | ~66–84 h | **~$26–34** |
| + stretch E8 (8B) | +8–12 h | **+$5–7** |
| **Total cloud (no local GPU)** | ~74–96 h | **~$30–42** |

Add **~$3–4** if you also run the pilot phase on Jobs before the corpus arrives.

**Cheapest cloud workflow:** train on Jobs (`eval_after_train: false`, ~2 h, ~$0.80/run) + eval
locally with `eval_finetuned.py` — cuts per-run cost roughly in half (~**$15–20** for the core matrix).

---

## 1. What "fine-tuning" means here (plain language)

We take a small open chat model (for example Llama-3.2-3B) and teach it, from examples, to look at one
sentence in a German story (with a few sentences of context around it) and answer whether a NEW SCENE
starts at that sentence. We do not retrain the whole model: we use **QLoRA**, which freezes the big
model and only trains tiny "adapter" layers.

The paper's main lesson: **Llama fine-tuning only works well when the task is framed as explicit
scene-change reasoning**, not as a simple True/False classification. No-CoT fine-tuning performs very
badly on Test-Full (0.09 relaxed F1), while CoT-List reaches 0.62, close to the best BERT model at
0.68.

For each sentence the model sees a prompt like:

```
... previous sentences ...
<sentence>the target sentence</sentence>
... following sentences ...
Question: does a new scene start at the target sentence? Answer with JSON.
```

and learns to answer with a structured rationale plus a machine-readable label, e.g.:

```
a) there is a significant change in narrative action,
b) there is no significant change in location,
c) there is a significant change in time,
d) there is no significant change in the character constellation,
e) therefore, the sentence starts a new scene.
{"label": "BORDER", "confidence": 0.9}
```

The JSON `{"label": "BORDER"}` object is our equivalent of the safer `Final label: BORDER` format
(suggested improvement over free-text regex extraction).

---

## 2. The paper's flow, documented as our baseline

From [`../reference/2025.naacl-long.500.md`](../reference/2025.naacl-long.500.md) (sections 4.2, 6.3, 7.2,
appendix A.2/A.4):

| Item | Paper choice |
|------|--------------|
| Base model | `unsloth/llama-3-8b-Instruct-bnb-4bit` (4-bit) |
| Method | QLoRA via Unsloth; LoRA r=16, alpha=16, dropout=0, standard 7 target modules |
| Training data | **Train-Full** = 32 texts (Table 6); per-sentence samples |
| Context | surrounding text up to **512 tokens total**, balanced by sentence count, `<sentence>` markup |
| Class balance | keep **all BORDER** + **10% of NOBORDER** (training only); eval uses every sentence |
| Target format | two variants: **No-CoT** ("True/False, because...") vs **CoT-List** ("a)..e)..") |
| Scoring | relaxed F1, t=3 (snap a prediction to a gold border if within 3 sentences), averaged per text |
| Result (Test-Full) | **No-CoT = 0.09**, **CoT-List = 0.62** relaxed F1; on STSS-Test-2 CoT-List = **0.63** |
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
distribution, prompting is closer to ~0.5. Fine-tuning is how we aim for the 0.55-0.63 range.

---

## 3. Splits and the data we assume

Split membership comes from paper Table 6 and is encoded in
[`../../data/manifests/finetune_splits.json`](../../data/manifests/finetune_splits.json):

| Split | Texts | Role |
|-------|-------|------|
| `train_full` | 32 | Training set (our main train split) |
| `train_with_high` | 25 | Smaller train split (ablation) |
| `stss_train` | 20 | Smallest train split (ablation) |
| `stss_test_2` | 2 (Aus guter Familie, Effi Briest) | **Our main eval** (high literature; locally available) |
| `stss_test_1` | 4 | Dime-novel test |
| `ood_test` | 3 | Out-of-distribution test (Harry Potter, fairy tale) |
| `test_full` | 9 | All test sets combined (paper headline) |

**Assumption:** the full 41-text corpus is on disk in the same `"<Text Name>.xmi.zip"` format as the
two STSS-Test-2 novels already under
[`../../upstream/scene-segmentation/data/full/stss_test_2/`](../../upstream/scene-segmentation/data/full).
The data builder discovers zips recursively under `--corpus_dir` and matches them to split members by
file name. Texts that are not on disk are reported and skipped (so you can start partial).

### Important data caveat (scenes vs segments)

Our XMI parser extracts only `Szene Ebene 1` elements, so a gold BORDER = the first sentence of each
**scene**. The paper also treats **non-scenes** as segments. So for STSS-Test-2 we get 145 + 172 = 317
scene borders, whereas counting non-scenes too would give 219 + 227 = 446 segment borders. The
verification step reports both numbers. Whether to also label non-scene starts as borders is an open
data-conversion decision; if we change it, that needs a decision note. The numbers in this plan use the
current scene-only definition (which all our prompting baselines also use, so comparisons stay fair).

---

## 4. Data-usage policy for currently available data

### What we have today

| Manifest | Files | Format | Source |
|----------|-------|--------|--------|
| [`stss_test_2.json`](../../data/manifests/stss_test_2.json) | Aus guter Familie, Effi Briest | `.xmi.zip` (gold scene annotations) | LSX-UniWue scene-segmentation |
| [`excel_prompting.json`](../../data/manifests/excel_prompting.json) | Gänsemagd, Kleist | `.txt` (sentence-level prompting) | LSX-UniWue scene-segmentation |

**Answer:** Yes, this is enough for **initial testing only** — not for real Llama fine-tuning results or
paper comparison. The paper uses an extended dataset of **41 texts or text fragments**, split into
training and test subsets, with one training sample per sentence, all `BORDER` examples kept, and only
10% of `NOBORDER` examples retained because the task is highly imbalanced.

### Valid uses vs invalid uses

| Goal | Use current data? | Valid? |
|------|------------------:|--------|
| Pipeline debugging (XMI loading, sample generation) | Yes | Valid |
| Prompt testing (CoT-List vs No-CoT, parseability) | Yes | Valid |
| Tiny sanity evaluation on the two XMI novels | Yes | Valid |
| Fine-tuning smoke test / overfitting test | Yes, mark as **debugging** | Valid only as debugging |
| Reported model performance | No | Not valid |
| Comparison with the paper | No | Not valid |
| Meaningful fine-tuning / generalization estimates | No | Not valid |
| Claiming one prompt or model is better | No | Not valid |

### Hard rule: STSS-Test-2 is a test set

In the paper, **STSS-Test-2 is a test set**, not training data. It consists of high-literature texts
used to test generalization. Training on it would invalidate later paper comparison.

Folds mode in [`build_sft_dataset.py`](../../src/finetune/build_sft_dataset.py) (`fold_A` / `fold_B`)
trains on one STSS novel and evaluates on the other. This is **debugging-only**: any run note using
folds mode must be tagged `debug`, and its scores must **never** be quoted as model performance.

The Excel prompting texts (Gänsemagd, Kleist) are **qualitative prompt-debugging material**, not
training data for paper-comparable runs.

### What current data can and cannot answer

**Good for:**

- Can I reconstruct sentence-level samples?
- Can I mark the target sentence correctly?
- Can I generate CoT-List prompts?
- Can I parse the model output?
- Can I compute relaxed F1?
- Does my code handle XMI files correctly?
- Does the model predict almost every sentence as BORDER?
- Does the model produce too many false positives around dialogue, time jumps, or character changes?

**Not good for:**

- Does Llama fine-tuning work?
- Is my model better than the paper?
- Is CoT-List generally better than No-CoT?
- How much training data is enough?
- Does the model generalize across literary types?

### Pilot 0 — three-stage gate (required before E1+)

Do **not** start serious fine-tuning until Pilot 0 passes. Real experiments (E1+) require the full
41-text corpus on disk **and** a completed Pilot 0 report.

#### Stage 1: Prompting pipeline test

Use all four texts: Aus guter Familie, Effi Briest, Gänsemagd, Kleist.

Generate prompts around each candidate sentence and test whether the model gives parseable answers.
Main metrics (not F1 yet):

- % parseable outputs
- % outputs with valid final label
- number of malformed generations
- whether CoT fields (a–e) are present

This tests whether the prompt format is technically stable.

#### Stage 2: Tiny evaluation on the two XMI files

Use only Aus guter Familie and Effi Briest (gold scene annotations). Run zero-shot or prompted Llama
and compute:

- strict F1 (t=0)
- relaxed F1 at t=1 and t=3
- precision and recall (report separately, not only F1)
- number of predicted borders vs gold borders

Already produced by [`train_job.py`](../../src/finetune/hf_jobs/train_job.py) and
[`eval_finetuned.py`](../../src/finetune/eval_finetuned.py). The paper argues exact F1 is too strict
and uses relaxed F1 with tolerance t=3.

#### Stage 3: Fine-tuning smoke test only

Fine-tune on one XMI novel, test on the other — only to verify training code runs:

```text
Train: Aus guter Familie  →  Test: Effi Briest   (fold_A)
Train: Effi Briest        →  Test: Aus guter Familie (fold_B)
```

This is E0. **Do not interpret the score as meaningful.** With only two texts, results mostly reflect
text-specific overfitting.

#### Pilot 0 deliverable

Produce a short report:

```text
Pilot 0: Data and Prompting Sanity Check

Data:
- 2 annotated STSS-Test-2 XMI files
- 2 sentence-level prompting TXT files

Experiments:
1. No-CoT prompting
2. CoT-List prompting
3. CoT-List with stricter final label format

Evaluation:
- parseability
- number of predicted borders
- precision / recall / relaxed F1 on the two XMI files
- manual inspection of 20 false positives and 20 false negatives
```

Most useful next step after Pilot 0: implement the evaluation pipeline on `stss_test_2` and treat the
Excel prompting files as qualitative prompt-debugging material only.

---

## 5. The tools you will run

| File | What it does |
|------|--------------|
| [`../../src/finetune/build_sft_dataset.py`](../../src/finetune/build_sft_dataset.py) | Turns gold XMI/Excel into `train.jsonl` + `eval.jsonl` per job, plus `verification.json`. |
| [`../../src/finetune/hf_jobs/train_job.py`](../../src/finetune/hf_jobs/train_job.py) | Train + eval script (local GPU or HF Jobs via UV). |
| [`../../src/finetune/hf_jobs/submit_job.sh`](../../src/finetune/hf_jobs/submit_job.sh) | Builds data, uploads private HF dataset, runs locally or submits Jobs. `DATA_SCOPE=pilot` (default) or `corpus`. |
| [`../../src/finetune/hf_jobs/configs/`](../../src/finetune/hf_jobs/configs/) | Per-experiment JSON configs (`E0_smoke`, `E0_pilot_full`, `E1_anchor`, …). |
| [`../../requirements-finetune.txt`](../../requirements-finetune.txt) | Pinned fine-tuning deps (CUDA torch installed separately). |
| [`../../src/finetune/eval_finetuned.py`](../../src/finetune/eval_finetuned.py) | Standalone re-eval of an adapter (e.g. after train-only cloud run). |

**Local 8 GB defaults** (auto-applied in E0 config; use for all local runs if you hit OOM):

- `batch_size=1`, `grad_accum=8`
- `eval_batch_size=8`

Key builder options (one factor each):
- `--target_format {cot_list,json,no_cot}` — assistant answer style (all end with a JSON label).
- `--negative_mode {ratio,paper10pct,hard}` — how NOBORDER training rows are chosen.
- `--context_mode {sentences,tokens512}` with `--context N` / `--token_budget 512`.
- `--train_split` / `--eval_split` (corpus mode), `--fold` (folds mode).

### Code gaps (TODO before the corresponding experiment)

| Gap | Blocks | Priority |
|-----|--------|----------|
| Completion-only loss (mask prompt tokens; train assistant turn only) | E1b | **Highest** |
| Percentage-based negative sweep (`5% / 10% / 20% / 30% / 50%` of NOBORDER) | E4 extended | High |
| Near-border rule: keep all NOBORDER within ±1..3 of a border, then top up randomly | E4 hard variant | High |
| `max_seq_len` scaling with `--token_budget` (512–2048 sweep) | E5 extended | Medium |
| Cluster-merge post-processing (merge nearby predicted borders into one best boundary) | E7 extended | Medium |
| Validation split + eval-during-training + best-checkpoint + early stopping | E10 | Medium |
| Non-scene segment parsing + 4-way boundary-type labels | E9 | Stretch (needs decision note) |

Current status of upstream gaps in our code:

- **Completion-only loss:** `train_job.py` trains on the full chat-formatted string
  (`dataset_text_field="text"`, no response masking). The upstream
  [`train_unsloth.py`](../../upstream/scene-segmentation/llama/train_unsloth.py) has the same issue;
  TRL notes recommend training on completions only.
- **Negative sampling:** `paper10pct` and `hard` modes exist; percentage sweep and the exact
  "keep-all-near-border-then-random-top-up" rule do not.
- **Post-processing:** `min_scene_len_3/5` and confidence threshold exist; cluster-merge does not.
- **Validation:** no eval-during-training, no best-checkpoint saving, no early stopping.

---

## 6. Step-by-step

### Step 0 — One-time setup (~15 min)

1. HF Pro account active; `hf auth login` with a **write** token.
2. Locally: `pip install huggingface_hub unsloth trl` (or use project venv).
3. Set `export HF_USER=RuthonField` (or your username).
4. (Optional, only for cloud Jobs) Add prepaid credits at
   [hf.co/settings/billing](https://huggingface.co/settings/billing).

What you should see: `hf auth whoami` prints your username without error.

### Step 1 — Pilot 0: build data and verify pipeline (~10 min, no GPU)

Folds mode works today with only STSS-Test-2 + Excel (**debugging / Pilot 0 only**):

```bash
source .venv/bin/activate
python src/finetune/build_sft_dataset.py --mode folds --fold both \
  --target_format cot_list --negative_mode paper10pct
```

Corpus mode (paper-comparable; **required before E1+**, once the full corpus is on disk):

```bash
python src/finetune/build_sft_dataset.py --mode corpus \
  --train_split train_full --eval_split stss_test_2 \
  --target_format cot_list --negative_mode paper10pct
```

What you should see: per-job line `train=... eval=...`, then `[verify] OK` with each text's
sentence/border counts matching the manifest (a `MISMATCH` means a parsing or split problem — fix
before training). Outputs land in `data/processed/finetune/<job>/` plus `verification.json`.

Complete Pilot 0 Stages 1–2 (prompting + tiny eval) before proceeding to Step 2.

### Step 2 — E0 smoke run (local, free, ~1–2 h GPU; Pilot 0 Stage 3)

```bash
HF_USER=RuthonField DATA_SCOPE=pilot RUN_CONFIG=src/finetune/hf_jobs/configs/E0_smoke.json \
  BUILD_MODE=skip bash src/finetune/hf_jobs/submit_job.sh
```

(`BUILD_MODE=skip` reuses data from Step 1; omit it to rebuild.)

What you should see: adapter at `https://huggingface.co/RuthonField/scene-seg-llama-3-2-3b-instruct-fold_A`
plus `metrics_*.json` with a real `macro_f1` (not 0.0/NaN). Tag the run note as **debug**; do not
report these numbers as model performance.

### Step 3 — Run the experiment matrix (one factor at a time)

**Gate:** E1+ runs only after (a) Pilot 0 complete and (b) full 41-text corpus verified on disk.

Each row is one `submit_job.sh` invocation. Fixed controls unless the row changes them: train =
`train_full`, eval = `stss_test_2`, seed 1337, LoRA r=16/alpha=16, 1 epoch, LR 2e-4, target =
`cot_list`, context = 4 sentences each side, negatives = `paper10pct`.

#### Recommended ablation order

Run experiments in this sequence (one factor at a time):

1. **Baseline reproduction** — E1: paper CoT-List, 512-token context, 10% negatives.
2. **Completion-only loss** — E1b (highest-priority code change).
3. **Negative sampling** — E4: 10%, 20%, hard near-border negatives; evaluate precision and recall
   separately.
4. **Context length** — E5: 512 vs 1024 vs 2048 tokens.
5. **Output format** — E3: CoT-List vs No-CoT vs JSON-only label.
6. **Scene/non-scene auxiliary labels** — E9 (stretch; requires decision note).
7. **Base models** — E2: Llama, Qwen, Mistral variants.

**Most promising changes** (target these first after baseline repro):

- Completion-only loss
- Hard near-border negative sampling
- Longer context (beyond paper's 512-token BERT-fair window)
- Cleaner final labels (JSON `{"label": ...}` — already supported; ablate vs free-text in E3)

#### Experiment matrix

| Exp | Factor under test | How | Status | Why |
|-----|-------------------|-----|--------|-----|
| **E0** | pipeline smoke | folds mode, `E0_smoke.json` | Supported | Pilot 0 Stage 3; debugging only |
| **E1** | anchor baseline | `E1_anchor.json`, corpus, CoT-List, paper10pct, tokens512 | Supported | Paper-comparable anchor all later runs beat |
| **E1b** | completion-only loss | E1 config + mask prompt tokens in `train_job.py` | **Code TODO** | Model should learn answer pattern, not reproduce long prompts |
| **E2** | base model family | swap `models` in config | Supported | Prompt format / class balance may matter more than size |
| **E3** | target format | rebuild `--target_format json` and `no_cot` | Supported | Paper: biggest single factor (0.62 vs 0.09); keep CoT-List as default |
| **E4** | negative sampling | rebuild `--negative_mode ratio`, `hard`; sweep 5/10/20/30/50% | Partial | Random negatives too easy; hard mode targets FP error pattern |
| **E5** | context length | rebuild `--context_mode tokens512 --token_budget {512,768,1024,1536,2048}` | Partial | Paper used 512 for BERT fairness; Llama may benefit from longer context |
| **E6** | capacity | config `epochs=2`, then `lora_r=32` (best only) | Supported | Cheap probe for more learning |
| **E7** | post-processing | in-job `min_scene_len_3`, `confidence+minlen`; cluster-merge | Partial | Scene boundaries are sparse; suppress nearby false positives |
| **E8** | stretch repro | 8B Llama-3.1; `test_full` eval; two-stage verifier | Supported | May need `COMPUTE=jobs FLAVOR=t4-small` |
| **E9** | scene/non-scene types | 4-way labels: SCENE_TO_SCENE / SCENE_TO_NONSCENE / NONSCENE_TO_SCENE / NOBORDER | **Code TODO** | Targets non-scene merge errors; collapse to binary for eval |
| **E10** | validation selection | val split from train texts; eval every N steps; save best by F1@3; early stop | **Code TODO** | Final epoch may not be best on small dataset |

#### Improvement suggestions mapped to experiments

| # | Suggestion | Experiment | Implementation |
|---|------------|------------|----------------|
| 1 | Keep CoT-List; structured a–e) + machine-friendly final label | E3 (ablation) | **Supported** — JSON label in all formats |
| 2 | Train on completions only | E1b | **Code TODO** — Unsloth `train_on_responses_only` or TRL assistant masking |
| 3 | Tune negative ratio (5–50%); track P/R separately | E4 | **Partial** — `paper10pct` + `ratio`; percentage sweep TODO |
| 4 | Near-border hard negatives (±1..3) | E4 | **Partial** — `--negative_mode hard --hard_window 3`; keep-all-near rule TODO |
| 5 | Context beyond 512 tokens | E5 | **Partial** — `--token_budget` exists; couple to `max_seq_len` TODO |
| 6 | Second-stage thresholding / smoothing | E7 | **Partial** — min-scene-len + confidence; cluster-merge TODO |
| 7 | Scene/non-scene boundary types | E9 | **Code TODO** — parser + decision note required |
| 8 | Modern base models (Llama-3.1-8B, Llama-3.2-3B, Qwen2.5-7B, Qwen3-8B, Mistral-7B) | E2, E8 | **Supported** — config `models` list; track German encoder baseline separately |
| 9 | Validation-based model selection | E10 | **Code TODO** — no eval-during-training yet |
| 10 | Ablation ordering | See above | Documented |

**E2 model candidates:**

- `unsloth/Llama-3.2-3B-Instruct` — cheap anchor / local default
- `unsloth/Meta-Llama-3.1-8B-Instruct-bnb-4bit` — paper-scale repro (E8)
- `unsloth/Qwen2.5-7B-Instruct-bnb-4bit` or Qwen3-8B
- `unsloth/Mistral-7B-Instruct-v0.3-bnb-4bit`
- German encoder baseline (GBERT) tracked separately, not in QLoRA matrix

**E4 decision rules** (when sweeping negatives):

- Model predicts too many borders → increase negative fraction or use `hard` mode
- Model misses borders → decrease negative fraction or oversample hard positives

**Standard local command** (free):

```bash
HF_USER=RuthonField DATA_SCOPE=corpus RUN_CONFIG=src/finetune/hf_jobs/configs/E1_anchor.json \
  bash src/finetune/hf_jobs/submit_job.sh
```

**Cloud fallback** (prepaid credits; see §0 cost table):

```bash
HF_USER=RuthonField DATA_SCOPE=corpus COMPUTE=jobs FLAVOR=t4-small TIMEOUT=8h \
  RUN_CONFIG=src/finetune/hf_jobs/configs/E1_anchor.json \
  bash src/finetune/hf_jobs/submit_job.sh
```

Data-side factors (E3/E4/E5/E9): rerun `build_sft_dataset.py`, then `submit_job.sh` (re-uploads data).
Training-side factors (E1b/E2/E6/E10): edit config and/or `train_job.py`.

What you should see each time: a new adapter repo + `metrics_*.json`. Compare
`scenarios.none.tol_3.macro_f1` (raw) and post-processed variants against E1. Always report precision
and recall alongside F1, especially when tuning negatives (E4).

### Success criteria

- **Pilot 0:** parseability > 95%; pipeline produces expected input-output structure; manual FP/FN
  inspection complete.
- **Must (E1+):** beat our prompting natural-distribution baseline (F1@3 ~ 0.51 post-processed).
- **Target:** F1@3 >= 0.55 on STSS-Test-2 with a 3B model.
- **Stretch:** reach the paper's 0.62-0.63 range.

---

## 7. Time estimate

| Phase | Work | Time |
|-------|------|------|
| Setup (Step 0) | HF auth, optional credits | ~15 min (one-time) |
| Pilot 0 (Step 1 + Stages 1–2) | data build, prompting, tiny eval | ~1–2 days |
| E0 smoke (Step 2) | 1 model, eval_limit 200 | ~1–2 h local GPU |
| Data build + verify (repeat per data factor) | local | ~10 min each |
| Per full experiment (local) | 3B train (~2–3 h) + full eval (~4–6 h) | **~6–9 h GPU** |
| Core matrix E1–E7, E1b, E10 | ~12 runs serial on local GPU | **~72–108 h GPU** (~1–2 weeks nights/weekends) |
| Stretch E8–E9 | cloud Job if local OOM; non-scene parsing | ~8–10 h cloud (~$5–8 on t4-small) + data work |

Local runs are slower per hour than a cloud T4 but cost **$0 extra**. Parallel cloud Jobs are possible
if you add credits, but serial local is the budget default.

---

## 8. Logging (per [`../../rule.md`](../../rule.md))

- Experiment note:
  [`../../research_log/experiments/experiment__finetune__hf-jobs-qlora-campaign.md`](../../research_log/experiments/experiment__finetune__hf-jobs-qlora-campaign.md).
- One run note per submission in `research_log/runs/`; record config, Job URL (if cloud), adapter repo,
  and `metrics_*.json` numbers.
- **Pilot 0 / E0 / folds-mode runs:** tag run notes as `debug`; never quote their F1 as model performance.
- Artifact note for each adapter + metrics file in `research_log/artifacts/`.
- Decision note for compute platform switch:
  [`../../research_log/decisions/decision__finetune-compute-hf-local.md`](../../research_log/decisions/decision__finetune-compute-hf-local.md).
- Decision note required before E9 (scene/non-scene label definition change).

---

## 9. Deprecated: Kaggle path

The Kaggle kernel under `src/finetune/kaggle/` is **deprecated** (see README there). It remains for
reference only; all new runs use `src/finetune/hf_jobs/`.
