# dProse Full-Corpus Scene Segmentation — Final Report

## What we did

We ran automatic scene-boundary labelling over the whole dProse prose corpus with Gemini 2.5 Pro (batch API, prompt family B, 12 sentences of context each side). Every sentence gets one of two labels: `BORDER` (a new scene starts here) or `NOBORDER` (same scene continues). Because dProse has no gold scene labels, we could not measure accuracy directly. Instead we ran the corpus in cost-capped waves and, after each wave, checked the health and plausibility of the output: parse success, BORDER rate, scene lengths, and runs of consecutive BORDERs. Books with unusual numbers were double-checked around the flagged sentences. 

## Corpus at a glance

- **327 books**, **120,369 sentences** labelled end to end.
- Median BORDER rate across books: **24.0%** (range 8.9% to 41.4%).
- Statistical outliers on BORDER rate (|z| >= 2): **16 books** (9 high, 7 low).

## Scene segmentation patterns

- Typical scene length is short: corpus-median of the per-book median scene length is **2 sentences**.
- On average **54%** of inferred scenes are only 1-2 sentences long — the main over-segmentation signal to watch.
- Across the corpus, **67,502 sentences** (56.1%) are flagged for manual review (either merge or split candidates).
- Runs of consecutive BORDERs (several scene breaks in a row) are the clearest sign the model over-split a passage, usually around dialogue.

## Nature of the corpus

dProse is heterogeneous German prose: short lyrical pieces sit next to long novels, and registers range from fairy-tale narration to dense epistolary and dialogue-heavy texts. This shows up directly in the wide spread of BORDER rates: there is no single "correct" rate for the corpus, so a book's rate is only meaningful relative to its own genre and length. High-rate books tend to be fragmentary or dialogue-driven (many short scenes); low-rate books tend to be single continuous passages (letters, monologue, sustained description). The per-book metrics in `corpus_stats.csv` and the outlier notes in `anomalous_books.csv` are the right lens for judging any individual book.

## Known data-quality notes

- **40 sentences** carry a `manual_fix` = `neighbor_agreement` flag (see the `manual_fix` column in `all_sentences.csv`); these were labelled by consensus of their neighbours, not by the model, and are the first place to look during review.
- A few sentences were originally blocked by the model's safety filter (`PROHIBITED_CONTENT`); these are among the patched rows.

## Files in this folder

- `corpus_stats.csv` — per-book metrics + a corpus aggregate row.
- `anomalous_books.csv` — BORDER-rate outliers with review guidance.
- `all_sentences.csv` — every sentence, `border` as 0/1, with model reasoning and review flags.
