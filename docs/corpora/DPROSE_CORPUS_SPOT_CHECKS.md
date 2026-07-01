# dProse Full Corpus — Processing Spot-Checks

**Purpose:** Living log of sanity checks and manual spot-reviews during the resumable full-corpus batch run (`dprose-full-corpus`). Each wave gets a section after completion.

**Run root:** `outputs/runs/dprose_batch/dprose-full-corpus/`  
**Config:** Gemini 2.5 Pro batch, Prompt Family B, `max_output_tokens=2048`, `thinking_budget=-1`, `context_sentences=12`  
**Progress artifact:** `corpus_progress.json`

Related:

- [DPROSE_PILOT_SANITY_CHECK.md](./DPROSE_PILOT_SANITY_CHECK.md) — pre-scale pilot (3 books)
- [DPROSE_COST_ESTIMATE.md](./DPROSE_COST_ESTIMATE.md) — cost model and wave budgeting
- Plan: `.cursor/plans/dprose_full_corpus_run_ee81d741.plan.md`

No gold labels exist for dProse. Spot-checks validate **pipeline health** (parse rate, batch success, cost) and **label plausibility** (border rate, over-segmentation signals, text-aligned reasoning)—not accuracy against human scene boundaries.

---

## Spot-check workflow

After each book completes, the orchestrator runs `scripts/evaluation/review_dprose_book.py` and prints a review block. During processing we use:

| Layer | What | When |
|-------|------|------|
| Automated | Parse OK rate, BORDER rate, scene length, consecutive-BORDER alerts | Every book |
| Quality gate | Stop wave if `parse_ok_rate < 0.95` | Per book |
| Post-wave | Aggregate stats vs pilot; scan for outliers | End of wave |
| Manual | Read predictions around flagged indices | Outliers + parse failures |

**Logs:** `logs/dprose/wave_<wave_id>_<date>.log`  
**Per-book artifacts:** `books/<slug>/book_review.json`, `book_review.txt`, `predictions.jsonl`

---

## Corpus progress (snapshot)

| Metric | After Wave 4 |
|--------|----------------|
| Books complete | 179 / 327 |
| Sentences complete | 67,704 / 120,369 |
| Cumulative cost | ~$286.20 USD |
| Parse OK (all completed books) | 67,655 / 67,704 (**99.93%**) |
| Parse OK (Wave 4 books only) | 20,723 / 20,735 (99.9%) |
| Books with remaining parse fails | **26** (49 sentence-keys) |

Pilot (3 books) + Wave 1 (15 books) + Wave 2 (55 books, `dprose_161` … `dprose_692`) + Wave 3 (51 books, `dprose_693` … `dprose_1029`) + Wave 4 (55 books, `dprose_1040` … `dprose_1535`).

### Parse failures — corpus inventory (post-Wave 4)

Authoritative source: per-book `book_review.json` / `predictions.jsonl` on disk (2026-07-01). Partial `--retry_failed` passes on 2026-06-30 cleared **33** keys across Wave 1 pilot + Wave 2 (`logs/dprose/retry_failed_2026-06-30.log`) and **11** keys across Waves 3–4 (`logs/dprose/retry_failed_2026-06-30_wave3plus.log`). **49 keys** remain.

| Wave | Books with fails | Failed keys | Lowest parse % |
|------|----------------:|------------:|---------------:|
| Pilot + Wave 1 | 0 | 0 | — |
| Wave 2 | 4 | 15 | 97.8% (`dprose_435`) |
| Wave 3 | 12 | 22 | 98.4% (`dprose_989`) |
| Wave 4 | 10 | 12 | 99.5% (`dprose_1535`, `dprose_1156`) |
| **Total** | **26** | **49** | 97.8% |

All 179 completed books pass the **≥95% parse gate**. No full-book re-runs needed — only sentence-key retries via `--retry_failed`.

| Book | Parse | Fails | Failed keys |
|------|------:|------:|-------------|
| dprose_435 | 265/271 (97.8%) | 6 | `:199`, `:200`, `:206`, `:210`, `:211`, `:212` |
| dprose_989 | 304/309 (98.4%) | 5 | `:17`, `:36`, `:75`, `:132`, `:271` |
| dprose_555 | 549/555 (98.9%) | 6 | `:426`, `:431`, `:432`, `:435`, `:440`, `:441` |
| dprose_926 | 353/356 (99.2%) | 3 | `:244`, `:288`, `:332` |
| dprose_1535 | 376/378 (99.5%) | 2 | `:173`, `:251` |
| dprose_1156 | 383/385 (99.5%) | 2 | `:21`, `:274` |
| dprose_838 | 422/424 (99.5%) | 2 | `:367`, `:72` |
| dprose_516 | 428/430 (99.5%) | 2 | `:93`, `:101` |
| dprose_802 | 255/256 (99.6%) | 1 | `:51` |
| dprose_764 | 525/527 (99.6%) | 2 | `:93`, `:130` |
| dprose_904 | 547/549 (99.6%) | 2 | `:239`, `:255` |
| dprose_1023 | 308/309 (99.7%) | 1 | `:174` |
| dprose_1303 | 321/322 (99.7%) | 1 | `:19` |
| dprose_1332 | 344/345 (99.7%) | 1 | `:134` |
| dprose_906 | 352/353 (99.7%) | 1 | `:150` |
| dprose_979 | 760/762 (99.7%) | 2 | `:332`, `:478` |
| dprose_1319 | 405/406 (99.8%) | 1 | `:298` |
| dprose_1356 | 439/440 (99.8%) | 1 | `:90` |
| dprose_1363 | 439/440 (99.8%) | 1 | `:3` |
| dprose_1019 | 449/450 (99.8%) | 1 | `:393` |
| dprose_1049 | 451/452 (99.8%) | 1 | `:303` |
| dprose_1345 | 493/494 (99.8%) | 1 | `:165` |
| dprose_898 | 515/516 (99.8%) | 1 | `:373` |
| dprose_293 | 520/521 (99.8%) | 1 | `:35` |
| dprose_757 | 574/575 (99.8%) | 1 | `:88` |
| dprose_1462 | 583/584 (99.8%) | 1 | `:572` |

**Estimated retry cost (all 49 keys):** ~**$0.20** (~0.07% of $286.20 cumulative; ~$0.004/sentence).

---

## Wave 1 — `wave_01_eur25` (2026-06-28)

**Manifest:** `data/manifests/waves/wave_01_eur25.json`  
**Log:** `logs/dprose/wave_wave_01_eur25_2026-06-28.log`  
**Books:** 15 (`dprose_51`, `dprose_52`, `dprose_56`, `dprose_59`, `dprose_74`, `dprose_77`, `dprose_106`, `dprose_119`, `dprose_120`, `dprose_121`, `dprose_135`, `dprose_137`, `dprose_146`, `dprose_148`, `dprose_151`)  
**Budget cap:** $23.00 — **not hit** (wave spend ~$21.40)

### Aggregate metrics

| Metric | Wave 1 (15 books) | Pilot (3 books) |
|--------|-------------------|-----------------|
| Sentences | 4,880 | 989 |
| Parse OK | 4,880 / 4,880 (100%) | 988 / 989 (99.9%) |
| BORDER rate | 23.5% | 23.8% |
| Median scene length | 1–4 (per book) | 2–3 |
| 1–2 sent scenes | 38.8–65.8% | 46–57% |
| Max consecutive BORDER | 7 (`dprose_119`) | 5 (`dprose_806`) |
| Batch jobs | 15 / 15 succeeded | — |

**Verdict:** Wave 1 **passed**. Behavior matches the validated pilot: ~24% BORDER rate, ~half of inferred scenes span 1–2 sentences, coherent `reason` fields. Over-segmentation at montage/chapter boundaries is expected (see pilot doc); not a pipeline defect.

### Per-book summary

Parse 100% on all 15 (2 keys retried — see below). Sorted by BORDER rate; Notes only when flagged.

| Book | Sents | BORDER | Med | Run | Notes |
|------|------:|-------:|----:|----:|-------|
| dprose_137 | 331 | **14.5%** | **4** | 3 | Low — episodic dialogue; 54-sent gap idx 40–94 |
| dprose_148 | 577 | 18.4% | 2 | 5 | Longest in wave |
| dprose_56 | 284 | 19.7% | 3 | 4 | |
| dprose_146 | 434 | 20.7% | 2 | 6 | |
| dprose_77 | 282 | 21.6% | 3 | 4 | |
| dprose_121 | 271 | 21.8% | 2 | 4 | |
| dprose_135 | 362 | 23.2% | 2 | 5 | |
| dprose_59 | 266 | 24.1% | 3 | 4 | |
| dprose_151 | 367 | 25.1% | 2 | 5 | |
| dprose_74 | 414 | 25.6% | 2 | 5 | |
| dprose_120 | 241 | 25.7% | 2 | 5 | Parse fail idx 48 → retried |
| dprose_119 | 220 | 28.2% | 2 | **7** | Run idx 155–161: frame coda + Part 2 title |
| dprose_106 | 364 | 28.6% | 2 | 4 | |
| dprose_51 | 238 | 32.4% | 2 | 4 | High — fairy-tale exposition |
| dprose_52 | 229 | **32.8%** | 1 | **6** | Highest rate; travel montage idx 57–62 (6× BORDER) |

### Parse failures and retries

Two keys failed initial parse (prose/thinking output instead of JSON—the same failure mode as `dprose_100:22` in the pilot).

| Key | Sentence (abbrev.) | Initial failure | Retry result |
|-----|-------------------|-----------------|--------------|
| `dprose_120:48` | «Im weißen Kleide standen Feld und Wald.» | Markdown prose answer, no JSON | **BORDER** — winter landscape after family scene |
| `dprose_137:104` | Frechdachs lassos the miller | Truncated thinking prose | **NOBORDER** — climax of ongoing capture scene |

**Retry command (2026-06-28):**

```bash
set -a && source .env && set +a
.venv/bin/python -u src/runners/run_dprose_batch_corpus.py \
  --wave_manifest data/manifests/waves/wave_01_eur25.json \
  --books dprose_120,dprose_137 \
  --retry_failed \
  --output_root outputs/runs/dprose_batch/dprose-full-corpus
```

**Retry log:** `logs/dprose/retry_failed_2026-06-28.log`  
Both books reached **100% parse** after retry.

**Operational fix:** `--retry_failed` initially wrote retry-only batch stats into `corpus_progress.json` (wrong per-book cost/border rate). Repaired from `book_review.json`; orchestrator updated to read review metrics for progress updates on all runs.

---

### Manual spot-checks — outliers

#### `dprose_52` — highest BORDER rate (32.8%), max run 6

**Text:** *Die drei Prinzen* — satirical fairy tale (King Monosogoporibius I, three nephews).

**Findings:**

- **Opening acts:** ~38–42% BORDER in the first two thirds — dense exposition (succession debate, mother’s scheming, lottery).
- **Triple/quadruple openings:** idx 20–23 — four consecutive BORDERs around one narrative beat (clever mother / “Wie das heißt…”).
- **Max run idx 57–62:** compressed summary montage on return journey — courtiers gossip → capital → regency transfer → first manifest → constant war. Six sentences, six BORDERs (same pattern as travel montage in `dprose_806`).

**Assessment:** High rate matches **genre** (rapid fairy-tale summary), not a bug. Acceptable for fine-grained event labels; too dense for coarse scene boundaries. Optional post-process merge at idx 57–62.

---

#### `dprose_137` — lowest BORDER rate (14.5%), median scene 4

**Text:** *Das höllische Automobil* — comic folk tale (giant Rumbo, Frechdachs, episodic devil/miller adventures).

**Findings:**

- **Long dialogue/action blocks:** largest gap **54 sentences** without a BORDER (idx 40–94, Frechdachs ↔ miller ↔ Rumbo episode).
- **Max scene length:** 54 sentences; median scene 4 vs wave median ~2.
- **Max consecutive run idx 36–38:** “Soviel von seiner Speisekarte” → Rumbo lazy → sneeze — minor over-split at episode boundary (run of 3 only).
- **Retry idx 104:** NOBORDER — violent lasso action is climax of miller scene, not a new time/place.

**Assessment:** Conservative labeling fits **episodic, dialogue-heavy** structure—the opposite problem from over-segmentation outliers. Structurally plausible; no re-run needed. Optional manual read of idx 40–94 if validating one long “scene.”

---

#### `dprose_119` — worst consecutive BORDER run (7)

**Text:** *Der Schein trügt* — school memoir; Part 1 = “Zelt der Samojeden” frame story; Part 2 = *Ein Ferienabenteuer* (Gigas).

**Max run idx 155–161:**

| idx | Content (abbrev.) | Note |
|-----|-------------------|------|
| 155 | Conversation generalizes; relief when Heraklit joins | Part 1 coda |
| 156 | “Der Abend verlief ganz heiter…” | Same epilogue |
| 157 | “Im Zelt… urgemütlich; Geschichte nie wieder berührt” | Closing frame |
| 158 | “Heraklit blieb uns ein guter Freund…” | Final frame sentence |
| 159 | **“Ein Ferienabenteuer Ferien – schönstes Wort…”** | New **section title** — clear BORDER |
| 160 | “Weihnachtsferien, Osterferien…” | Lyric preamble to Part 2 |
| 161 | “Die Krone aber tragen die Herbstferien…” | Still holiday essay |

**Assessment:** Over-segmentation at a **structural boundary** (frame coda + new titled section + preamble)—same pattern as Roman-numeral headers in `dprose_100`. Part 2 (Gigas, idx 159+) segments normally afterward. Good post-process merge candidate (collapse 155–158 and/or 159–161). No re-run needed.

---

### Spot-check — last book `dprose_151` (wave tail)

**Text:** *Keuschheitslegende*

Not an outlier by rate (25.1%), but reviewed as the final automated review in the wave log.

- **idx 0–1 both BORDER:** idx 0 correct (story start); idx 1 debatable (shift to general authorial comment on women).
- **idx 259–263 (run of 5):** disoriented journey montage — “Sie fror” → blurred perception → train/platform → familiar sounds → enters room. Coherent reasoning; too granular for film-level scenes (pilot `dprose_806` pattern).

---

### Wave 1 conclusions

| Check | Result |
|-------|--------|
| All batch jobs succeeded | Yes |
| Parse rate ≥ 95% gate | Yes (100% after retries) |
| BORDER rate stable vs pilot | Yes (~23.5% vs 23.8%) |
| Major plot transitions captured | Yes (spot-checks confirm) |
| Border rate plausible for coarse human scenes | No — expected; fine-grained |
| Outliers indicate pipeline failure | No — text-structure driven |

---

## Wave 2 — `wave_02_eur100` (2026-06-29 — 2026-06-30)

**Manifest:** `data/manifests/waves/wave_02_eur100.json`  
**Log:** `logs/dprose/wave_wave_02_eur100_2026-06-29.log` (partial — multiple resume sessions; per-book `book_review.json` is authoritative)  
**Books:** 55 (`dprose_161` … `dprose_692`)  
**Budget cap:** $113.78 cumulative — **reached** (~$108.51 API spend excl. pilot seed; corpus total $112.92 incl. pilot)

### Aggregate metrics

| Metric | Wave 2 (55 books) | Wave 1 (15 books) | Pilot (3 books) |
|--------|-------------------|-------------------|-----------------|
| Sentences | 20,654 | 4,880 | 989 |
| Parse OK | 20,602 / 20,654 (99.8%) | 4,880 / 4,880 (100%) | 988 / 989 (99.9%) |
| BORDER rate | 22.9% | 23.4% | 23.8% |
| Median scene length | 1–4 (per book) | 1–4 | 2–3 |
| 1–2 sent scenes | 33.3–64.0% | 38.8–65.8% | 46–57% |
| Max consecutive BORDER | **9** (`dprose_516`) | 7 (`dprose_119`) | 5 (`dprose_806`) |
| Batch jobs | 55 / 55 succeeded | 15 / 15 | — |
| Wave spend | ~$87.13 | ~$21.40 | — |

**Verdict:** Wave 2 **passed**. BORDER rate and scene-length spread match Waves 1 and pilot. Wider dispersion at the low end (four books under 14% BORDER) and high end (five books over 30%) — all text-structure plausible on spot-check. One **billing incident** on `dprose_615` (see below); recovered via resume after spend-cap raise.

### Per-book summary

Aggregate parse 99.8% (50 failed keys across 20 books; all books ≥95% gate). Sorted by BORDER rate; Notes only when flagged.

| Book | Sents | Parse | BORDER | Med | Run | Notes |
|------|------:|------:|-------:|----:|----:|-------|
| dprose_661 | 514 | 100% | **8.9%** | **4** | 4 | Low — long scenes |
| dprose_692 | 345 | 100% | **12.8%** | **4** | 3 | Low |
| dprose_691 | 463 | 100% | **13.2%** | **3** | 5 | Low |
| dprose_690 | 476 | 100% | **13.7%** | 2 | 5 | Low |
| dprose_686 | 569 | 99.6% | 14.1% | 3 | 5 | 2 parse fail(s) |
| dprose_654 | 426 | 99.5% | 14.3% | 2 | 4 | 2 parse fail(s) |
| dprose_317 | 276 | 99.6% | 14.9% | 3 | 3 | 1 parse fail(s) |
| dprose_275 | 348 | 100% | 15.8% | 3 | 6 | |
| dprose_320 | 322 | 100% | 17.1% | 4 | 3 | |
| dprose_221 | 500 | 99.4% | 17.2% | 3 | 6 | 3 parse fail(s) |
| dprose_611 | 647 | 100% | 17.9% | 2 | 5 | |
| dprose_261 | 326 | 100% | 19.3% | 3 | 3 | |
| dprose_547 | 353 | 100% | 20.4% | 3 | 5 | |
| dprose_276 | 309 | 99.7% | 20.7% | 3 | 4 | 1 parse fail(s) |
| dprose_162 | 458 | 100% | 21.2% | 3 | 5 | |
| dprose_511 | 378 | 100% | 21.4% | 2.5 | 5 | |
| dprose_546 | 359 | 100% | 21.7% | 3 | 4 | |
| dprose_254 | 314 | 99.7% | 22.0% | 2.5 | 4 | 1 parse fail(s) |
| dprose_218 | 483 | 100% | 22.8% | 2 | 7 | run 7× idx 302–308 |
| dprose_259 | 218 | 100% | 22.9% | 2 | 7 | run 7× idx 7–13 |
| dprose_178 | 395 | 100% | 23.3% | 2 | 4 | |
| dprose_293 | 521 | 99.8% | 23.6% | 2 | 5 | 1 parse fail(s) |
| dprose_161 | 648 | 100% | 23.6% | 3 | 4 | Longest in wave |
| dprose_609 | 354 | 100% | 23.7% | 1 | 7 | run 7× idx 239–245 |
| dprose_454 | 366 | 100% | 24.0% | 2 | 4 | |
| dprose_574 | 255 | 99.6% | 24.3% | 3 | 5 | 1 parse fail(s) |
| dprose_435 | 271 | 97.4% | 24.4% | 1.5 | 6 | 7 parse fail(s) |
| dprose_251 | 373 | 100% | 24.4% | 2 | 7 | run 7× idx 292–298 |
| dprose_270 | 436 | 100% | 24.5% | 2 | 4 | |
| dprose_555 | 555 | 97.3% | 24.7% | 2 | 7 | 15 parse fail(s); run idx 151–157 |
| dprose_262 | 402 | 100% | 24.9% | 2 | 4 | |
| dprose_615 | 542 | 99.6% | 25.1% | 2 | 6 | Billing-cap retry |
| dprose_510 | 466 | 100% | 25.1% | 2 | 4 | |
| dprose_567 | 293 | 99.3% | 25.3% | 2 | 5 | 2 parse fail(s) |
| dprose_459 | 378 | 100% | 25.7% | 2 | 6 | |
| dprose_479 | 320 | 100% | 25.9% | 2 | 6 | |
| dprose_425 | 371 | 99.7% | 26.1% | 2 | 5 | 1 parse fail(s) |
| dprose_263 | 237 | 99.6% | 26.2% | 2 | 5 | 1 parse fail(s) |
| dprose_209 | 202 | 100% | 26.2% | 2 | 5 | |
| dprose_265 | 196 | 100% | 27.0% | 2 | 4 | |
| dprose_321 | 199 | 100% | 27.1% | 2 | 4 | |
| dprose_542 | 309 | 100% | 27.2% | 2 | 3 | |
| dprose_527 | 417 | 100% | 27.3% | 2 | **8** | run idx 159–166 |
| dprose_587 | 363 | 100% | 27.5% | 2 | 6 | |
| dprose_521 | 318 | 100% | 28.0% | 2 | 6 | |
| dprose_481 | 401 | 100% | 28.2% | 2 | 7 | run idx 247–253 |
| dprose_289 | 442 | 99.3% | 28.3% | 2 | 7 | 3 parse fail(s) |
| dprose_196 | 243 | 100% | 28.4% | 2 | 4 | |
| dprose_516 | 430 | 99.5% | 28.8% | 2 | **9** | **Worst run** idx 74–82 |
| dprose_561 | 267 | 99.3% | 28.8% | 2 | 4 | 2 parse fail(s) |
| dprose_256 | 210 | 100% | **31.0%** | 2 | 7 | High — Japanese vignette |
| dprose_166 | 330 | 99.7% | **31.2%** | 1 | 7 | High — mythic/faun episode |
| dprose_512 | 535 | 99.8% | **31.4%** | 2 | 5 | High |
| dprose_590 | 189 | 100% | **31.7%** | 2 | 3 | High |
| dprose_642 | 336 | 99.7% | **33.0%** | 1 | **8** | Highest rate; run idx 134–141 |

### Billing incident — `dprose_615`

First submit returned **0/542 parse** — every response was a Gemini API billing error (*monthly project spend cap exceeded*), not a JSON failure. Orchestrator correctly **blocked** the wave.

After raising the cap in [AI Studio → Spend](https://aistudio.google.com/spend), resume re-submitted the book:

| Attempt | Parse | Outcome |
|---------|-------|---------|
| 1st batch (`…y1s9e9xe`) | 0% | All keys = spend-cap error |
| Re-submit | **99.6%** (540/542) | 25.1% BORDER, $2.21 |

**Operational fix:** orchestrator now re-submits when on-disk predictions are below the 95% parse gate (instead of treating row count as complete).

### Parse failures (deferred retry)

50 keys across 20 books failed initial parse (prose/thinking instead of JSON — same mode as Wave 1). All books still **≥95%** parse; no wave blocker. Worst at wave end: `dprose_555` (15 fails, 97.3%), `dprose_435` (7 fails).

**Partial retry (2026-06-30):** `--retry_failed` on 21 books (pilot `dprose_100` + 20 Wave 2 books) cleared 33 keys. Remaining Wave 2 failures: **17 keys / 6 books** — see [corpus inventory](#parse-failures--corpus-inventory-pre-wave-4).

---

### Manual spot-checks — outliers

#### `dprose_661` — lowest BORDER rate (8.9%), median scene 4

**Text:** *Der Wurzgartner* — Tirol-set novella (Amtsrichter Schüttke).

**Findings:** Mean scene length **10.9** sentences vs wave median ~3; only 36% of scenes span 1–2 sentences. Long sustained dialogue/exposition blocks dominate.

**Assessment:** Conservative labeling fits **realist novella** pacing — mirror image of `dprose_137` in Wave 1. Plausible; no re-run.

---

#### `dprose_642` — highest BORDER rate (33.0%), max run 8

**Text:** Opens mid-dialogue («Ja, Sie!»).

**Findings:** Median scene **1**; 64% of scenes are 1–2 sentences. Max run idx 134–141 (8× BORDER) — rapid dialogue exchange.

**Assessment:** High rate driven by **stichomythic dialogue** and fragmentary opening, not pipeline error. Same class as fairy-tale montage outliers.

---

#### `dprose_516` — worst consecutive BORDER run (9)

**Text:** Business-correspondence frame («Er schreibt also an seinen Brüsseler oder Berliner Geschäftsfreund…»).

**Max run idx 74–82:** nine consecutive BORDERs in a compressed anecdote chain within the letter narrative.

**Assessment:** Over-segmentation at a **nested summary** boundary — same montage pattern as `dprose_806` / `dprose_119`. Good post-process merge candidate. 2 parse fails (idx 93, 101) — retry later.

---

#### `dprose_166` — high BORDER (31.2%), median scene 1

**Text:** Mythic episode («Aus dem Busch sprangen die losen Faune…»).

**Findings:** 61.5% of scenes span 1–2 sentences; max run 7× at idx 210–216.

**Assessment:** Fits **lyric/mythic** rapid beats. Expected fine-grained density.

---

#### `dprose_615` — billing + tail cluster

After successful re-submit: normal 25.1% BORDER. Notable cluster idx 130–135 (6× BORDER) in hunting-hut scene; 2 parse fails at idx 79, 119.

---

### Wave 2 conclusions

| Check | Result |
|-------|--------|
| All batch jobs succeeded | Yes (incl. `dprose_615` re-submit) |
| Parse rate ≥ 95% gate | Yes (all 55 books) |
| BORDER rate stable vs pilot | Yes (~22.9% vs 23.8%) |
| Billing incident recovered | Yes (spend-cap raise + resume) |
| Outliers indicate pipeline failure | No — text-structure driven |
| New corpus-wide pattern | Low-BORDER realist novellas (`dprose_661`–`692` tail) alongside high-BORDER dialogue/myth |

**Follow-ups before Wave 3:**

1. Top up billing; plan Wave 3 (`plan_dprose_waves.py --budget_eur 100 --exclude_completed`).
2. Raise cumulative `--max_cost_usd` cap (~$113.78 + new wave headroom).
3. Optional: `--retry_failed` on `dprose_555`, `dprose_435` if targeting 100% parse before merge.

---

## Wave 3 — `wave_03_eur100` (2026-06-30)

**Manifest:** `data/manifests/waves/wave_03_eur100.json`  
**Log:** `logs/dprose/wave_wave_03_eur100_2026-06-30.log`  
**Books:** 51 (`dprose_693` … `dprose_1029`)  
**Budget cap:** $201.67 cumulative — **not hit** (wave spend ~$85.75; corpus total $198.67)

### Aggregate metrics

| Metric | Wave 3 (51 books) | Wave 2 (55 books) | Wave 1 (15 books) | Pilot (3 books) |
|--------|-------------------|-------------------|-------------------|-----------------|
| Sentences | 20,446 | 20,654 | 4,880 | 989 |
| Parse OK | 20,419 / 20,446 (99.9%) | 20,602 / 20,654 (99.8%) | 4,880 / 4,880 (100%) | 988 / 989 (99.9%) |
| BORDER rate | 21.8% | 22.9% | 23.4% | 23.8% |
| Median scene length | 1–5 (per book) | 1–4 (per book) | 1–4 | 2–3 |
| 1–2 sent scenes | 36.7–67.9% | 33.3–64.0% | 38.8–65.8% | 46–57% |
| Max consecutive BORDER | **11** (`dprose_979`) | 9 (`dprose_516`) | 7 (`dprose_119`) | 5 (`dprose_806`) |
| Batch jobs | 51 / 51 succeeded | 55 / 55 | 15 / 15 | — |
| Wave spend | ~$85.75 | ~$87.13 | ~$21.40 | — |

**Verdict:** Wave 3 **passed**. BORDER rate and scene-length spread match prior waves. Six books under 14% BORDER (low end continues Wave 2 realist-novella pattern); seven books over 30% BORDER. New corpus-wide record: **11 consecutive BORDERs** on `dprose_979` (prior max 9 on `dprose_516`).

### Per-book summary

Aggregate parse 99.9% (27 failed keys across 13 books; all books ≥95% gate). Sorted by BORDER rate; Notes only when flagged.

| Book | Sents | Parse | BORDER | Med | Run | Notes |
|------|------:|------:|-------:|----:|----:|-------|
| dprose_702 | 423 | 100% | **11.6%** | **5** | 4 | Low — long scenes |
| dprose_701 | 357 | 100% | **12.0%** | **5** | 4 | Low — long scenes |
| dprose_697 | 325 | 99.7% | **12.3%** | 2 | 6 | Low; 1 parse fail(s) |
| dprose_693 | 290 | 100% | **12.4%** | 3 | 3 | Low |
| dprose_695 | 406 | 100% | **13.3%** | 2 | 4 | Low |
| dprose_753 | 653 | 100% | **13.3%** | 3 | 6 | Low |
| dprose_782 | 583 | 100% | 14.1% | 3 | 5 |  |
| dprose_696 | 394 | 100% | 14.5% | 3 | 3 |  |
| dprose_859 | 421 | 100% | 15.0% | 4 | 7 | run 7× idx 2–8 |
| dprose_1023 | 309 | 99.7% | 15.2% | 4 | 3 | 1 parse fail(s) |
| dprose_1022 | 538 | 100% | 15.6% | 3 | 5 |  |
| dprose_755 | 448 | 100% | 15.8% | 2 | 4 |  |
| dprose_797 | 333 | 100% | 16.5% | 4 | 5 |  |
| dprose_700 | 466 | 100% | 17.8% | 2 | 5 |  |
| dprose_926 | 356 | 99.2% | 19.9% | 3 | 4 | 3 parse fail(s) |
| dprose_938 | 382 | 100% | 20.4% | 3 | 4 |  |
| dprose_979 | 762 | 99.7% | 20.5% | 3 | **11** | **Worst run** idx 149–159; 2 parse fail(s); Longest in wave |
| dprose_884 | 518 | 100% | 20.7% | 3 | 5 |  |
| dprose_838 | 424 | 99.5% | 20.8% | 2 | 5 | 2 parse fail(s) |
| dprose_730 | 239 | 100% | 20.9% | 2 | 5 |  |
| dprose_930 | 189 | 100% | 21.2% | 2 | 4 |  |
| dprose_908 | 553 | 100% | 21.3% | 2 | 7 | run 7× idx 132–138 |
| dprose_727 | 261 | 100% | 21.5% | 2 | 5 |  |
| dprose_719 | 442 | 100% | 21.9% | 2 | 6 |  |
| dprose_1029 | 389 | 100% | 21.9% | 2 | 4 |  |
| dprose_906 | 353 | 99.7% | 22.4% | 2 | 4 | 1 parse fail(s) |
| dprose_853 | 316 | 100% | 22.8% | 2 | 4 |  |
| dprose_1021 | 417 | 100% | 22.8% | 3 | 4 |  |
| dprose_728 | 449 | 100% | 23.2% | 2 | 6 |  |
| dprose_1018 | 318 | 100% | 23.3% | 2 | 4 |  |
| dprose_1019 | 450 | 99.8% | 23.8% | 2 | **8** | run 8× idx 260–267; 1 parse fail(s) |
| dprose_879 | 683 | 100% | 23.9% | 2 | **8** | run 8× idx 44–51 |
| dprose_764 | 527 | 99.2% | 24.3% | 2 | 7 | run 7× idx 408–414; 4 parse fail(s) |
| dprose_802 | 256 | 99.6% | 24.6% | 2 | **9** | run 9× idx 83–91; 1 parse fail(s) |
| dprose_737 | 351 | 100% | 24.8% | 2 | 4 |  |
| dprose_1014 | 375 | 100% | 24.8% | 2 | 6 |  |
| dprose_1020 | 395 | 100% | 25.1% | 2 | 6 |  |
| dprose_756 | 389 | 100% | 25.4% | 2 | 6 |  |
| dprose_757 | 575 | 99.5% | 25.4% | 2 | 6 | 3 parse fail(s) |
| dprose_989 | 309 | 98.4% | 26.2% | 2 | 5 | 5 parse fail(s) |
| dprose_988 | 351 | 100% | 26.5% | 2 | 7 | run 7× idx 36–42 |
| dprose_721 | 276 | 100% | 26.8% | 2 | 5 |  |
| dprose_952 | 191 | 100% | 28.3% | 2 | 4 |  |
| dprose_904 | 549 | 99.6% | 28.6% | 2 | 5 | 2 parse fail(s) |
| dprose_738 | 390 | 100% | **30.3%** | 2 | 7 | High |
| dprose_843 | 419 | 100% | **31.0%** | 2 | 7 | High |
| dprose_953 | 327 | 100% | **32.7%** | 2 | 5 | High |
| dprose_1015 | 310 | 100% | **32.9%** | 2 | 5 | High |
| dprose_898 | 516 | 99.8% | **33.3%** | 1 | **8** | High; run 8× idx 416–423; 1 parse fail(s) |
| dprose_739 | 262 | 100% | **33.6%** | 2 | 7 | High |
| dprose_965 | 231 | 100% | **36.4%** | 2 | 6 | High; Highest rate |

### Parse failures (deferred retry)

27 keys across 13 books failed initial parse (prose/thinking instead of JSON — same mode as Waves 1–2). All books still **≥95%** parse; no wave blocker. Worst: `dprose_989` (5 fails, 98.4%), `dprose_764` (4 fails), `dprose_926` (3 fails). None retried yet — all 27 keys still open; see [corpus inventory](#parse-failures--corpus-inventory-pre-wave-4).

---

### Manual spot-checks — BORDER outliers

Wave median ~22% BORDER. **Low** = under 14% (six books at wave head); **high** = over 30% (seven books). All assessments below are from automated review stats plus reading `predictions.jsonl` around flagged indices — same failure-mode class as Waves 1–2 (genre/structure, not pipeline bugs).

#### Low BORDER cluster — Dagobert Trostler series (`dprose_693`–`dprose_702`)

Six of the seven sub-14% books are **Karl Hans Strobl detective novellas** featuring amateur sleuth Dagobert Trostler and the Grumbach / Frau Violet circle. They share sustained **single-location social scenes** (club dinners, ministerial receptions, drawing-room dialogue) where many sentences advance one continuous event.

| Book | BORDER | Med | Mean scene | Pattern |
|------|-------:|----:|-----------:|---------|
| dprose_702 | 11.6% | 5 | 8.6 | Reception at the minister-president's; 41-sent gap idx 76–117 |
| dprose_701 | 12.0% | 5 | 8.1 | Aesthetic debate at one sitting; gaps to 33 sentences |
| dprose_697 | 12.3% | 2 | 7.9 | Drawing-room search scene; 45-sent gap idx 187–232 |
| dprose_693 | 12.4% | 3 | 7.8 | *Der große Schmuckdiebstahl* — club dinner frame; title + setup BORDERs, then long meeting block |
| dprose_695 | 13.3% | 2 | 7.4 | Dramatic opening (fire in room) then extended dialogue; **70-sent gap** idx 72–142 |
| dprose_696 | 14.5% | 3 | 6.8 | Frau Violet / husband subplot — same series, just above threshold |

**Assessment:** Mirror image of Wave 2 low-BORDER realist novellas (`dprose_661`). The model correctly treats **one dinner/reception as one macro-scene** and only BORDERs on chapter titles, late arrivals (Dagobert), or time jumps (“Essenszeit geworden”). Conservative labeling is structurally plausible; optional post-process if film-level granularity is needed.

---

#### `dprose_753` — lowest non-series low outlier (13.3%), median scene 3

**Text:** *Die Geschichte vom abgerissenen Knopfe* — framed memoir (“Er ist jetzt Regierungsreferendar…”), Raabe-style retrospective narrator.

**Findings:** Mean scene **7.4** sentences; **20** gaps ≥10 sentences without a BORDER. Long flashback blocks (e.g. Lore/Berta memory) stay NOBORDER across dozens of sentences. Short BORDER burst idx 159–164 marks **return from flashback** to present-tense telling — same coda pattern as `dprose_137`.

**Assessment:** Low rate fits **embedded-anecdote** structure, not under-segmentation failure.

---

#### High BORDER — `dprose_965` (36.4%, highest in wave)

**Text:** *Der Narr auf Manegg* — historical anecdote chain (1409 Burg fire, Manesse lineage, night-women legend).

**Findings:** Median scene **2**; **68%** of scenes span 1–2 sentences. Opening idx 0–1: title + “schöner Septembertag” both BORDER. Mid-text idx 99–104: **six consecutive BORDERs** compressing multi-day waits, Ital's decline, castle fire, and genealogical digression — each sentence introduces a new temporal or anecdotal beat.

**Assessment:** **Summary/montage prose** at historical distance — same class as fairy-tale travel montage (`dprose_52`, `dprose_806`). Too fine for coarse scenes; good merge candidate at idx 99–104.

---

#### `dprose_739` — high BORDER (33.6%)

**Text:** *Aus dem Leben eines Vielgeprüften* — episodic **window diary** (“Jeden Morgen … setze ich mich ans Fenster”).

**Findings:** **62%** 1–2-sent scenes. Each vignette (coachman acquaintance, horse auction, shaving routine, “several days passed”) gets its own BORDER. Max run idx 178–184: auction announcement → chapter close → time jump → return to window.

**Assessment:** High rate driven by **essayistic/episodic form** — one BORDER per anecdote is expected for event-level labels.

---

#### `dprose_898` — high BORDER (33.3%), median scene **1**

**Text:** *Die Seele* — mystical cloister monologue (ecstasy, Generalvicar's arrival).

**Findings:** **66%** 1–2-sent scenes; only **10** gaps ≥10 sents. Max run idx 416–423: each sentence is a new spiritual beat (“Mich läßt man gehen” → “Gestern…” → “Jubel, Jubel!” → “Hochzeitsnacht, meine Seele”). Median scene 1 = half of all “scenes” are single sentences.

**Assessment:** **Lyric/ecstatic** interior monologue — inherently over-segmented at sentence level. Same class as mythic `dprose_166` (Wave 2).

---

#### `dprose_843` — high BORDER (31.0%)

**Text:** Opens on intimate nocturnal image (moonbeam in her eyes).

**Findings:** **64%** short scenes. Cluster idx 354–360: rapid emotional reversals (throws light away → kneels → weeps → dialogue beats) — seven BORDERs in seven sentences during climax.

**Assessment:** **Stichomythic/emotional dialogue** at scene peak — not a parsing error; merge candidate for film-level boundaries.

---

#### `dprose_953` — high BORDER (32.7%)

**Text:** Opens mid-oration on the “Geschlecht der Kabisse” — **fantastic/historical** vignette.

**Findings:** Mean scene **3.0**; tail cluster idx 317–321: protagonist's reflective eating → humorists join → time jump → business sale — each shift BORDERed.

**Assessment:** Fits **compressed anecdotal** prose (cf. Swiss/German Novellen tradition). Plausible fine-grained labels.

---

#### `dprose_1015` — high BORDER (32.9%)

**Text:** *Ein geistlich Armer* — **Plattdeutsch** dialect tale (Hans, Wieb, Höker Rasmussen).

**Findings:** **65%** 1–2-sent scenes. Cluster idx 128–132: shift from internal grief to pancake errand → “day after funeral” → encounter at Steinwall — dialect dialogue and time markers each trigger BORDER.

**Assessment:** Dialect + **funeral-to-daily-life transition** produces dense boundaries; structurally similar to `dprose_119` frame/part boundaries.

---

#### `dprose_738` — high BORDER (30.3%, threshold)

**Text:** Mother–child reunion scene opening; mid-text shifts to **object narrator** (“Dieser Besen war ich”).

**Findings:** Max run idx 173–179: broom acquires voice → journey through streets → “half-year” summary → meta “I will be brief” → young couple introduced — **seven BORDERs** across frame transitions.

**Assessment:** **Nested narrative frames** (object tale inside social satire) — each frame opening correctly BORDERed; over-segmentation only if merging across frame levels.

---

#### Structural outlier (normal BORDER rate) — `dprose_979` — record 11× run at 20.5%

**Text:** *Die überlaute Frau Bautz* — Davos sanatorium dinner / social novel (762 sentences, longest in wave).

**Findings:** BORDER rate is **normal** (20.5%), but idx 149–159 are **eleven consecutive BORDERs** as Sylvester leaves dinner → headache → street → bar → new character (girl in blue jacket). Each physical micro-step (air, headache, street, lieutenant, bar, elbow, turn, see girl) is its own event.

**Assessment:** **Montage exit sequence** — same pattern as `dprose_119` frame coda and `dprose_516` letter anecdote chain. Corpus-wide worst run; strong post-process merge candidate (collapse 149–159). Not a reason to re-run.

---

#### Near-miss — `dprose_859` (15.0%, opening run 7×)

**Text:** *Als Peter Hille reich war* — **meta-literary memoir** (Julius Hart recalls poet Peter Hille).

**Findings:** Low overall rate but idx 2–8 are seven BORDERs in the **article preamble** (introduction → “Mitte der sechziger Jahre” → “lived with me” → posthumous works → years unseen → sudden arrival → doorbell scene).

**Assessment:** **Periodical-essay structure** with explicit time stamps — over-segmented opening, long calm middle (median scene 4, 16 gaps ≥10). Borderline low; opening cluster is the actionable merge target.

---

### Wave 3 conclusions

| Check | Result |
|-------|--------|
| All batch jobs succeeded | Yes |
| Parse rate ≥ 95% gate | Yes (all 51 books) |
| BORDER rate stable vs pilot | Yes (~21.8% vs 23.8%) |
| Outliers indicate pipeline failure | No — text-structure driven (see manual spot-checks above) |
| New corpus-wide pattern | Record 11× BORDER run (`dprose_979`); Dagobert-series low-BORDER cluster (`dprose_693`–`dprose_702`); diary/mystic high-BORDER tail |

**Follow-ups before Wave 4:**

1. Plan Wave 4 (`plan_dprose_waves.py --budget_eur 100 --exclude_completed`).
2. Raise cumulative `--max_cost_usd` cap (~$198.67 + new wave headroom).
3. Optional: corpus-wide `--retry_failed` on 19 books / 44 keys (~$0.19) if targeting 100% parse before merge — **not required** for the 95% gate.

---

## Wave 4 — `wave_04_eur100` (2026-06-30 — 2026-07-01)

**Manifest:** `data/manifests/waves/wave_04_eur100.json`  
**Log:** `logs/dprose/wave_wave_04_eur100_2026-06-30.log` (primary; tail resume continued 2026-07-01)  
**Books:** 55 (`dprose_1040` … `dprose_1535`)  
**Budget cap:** $287.47 cumulative — **not hit** (wave spend ~$87.53; corpus total $286.20)

### Aggregate metrics

| Metric | Wave 4 (55 books) | Wave 3 (51 books) | Wave 2 (55 books) | Wave 1 (15 books) | Pilot (3 books) |
|--------|-------------------|-------------------|-------------------|-------------------|-----------------|
| Sentences | 20,735 | 20,446 | 20,654 | 4,880 | 989 |
| Parse OK | 20,723 / 20,735 (99.9%) | 20,419 / 20,446 (99.9%) | 20,602 / 20,654 (99.8%) | 4,880 / 4,880 (100%) | 988 / 989 (99.9%) |
| BORDER rate | 22.2% | 21.8% | 22.9% | 23.4% | 23.8% |
| Median scene length | 1–5 (per book) | 1–5 (per book) | 1–4 (per book) | 1–4 | 2–3 |
| 1–2 sent scenes | 36.4–72.6% | 36.7–67.9% | 33.3–64.0% | 38.8–65.8% | 46–57% |
| Max consecutive BORDER | **13** (`dprose_1060`) | 11 (`dprose_979`) | 9 (`dprose_516`) | 7 (`dprose_119`) | 5 (`dprose_806`) |
| Batch jobs | 55 / 55 succeeded | 51 / 51 | 55 / 55 | 15 / 15 | — |
| Wave spend | ~$87.53 | ~$85.75 | ~$87.13 | ~$21.40 | — |

**Verdict:** Wave 4 **passed**. BORDER rate and scene-length spread match prior waves. One book under 14% BORDER (`dprose_1075`); six books over 30% BORDER. New corpus-wide record: **13 consecutive BORDERs** on `dprose_1060` (prior max 11 on `dprose_979`). Highest BORDER rate in corpus so far: **41.4%** on `dprose_1113`.

### Operational incident — transient 503 on tail resume

Run halted at book **46/55** (`dprose_1474`) when Gemini Files API returned **503 Service Unavailable** during batch JSONL upload (batch file written locally; upload never completed). Resume on **2026-07-01** with `--resume` skipped 45 completed books and finished the remaining 9 without re-work. In-flight resume for `dprose_1506` (existing `job_meta.json`, no predictions yet) also succeeded.

### Per-book summary

Aggregate parse 99.9% (12 failed keys across 10 books; all books ≥95% gate). Sorted by BORDER rate; Notes only when flagged.

| Book | Sents | Parse | BORDER | Med | Run | Notes |
|------|------:|------:|-------:|----:|----:|-------|
| dprose_1075 | 388 | 100% | **11.1%** | 5 | 4 | Low |
| dprose_1272 | 390 | 100% | 14.4% | 4 | 4 |  |
| dprose_1280 | 476 | 100% | 14.5% | 2 | 4 |  |
| dprose_1277 | 592 | 100% | 14.5% | 3 | 4 |  |
| dprose_1516 | 493 | 100% | 15.8% | 3 | 4 |  |
| dprose_1462 | 584 | 583/584 (99.8%) | 16.1% | 2 | 4 | 1 parse fail(s) |
| dprose_1306 | 407 | 100% | 16.5% | 3 | 3 |  |
| dprose_1088 | 615 | 100% | 16.9% | 3 | 7 |  |
| dprose_1049 | 452 | 451/452 (99.8%) | 17.0% | 2 | 4 | 1 parse fail(s) |
| dprose_1284 | 294 | 100% | 17.3% | 1 | 6 |  |
| dprose_1338 | 466 | 100% | 17.6% | 3 | 5 |  |
| dprose_1514 | 317 | 100% | 17.7% | 2 | 4 |  |
| dprose_1392 | 554 | 100% | 17.9% | 3 | 3 |  |
| dprose_1353 | 483 | 100% | 18.6% | 3 | 6 |  |
| dprose_1287 | 363 | 100% | 18.7% | 3 | 4 |  |
| dprose_1307 | 302 | 100% | 19.9% | 3 | 4 |  |
| dprose_1303 | 322 | 321/322 (99.7%) | 19.9% | 2 | 4 | 1 parse fail(s) |
| dprose_1302 | 382 | 100% | 19.9% | 2 | 4 |  |
| dprose_1356 | 440 | 439/440 (99.8%) | 20.0% | 1 | 5 | 1 parse fail(s) |
| dprose_1069 | 294 | 100% | 20.1% | 3 | 4 |  |
| dprose_1282 | 244 | 100% | 20.5% | 3 | 4 |  |
| dprose_1333 | 245 | 100% | 20.8% | 2 | 3 |  |
| dprose_1366 | 528 | 100% | 20.8% | 2 | 5 |  |
| dprose_1367 | 260 | 100% | 21.2% | 2 | 4 |  |
| dprose_1041 | 392 | 100% | 21.2% | 1 | 8 |  |
| dprose_1319 | 406 | 405/406 (99.8%) | 21.2% | 2 | 5 | 1 parse fail(s) |
| dprose_1332 | 345 | 344/345 (99.7%) | 21.7% | 2 | 6 | 1 parse fail(s) |
| dprose_1518 | 393 | 100% | 21.9% | 2 | 5 |  |
| dprose_1363 | 440 | 439/440 (99.8%) | 22.5% | 3 | 6 | 1 parse fail(s) |
| dprose_1314 | 229 | 100% | 22.7% | 2 | 8 |  |
| dprose_1265 | 358 | 100% | 22.9% | 2 | 6 |  |
| dprose_1531 | 242 | 100% | 23.1% | 3 | 3 |  |
| dprose_1530 | 207 | 100% | 23.2% | 2 | 6 |  |
| dprose_1040 | 378 | 100% | 23.5% | 2 | 6 |  |
| dprose_1345 | 494 | 493/494 (99.8%) | 23.7% | 2 | 4 | 1 parse fail(s) |
| dprose_1534 | 286 | 100% | 23.8% | 2.5 | 5 |  |
| dprose_1318 | 498 | 100% | 24.1% | 2 | 5 |  |
| dprose_1529 | 268 | 100% | 24.6% | 3 | 4 |  |
| dprose_1443 | 180 | 100% | 25.0% | 2 | 5 |  |
| dprose_1404 | 379 | 100% | 25.1% | 2 | 5 |  |
| dprose_1308 | 259 | 100% | 25.5% | 2 | 6 |  |
| dprose_1472 | 467 | 100% | 25.7% | 2 | 5 |  |
| dprose_1046 | 548 | 100% | 26.1% | 2 | 6 |  |
| dprose_1269 | 216 | 100% | 26.4% | 2 | 4 |  |
| dprose_1309 | 360 | 100% | 27.2% | 2 | 7 |  |
| dprose_1045 | 659 | 100% | 28.2% | 2 | 10 | run 10×; Longest in wave |
| dprose_1506 | 221 | 100% | 29.4% | 2 | 5 |  |
| dprose_1096 | 400 | 100% | 29.5% | 2 | 9 | run 9× |
| dprose_1535 | 378 | 376/378 (99.5%) | 29.9% | 2 | 6 | 2 parse fail(s) |
| dprose_1474 | 226 | 100% | 31.9% | 2 | 5 | High |
| dprose_1156 | 385 | 383/385 (99.5%) | 33.2% | 2 | 6 | 2 parse fail(s); High |
| dprose_1060 | 522 | 100% | 34.1% | 1 | 13 | High; **worst run** |
| dprose_1469 | 240 | 100% | 35.0% | 2 | 4 | High |
| dprose_1347 | 212 | 100% | 35.8% | 2 | 6 | High |
| dprose_1113 | 256 | 100% | **41.4%** | 1 | 10 | High; **highest rate** |

### Parse failures (deferred retry)

12 keys across 10 books failed initial parse (prose/thinking instead of JSON — same mode as Waves 1–3). All books still **≥95%** parse; no wave blocker. Worst: `dprose_1535` and `dprose_1156` (2 fails each, 99.5%). None retried yet — see [corpus inventory](#parse-failures--corpus-inventory-post-wave-4).

| Book | Parse | Failed keys |
|------|------:|-------------|
| dprose_1535 | 376/378 (99.5%) | `:173`, `:251` |
| dprose_1156 | 383/385 (99.5%) | `:21`, `:274` |
| dprose_1303 | 321/322 (99.7%) | `:19` |
| dprose_1332 | 344/345 (99.7%) | `:134` |
| dprose_1319 | 405/406 (99.8%) | `:298` |
| dprose_1356 | 439/440 (99.8%) | `:90` |
| dprose_1363 | 439/440 (99.8%) | `:3` |
| dprose_1049 | 451/452 (99.8%) | `:303` |
| dprose_1345 | 493/494 (99.8%) | `:165` |
| dprose_1462 | 583/584 (99.8%) | `:572` |

---

### Manual spot-checks — BORDER outliers

Wave median ~22% BORDER. **Low** = under 14% (one book); **high** = over 30% (six books).

#### `dprose_1075` — lowest BORDER rate (11.1%), median scene 5

**Text:** Dialogue-heavy philosophical sketch (professor, light, social observation).

**Findings:** Mean scene **8.8** sentences; only **36%** of scenes span 1–2 sentences (lowest short-scene rate in wave). Long sustained conversation blocks dominate; max run only 4× at idx 44–47 (professor's aside cluster).

**Assessment:** Conservative labeling fits **extended dialogue** structure — same class as Wave 2 `dprose_661` and Wave 3 Dagobert-series novellas. Plausible; no re-run.

---

#### `dprose_1113` — highest BORDER rate (41.4%), median scene 1

**Text:** *Der Feldhase* — naturalist hunting vignette (storm, hares, cabbage gardens).

**Findings:** **73%** of scenes span 1–2 sentences; median scene **1**. Opening idx 0–2: storm landscape + hare movement each BORDERed. Max run idx 107–116: **ten consecutive BORDERs** compressing hare escapes, trail counts, and field observations — each micro-beat is its own event.

**Assessment:** **Naturalist/montage prose** at sentence granularity — corpus-wide highest BORDER rate, same class as lyric montage (`dprose_965`, `dprose_898`). Too fine for coarse scenes; strong merge candidate at idx 107–116. Not a pipeline defect.

---

#### `dprose_1060` — record 13× run at 34.1% BORDER

**Text:** Philosophical dialogue opening («Was ist »liebe« und was ist »Frau«?»).

**Findings:** Median scene **1**; **70%** 1–2-sent scenes. Max run idx 438–450: **thirteen consecutive BORDERs** — ant-colony allegory montage («Den ganzen Staat für einen Menschen…» → «Wie weise sind doch die Einrichtungen der Ameisen!» → «Mögen die Menschen machen, was sie wollen…»). Each sentence is a new argumentative beat in the insect parable.

**Assessment:** **Allegorical essay montage** — new corpus-wide worst consecutive run (prior max 11 on `dprose_979`). Same montage pattern as frame coda / travel summary outliers. Good post-process merge candidate (collapse 438–450). No re-run needed.

---

#### `dprose_1045` — longest book (659 sents), run 10× at 28.2%

**Text:** Long-form narrative (659 sentences — longest in wave).

**Findings:** BORDER rate is normal (28.2%) but idx 385–394 are **ten consecutive BORDERs** in a compressed transition sequence. Otherwise typical 2-sent median scenes.

**Assessment:** **Montage exit/transition** at structural boundary — same class as `dprose_979` idx 149–159. Merge candidate; not a parse or pipeline issue.

---

#### `dprose_1474` — high BORDER (31.9%)

**Text:** *Tante Guttraud* — Jewish family memoir (Shabbes fish, aunt's martyrdom narrative).

**Findings:** Opening idx 0–3: title + exposition cluster. Tail idx 220–224: **five consecutive BORDERs** at story close (grave visit → mother's question → silent answer). This was the book interrupted by the 503 upload error; completed cleanly on resume with 100% parse.

**Assessment:** High rate fits **memoir frame + nested flashback** structure. 503 incident was transient API-side only.

---

### Wave 4 conclusions

| Check | Result |
|-------|--------|
| All batch jobs succeeded | Yes (incl. tail resume after 503) |
| Parse rate ≥ 95% gate | Yes (all 55 books) |
| BORDER rate stable vs pilot | Yes (~22.2% vs 23.8%) |
| Transient API failures recovered | Yes (`--resume` on 2026-07-01) |
| Outliers indicate pipeline failure | No — text-structure driven |
| New corpus-wide records | 13× BORDER run (`dprose_1060`); 41.4% BORDER rate (`dprose_1113`) |

**Follow-ups before Wave 5:**

1. Plan Wave 5 (`plan_dprose_waves.py --budget_eur 100 --exclude_completed`).
2. Raise cumulative `--max_cost_usd` cap (~$286.20 + new wave headroom).
3. Optional: corpus-wide `--retry_failed` on 26 books / 49 keys (~$0.20) if targeting 100% parse before merge — **not required** for the 95% gate.

---

## Wave 5+
