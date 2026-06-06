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

**Open problem — overprediction:** In the main runs, models often predicted far more borders than exist in the gold data (on the order of **five to six times** too many). Many mistakes are “a bit early or late” rather than completely wrong, but the sheer number of extra borders hurts **precision**. This needs a dedicated follow-up (better model choice, post-processing, or clearer annotation rules).

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

| Rank | Model | Reasoning mode | Exact F1 (tol0) | Near-match F1 (tol3) |
|---:|---|---|---:|---:|
| 1 | Gemini 2.5 Pro | on | **0.50** | **0.76** |
| 2 | Gemini 2.5 Pro | low | 0.49 | 0.72 |
| 3 | Claude Opus 4 | off | 0.44 | 0.61 |
| 4 | GPT-4.1 | off | 0.42 | 0.62 |
| 5 | Claude Sonnet 4 | off | 0.35 | 0.50 |

**Takeaway:** **Gemini 2.5 Pro with reasoning turned on** gave the best results on these Excel texts. Turning reasoning from “low” to “on” helped especially for near-match quality (tol3 F1 about **+0.04**). 

---

## 3) Step 2 — Post-processing experiment (Prompt B, one model)

**Why we ran this:** Even with Prompt B, the model often marks borders on **several neighbouring sentences** around a real scene change. Humans might accept “within a few sentences”, but strict scoring treats each extra mark as a false positive. We tested simple clean-up rules that **thin out** border marks that sit too close together.

**What we changed (only one thing at a time):**

| Rule | Idea in plain language |
|---|---|
| **none** | Use raw model output. |
| **min_scene_len_3** | After a predicted border, ignore any new border for the next **3** sentences. |
| **min_scene_len_5** | Same, but with a **5**-sentence gap. |

Same model and Prompt B as in the controlled run; only the clean-up rule differed.

**Results (both texts combined)**

| Rule | Precision | Recall | Exact F1 | Near-match F1 (tol3) | Near-match F1 (tol5) |
|---|---:|---:|---:|---:|---:|
| none | 0.06 | 0.33 | 0.10 | 0.36 | 0.42 |
| min gap 3 sentences | 0.06 | 0.19 | 0.09 | 0.51 | 0.57 |
| min gap 5 sentences | 0.07 | 0.14 | 0.09 | 0.54 | **0.67** |

- **Strict exact matching** stays weak for all rules (F1 around 0.09–0.10). Cleaning up neighbours does not magically fix every wrong border.
- **Softer “within a few sentences” scores improve a lot** when we enforce a minimum gap—especially **5 sentences** (tol5 F1 rises from **0.42 → 0.67**). That supports the idea that many errors are **clustered near** true boundaries, not random noise.
- The trade-off: stricter spacing **finds fewer** true borders (recall drops from 0.33 to 0.14 with the 5-sentence rule), because some legitimate borders sit closer than five sentences apart.

So post-processing is useful if reviewers care about **approximate** scene placement; it is less helpful if every sentence must be exact.

---

## 4) What went wrong (error pattern)

- **Too many predicted borders** compared with gold (over-segmentation).
- A noticeable share of false alarms sit **within one to three sentences** of a real border—timing slips, not wholly invented scenes.
- Errors often appear in **transition passages** (time/place/character shift), where the model is “almost” right.

---

## 5) Practical conclusions

1. Decide whether success means **exact sentence** or **within a few sentences**. The numbers look very different; mixing both without saying so is misleading.

2. Treat **border overprediction** as a first-class problem—either improve the model side (Gemini already helps) or agree on post-processing / annotation tolerance before reporting a single headline F1.

