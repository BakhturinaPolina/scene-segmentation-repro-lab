# dProse Full-Corpus Scene Segmentation — Final Report

## What we did

We ran automatic scene-boundary labelling over the whole dProse prose corpus with Gemini 2.5 Pro (batch API, prompt family B, 12 sentences of context each side). Every sentence gets one of two labels: `BORDER` (a new scene starts here) or `NOBORDER` (same scene continues). Because dProse has no gold scene labels, we could not measure accuracy directly. Instead we ran the corpus in cost-capped waves and, after each wave, checked the health and plausibility of the output: parse success, BORDER rate, scene lengths, and runs of consecutive BORDERs. Books with unusual numbers were read by hand around the flagged sentences. Sentences the model failed to label (thinking overflow, transient API errors, safety blocks) were fixed in three tiers: batch retry, synchronous retry, and finally a neighbour-agreement patch for the last few stubborn cases. The full log lives in `docs/corpora/DPROSE_CORPUS_SPOT_CHECKS.md`.

## Corpus at a glance

- **327 books**, **120,369 sentences** labelled end to end.
- Total estimated cost: **~$514 USD**.
- Parse success after remediation: **100.0%** mean per book (all 40 unresolved sentences patched by neighbour agreement).
- Median BORDER rate across books: **24.0%** (range 8.9% to 41.4%).
- Statistical outliers on BORDER rate (|z| >= 2): **16 books** (9 high, 7 low).

## Scene segmentation patterns

- Typical scene length is short: corpus-median of the per-book median scene length is **2 sentences**.
- On average **54%** of inferred scenes are only 1-2 sentences long — the main over-segmentation signal to watch.
- Across the corpus, **67,504 sentences** (56.1%) are flagged for manual review (either merge or split candidates).
- Runs of consecutive BORDERs (several scene breaks in a row) are the clearest sign the model over-split a passage, usually around dialogue.

## Nature of the corpus

dProse is heterogeneous German prose: short lyrical pieces sit next to long novels, and registers range from fairy-tale narration to dense epistolary and dialogue-heavy texts. This shows up directly in the wide spread of BORDER rates: there is no single "correct" rate for the corpus, so a book's rate is only meaningful relative to its own genre and length. High-rate books tend to be fragmentary or dialogue-driven (many short scenes); low-rate books tend to be single continuous passages (letters, monologue, sustained description). The per-book metrics in `corpus_stats.csv` and the outlier notes in `anomalous_books.csv` are the right lens for judging any individual book.

## Known data-quality notes

- **40 sentences** were labelled by neighbour agreement (not by the model) after retries failed; they live in the per-book `predictions.jsonl` under `manual_fix=neighbor_agreement`.
- A few sentences were originally blocked by the model's safety filter (`PROHIBITED_CONTENT`); these are among the patched rows.
- Sentence 0 of every book is forced to `is_scene_boundary=True` so `scene_id` and the boundary flag stay aligned (a book's first sentence always opens scene 1).
- The older `corpus_summary.json` and `predictions_full.jsonl` in the run root are **stale pilot artifacts** (3 books only) and should be ignored; the authoritative state is `corpus_progress.json` plus the per-book files under `books/`.

## Files in this folder

- `corpus_stats.csv` — per-book metrics + a corpus aggregate row.
- `anomalous_books.csv` — BORDER-rate outliers with review guidance.
- `all_sentences.csv` / `all_sentences.xlsx` — every sentence in the Kleist-scenes column order (`Sentence`, `Phrase`, `Text`, `is_scene_boundary`, `scene_id`) plus `slug` and `model_reason`.
- `per_book_xlsx/<slug>.xlsx` — one workbook per book with the same Kleist-scenes columns + `model_reason` (`is_scene_boundary` as True/False → Wahr/Falsch in German Excel).
- `final_report.md` — this file.
