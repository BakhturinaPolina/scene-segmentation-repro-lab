# Excel Prompting Experiments — Short Report

Date: 2026-06-01  

All runs below use **Prompt family B** (short zero-shot JSON instruction). That prompt, with deterministic decoding, was already the best setup on the STSS benchmark novels; we reused the same style here so results stay comparable across corpora.

---

## 1) Data and gold labels

Each row is one sentence. Annotators grouped sentences into scenes; whenever the scene number changes, the **first sentence of the new scene** is marked as a scene border.

**Example (simplified):**

| Sentence | Scene | Gold label |
|---|---|---|
| “Es lebte einmal eine alte Königin …” | 1 | BORDER (start of story / scene 1) |
| “Wie die erwuchs, wurde sie … versprochen.” | 1 | NOBORDER (same scene) |
| “Also nahmen beide von einander betrübten Abschied …” | 2 | BORDER (scene changed) |
| “Da sie eine Stunde geritten waren …” | 2 | NOBORDER |

**Corpus size**

| Text | Sentences | True scene borders | Border rate |
|---|---:|---:|---:|
| Gaensemagd | 71 | 7 | 9.9% |
| Kleist | 245 | 14 | 5.7% |
| **Both together** | **316** | **21** | **6.7%** |

Scene borders are **rare** compared with normal sentences. That matters when reading the scores below.

**Open problem — overprediction:** Weaker models in early runs predicted far more borders than exist in the gold data (on the order of **five to six times** too many). **Gemini 2.5 Pro** over-predicts less (~**2.2×** gold on the stability rerun). Many mistakes are “a bit early or late” rather than completely wrong, but extra borders still hurt **precision**.

---

## 2) Step 1 — Compare models (Prompt B, same settings)

We ran several large models on the same two texts with Prompt B and scored predictions against the Excel gold borders.

**How to read the metrics**

| Metric | Plain meaning |
|---|---|
| **Precision** | When the model says “border”, how often is it right? Low precision = many false alarms. |
| **Recall** | Of all real borders in the gold data, how many did the model find? Low recall = missed scene changes. |
| **F1 (exact)** | One combined score for exact sentence match (balances precision and recall). |
| **tol3 / tol5 F1** | Softer scores: a prediction still counts as correct if it falls within **3** or **5** sentences of the true border. Useful when the model is roughly right but shifted by a few sentences. |

**Model ranking on both Excel texts (full evaluation, Prompt B)**

Source runs: `outputs/runs/prompting/2026-05-31-excel-gemini-reasoning-on/` (Gemini, reasoning on), `2026-05-30-excel-3model-sweep/` (Gemini low, GPT-4.1, Sonnet 4), `2026-05-30-excel-opus4/` (Opus 4). Macro-averaged F1 over Gaensemagd + Kleist from each run’s `summary.json`.

| Rank | Model | Reasoning mode | Exact F1 (tol0) | Near-match F1 (tol3) |
|---:|---|---|---:|---:|
| 1 | Gemini 2.5 Pro | on | **0.50** | **0.76** |
| 2 | Gemini 2.5 Pro | low | 0.49 | 0.72 |
| 3 | Claude Opus 4 | off | 0.44 | 0.61 |
| 4 | GPT-4.1 | off | 0.42 | 0.62 |
| 5 | Claude Sonnet 4 | off | 0.35 | 0.50 |

*Recalculated from artifacts (2026-06-23): row 1 = macro F1 **0.4981** / **0.7617** (`google/gemini-2.5-pro`, reasoning on, seed 1337). A later stability rerun (`2026-06-16-excel-gemini-familyB-stability`) gives **0.5063** / **0.7707** — within ±0.02 of the May baseline.*

**Takeaway:** **Gemini 2.5 Pro with reasoning turned on** gave the best results on these Excel texts. Turning reasoning from “low” to “on” helped especially for near-match quality (tol3 F1 **+0.043**, 0.7617 vs 0.7184). 

---

## 3) Step 2 — Post-processing experiment (Prompt B, Gemini 2.5 Pro)

**Why we ran this:** Even with Prompt B, the model often marks borders on **several neighbouring sentences** around a real scene change. Humans might accept “within a few sentences”, but strict scoring treats each extra mark as a false positive. We tested simple clean-up rules that **thin out** border marks that sit too close together.

**What we changed (only one thing at a time):**

| Rule | Idea in plain language |
|---|---|
| **none** | Use raw model output. |
| **min_scene_len_3** | After a predicted border, ignore any new border for the next **3** sentences. |
| **min_scene_len_5** | Same, but with a **5**-sentence gap. |

**Model:** `google/gemini-2.5-pro` (reasoning on) — same as the top-ranked model in Step 1. Predictions from run `2026-05-31-excel-gemini-reasoning-on` (Prompt B, seed 1337, temperature 0). Only the clean-up rule differed; no new API calls.

**Results (both texts combined, macro-averaged over Gaensemagd + Kleist)** — recalculated from `outputs/review/excel/gemini_postprocess/normalization_what_if.csv` with **0-based index alignment** (gold CSV uses 1-based Excel IDs; runner review JSONL uses 0-based positions). Same aggregation as Step 1.

| Rule | Precision | Recall | Exact F1 | Near-match F1 (tol3) | Near-match F1 (tol5) |
|---|---:|---:|---:|---:|---:|
| none | 0.36 | 0.82 | **0.50** | **0.76** | 0.80 |
| min gap 3 sentences | 0.43 | 0.71 | 0.53 | 0.77 | 0.81 |
| min gap 5 sentences | 0.43 | 0.54 | 0.47 | 0.80 | **0.85** |

*(Exact macro source values: none P=0.3579 R=0.8215 F1=0.4981 tol3=0.7617 tol5=0.8007; min_gap_3 F1=0.5342 tol3=0.7707 tol5=0.8118; min_gap_5 F1=0.4726 tol3=0.7986 tol5=0.8493.)*

- **Raw Gemini (`none`) matches Step 1** — exact F1 **0.50** and tol3 **0.76** are the same run, now scored consistently.
- **Min-gap rules trade recall for precision.** A 3-sentence gap nudges exact F1 up to **0.53** on Gaensemagd but costs Kleist recall (gold borders can be 1 sentence apart). A 5-sentence gap pushes tol5 to **0.85** but exact F1 falls to **0.47**.
- **Post-processing is optional, not clearly dominant:** tol3 is nearly flat; only tol5 gains meaningfully under the 5-sentence rule, at the cost of missing real borders.

So post-processing helps only if reviewers care about **tol5** placement and accept lower recall; for exact or tol3 scoring, raw Gemini output remains the better default.

---

## 4) What went wrong (error pattern)

- **Too many predicted borders** compared with gold (over-segmentation).
- A noticeable share of false alarms sit **within one to three sentences** of a real border—timing slips, not wholly invented scenes.
- Errors often appear in **transition passages** (time/place/character shift), where the model is “almost” right.

---

## 5) Practical conclusions

1. Decide whether success means **exact sentence** or **within a few sentences**. The numbers look very different; mixing both without saying so is misleading.

2. Treat **border overprediction** as a first-class problem—Gemini already helps (~2× gold). Post-processing can raise tol5 (up to **0.85** with a 5-sentence gap) but lowers recall; default to raw Gemini unless tol5 is the agreed target metric.

