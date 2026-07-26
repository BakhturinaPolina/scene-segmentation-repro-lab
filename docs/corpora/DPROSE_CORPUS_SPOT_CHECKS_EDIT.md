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
| dprose_119 | 220 | 28.2% | 2 | **7** | Run idx 155–161: frame coda + Part 2 title |
| dprose_51 | 238 | 32.4% | 2 | 4 | High — fairy-tale exposition |
| dprose_52 | 229 | **32.8%** | 1 | **6** | Highest rate; travel montage idx 57–62 (6× BORDER) |
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
| dprose_218 | 483 | 100% | 22.8% | 2 | 7 | run 7× idx 302–308 |
| dprose_259 | 218 | 100% | 22.9% | 2 | 7 | run 7× idx 7–13 |
| dprose_161 | 648 | 100% | 23.6% | 3 | 4 | Longest in wave |
| dprose_609 | 354 | 100% | 23.7% | 1 | 7 | run 7× idx 239–245 |
| dprose_251 | 373 | 100% | 24.4% | 2 | 7 | run 7× idx 292–298 |
| dprose_555 | 555 | 97.3% | 24.7% | 2 | 7 | 15 parse fail(s); run idx 151–157 |
| dprose_527 | 417 | 100% | 27.3% | 2 | **8** | run idx 159–166 |
| dprose_481 | 401 | 100% | 28.2% | 2 | 7 | run idx 247–253 |
| dprose_516 | 430 | 99.5% | 28.8% | 2 | **9** | **Worst run** idx 74–82 |
| dprose_256 | 210 | 100% | **31.0%** | 2 | 7 | High — Japanese vignette |
| dprose_166 | 330 | 99.7% | **31.2%** | 1 | 7 | High — mythic/faun episode |
| dprose_512 | 535 | 99.8% | **31.4%** | 2 | 5 | High |
| dprose_590 | 189 | 100% | **31.7%** | 2 | 3 | High |
| dprose_642 | 336 | 99.7% | **33.0%** | 1 | **8** | Highest rate; run idx 134–141 |

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

**Assessment:** Mirror image of Wave 2 low-BORDER realist novellas (`dprose_661`). The model correctly treats **one dinner/reception as one macro-scene** and only BORDERs on chapter titles, late arrivals (Dagobert), or time jumps (“Essenszeit geworden”). Conservative labeling is structurally plausible; optional post-process if coarser scene granularity is needed.

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

**Assessment:** **Stichomythic/emotional dialogue** at scene peak — not a parsing error; merge candidate for coarser scene boundaries.

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

1. ~~Plan Wave 5~~ — done (`wave_05_eur100`, 2026-07-01 — 2026-07-02).
2. ~~Raise cumulative `--max_cost_usd` cap~~ — raised to ~$378.59.
3. Optional: corpus-wide `--retry_failed` on 42 books / 72 keys (~$0.29) if targeting 100% parse before merge — **not required** for the 95% gate.

---

## Wave 5 — `wave_05_eur100` (2026-07-01 — 2026-07-02)

**Manifest:** `data/manifests/waves/wave_05_eur100.json`  
**Log:** `logs/dprose/wave_wave_05_eur100_2026-07-01.log`  
**Books:** 59 (`dprose_1537` … `dprose_1970`)  
**Budget cap:** $378.59 — **not hit** (wave spend ~$88.76; cumulative $374.96)

Six books were already complete at session start (`dprose_1537`, `dprose_1545`, `dprose_1580`, `dprose_1588`, `dprose_1593`, `dprose_1617`); **53** processed in the single session (2026-07-02 UTC). One in-flight resume (`dprose_1647`) succeeded. No API incidents.

### Aggregate metrics

| Metric | Wave 5 (59 books) | Wave 4 (55 books) | Wave 3 (51 books) | Wave 2 (55 books) | Pilot (3 books) |
|--------|-------------------|-------------------|-------------------|-------------------|-----------------|
| Sentences | 20,486 | 20,735 | 19,089 | 19,000 | 989 |
| Parse OK | 20,463 / 20,486 (99.89%) | 20,723 / 20,735 (99.9%) | 19,067 / 19,089 (99.9%) | 18,985 / 19,000 (99.9%) | 988 / 989 (99.9%) |
| BORDER rate | 24.3% | 22.2% | 21.8% | 22.9% | 23.8% |
| Median scene length | 1–4 (per book) | 1–5 (per book) | 1–5 (per book) | 1–4 (per book) | 2–3 |
| 1–2 sent scenes | 43.4–69.8% | 36.4–72.6% | 36.7–67.9% | 33.3–64.0% | 46–57% |
| Max consecutive BORDER | **9** (`dprose_1712`) | 13 (`dprose_1060`) | 11 (`dprose_979`) | 9 (`dprose_516`) | 5 (`dprose_806`) |
| Batch jobs | 59 / 59 succeeded | 55 / 55 | 51 / 51 | 55 / 55 | — |
| Wave spend | ~$88.76 | ~$87.53 | ~$85.75 | ~$87.13 | — |

**Verdict:** Wave 5 **passed**. BORDER rate ticked up slightly (~24.3% vs ~22% prior waves) but remains within pilot range. Six books over 30% BORDER; none under 14% (lowest: `dprose_1593` at 15.0%). Worst consecutive run **9×** on `dprose_1712` — below Wave 4's corpus record (13× on `dprose_1060`). Highest BORDER rate: **36.7%** on `dprose_1913` (below Wave 4's 41.4% on `dprose_1113`). Wave 5 added **23** new parse-fail keys across **16** books; worst book `dprose_1925` (5 fails, 98.2%).

### Per-book summary

Aggregate parse 99.89% (23 failed keys across 16 books; all books ≥95% gate). Sorted by BORDER rate; Notes only when flagged.

| Book | Sents | Parse | BORDER | Med | Run | Notes |
|------|------:|------:|-------:|----:|----:|-------|
| dprose_1593 | 266 | 265/266 (99.6%) | 15.0% | 4 | 4 | 1 parse fail(s); near-low |
| dprose_1835 | 334 | 100% | 15.6% | 4 | 4 |  |
| dprose_1800 | 464 | 100% | 17.5% | 3 | 3 |  |
| dprose_1902 | 440 | 437/440 (99.3%) | 17.5% | 2 | 5 | 3 parse fail(s) |
| dprose_1824 | 251 | 100% | 18.3% | 2 | 5 |  |
| dprose_1757 | 401 | 400/401 (99.8%) | 18.7% | 3 | 6 | 1 parse fail(s) |
| dprose_1854 | 422 | 100% | 19.4% | 3 | 4 |  |
| dprose_1942 | 211 | 100% | 19.4% | 3 | 3 |  |
| dprose_1772 | 347 | 345/347 (99.4%) | 19.6% | 2 | 4 | 2 parse fail(s) |
| dprose_1802 | 456 | 455/456 (99.8%) | 19.7% | 2 | 4 | 1 parse fail(s) |
| dprose_1580 | 399 | 100% | 20.1% | 2 | 4 |  |
| dprose_1735 | 360 | 359/360 (99.7%) | 20.3% | 3 | 5 | 1 parse fail(s) |
| dprose_1734 | 276 | 100% | 20.7% | 3 | 2 |  |
| dprose_1928 | 304 | 303/304 (99.7%) | 21.1% | 3 | 5 | 1 parse fail(s) |
| dprose_1811 | 389 | 100% | 21.3% | 3 | 6 |  |
| dprose_1876 | 308 | 100% | 21.4% | 2 | 6 |  |
| dprose_1537 | 424 | 100% | 21.7% | 2 | 5 |  |
| dprose_1970 | 407 | 100% | 21.9% | 2 | 5 |  |
| dprose_1801 | 334 | 100% | 22.2% | 3 | 4 |  |
| dprose_1740 | 340 | 100% | 22.4% | 2 | 6 |  |
| dprose_1823 | 447 | 100% | 23.0% | 2 | 5 |  |
| dprose_1814 | 395 | 100% | 23.3% | 2 | 5 |  |
| dprose_1690 | 294 | 100% | 23.5% | 2 | 4 |  |
| dprose_1810 | 480 | 479/480 (99.8%) | 23.5% | 2 | 4 | 1 parse fail(s) |
| dprose_1939 | 213 | 100% | 23.9% | 2 | 5 |  |
| dprose_1834 | 573 | 100% | 24.1% | 2 | 6 | Longest in wave |
| dprose_1700 | 522 | 100% | 24.1% | 3 | 5 |  |
| dprose_1830 | 301 | 100% | 24.3% | 2 | 7 |  |
| dprose_1617 | 489 | 100% | 24.5% | 2 | 5 |  |
| dprose_1925 | 271 | 266/271 (98.2%) | 24.7% | 2 | 4 | 5 parse fail(s) |
| dprose_1848 | 359 | 358/359 (99.7%) | 24.8% | 2 | 6 | 1 parse fail(s) |
| dprose_1545 | 185 | 100% | 24.9% | 1 | 4 |  |
| dprose_1808 | 316 | 315/316 (99.7%) | 25.0% | 2 | 6 | 1 parse fail(s) |
| dprose_1647 | 493 | 100% | 25.2% | 2 | 6 |  |
| dprose_1723 | 306 | 100% | 25.5% | 2 | 5 |  |
| dprose_1831 | 371 | 100% | 25.6% | 2 | 5 |  |
| dprose_1588 | 400 | 399/400 (99.8%) | 25.8% | 2 | 6 | 1 parse fail(s) |
| dprose_1729 | 314 | 313/314 (99.7%) | 25.8% | 2 | 5 | 1 parse fail(s) |
| dprose_1820 | 284 | 100% | 26.1% | 2 | 5 |  |
| dprose_1726 | 296 | 295/296 (99.7%) | 26.4% | 2 | 6 | 1 parse fail(s) |
| dprose_1733 | 384 | 100% | 26.6% | 2 | 6 |  |
| dprose_1904 | 359 | 100% | 26.7% | 2 | 5 |  |
| dprose_1937 | 299 | 100% | 26.8% | 2 | 6 |  |
| dprose_1677 | 337 | 100% | 27.0% | 2 | 7 |  |
| dprose_1940 | 297 | 100% | 27.3% | 2 | 4 |  |
| dprose_1853 | 369 | 100% | 27.4% | 2 | 4 |  |
| dprose_1838 | 303 | 100% | 27.4% | 2 | 4 |  |
| dprose_1930 | 355 | 354/355 (99.7%) | 27.9% | 2 | 6 | 1 parse fail(s) |
| dprose_1927 | 177 | 100% | 28.2% | 1 | 4 |  |
| dprose_1857 | 348 | 100% | 28.4% | 2 | 4 |  |
| dprose_1695 | 259 | 100% | 29.3% | 2 | 6 |  |
| dprose_1712 | 569 | 100% | 29.5% | 2 | 9 | run 9×; **worst run** |
| dprose_1768 | 414 | 100% | 30.0% | 2 | 8 |  |
| dprose_1724 | 253 | 100% | **30.8%** | 2 | 5 | High |
| dprose_1825 | 422 | 100% | **31.0%** | 2 | 6 | High |
| dprose_1839 | 206 | 100% | **32.0%** | 2 | 4 | High |
| dprose_1924 | 230 | 100% | **32.2%** | 2 | 4 | High |
| dprose_1855 | 294 | 293/294 (99.7%) | **34.4%** | 2 | 6 | High; 1 parse fail(s) |
| dprose_1913 | 169 | 100% | **36.7%** | 2 | 5 | High; **highest rate** |

### Parse failures (deferred retry)

23 keys across 16 books failed initial parse (prose/thinking instead of JSON — same mode as Waves 1–4). All books still **≥95%** parse; no wave blocker. Worst: `dprose_1925` (5 fails, 98.2%). None retried yet — see [corpus inventory](#parse-failures--corpus-inventory-post-wave-5).

| Book | Parse | Failed keys |
|------|------:|-------------|
| dprose_1925 | 266/271 (98.2%) | `:143`, `:144`, `:145`, `:155`, `:157` |
| dprose_1902 | 437/440 (99.3%) | `:36`, `:37`, `:39` |
| dprose_1772 | 345/347 (99.4%) | `:102`, `:104` |
| dprose_1593 | 265/266 (99.6%) | `:173` |
| dprose_1855 | 293/294 (99.7%) | `:287` |
| dprose_1726 | 295/296 (99.7%) | `:70` |
| dprose_1928 | 303/304 (99.7%) | `:232` |
| dprose_1729 | 313/314 (99.7%) | `:194` |
| dprose_1808 | 315/316 (99.7%) | `:191` |
| dprose_1930 | 354/355 (99.7%) | `:9` |
| dprose_1848 | 358/359 (99.7%) | `:198` |
| dprose_1735 | 359/360 (99.7%) | `:210` |
| dprose_1588 | 399/400 (99.8%) | `:315` |
| dprose_1757 | 400/401 (99.8%) | `:293` |
| dprose_1802 | 455/456 (99.8%) | `:267` |
| dprose_1810 | 479/480 (99.8%) | `:184` |

---

### Manual spot-checks — BORDER outliers

Wave median ~24% BORDER. **Low** = under 14% (none); **high** = over 30% (six books).

#### `dprose_1593` — near-lowest BORDER rate (15.0%), median scene 4

**Text:** Sylt beach dialogue — Prussian justice official Löhnefinke and a colleague (moonlight, sea, life story).

**Findings:** Mean scene **6.7** sentences; only **43%** of scenes span 1–2 sentences. Long sustained dialogue blocks dominate; max run only 4× at idx 20–23 (outdoor transition cluster).

**Assessment:** Conservative labeling fits **extended dialogue** structure — same class as Wave 4 `dprose_1075` and Dagobert-series novellas. Plausible; no re-run.

---

#### `dprose_1913` — highest BORDER rate (36.7%), median scene 2

**Text:** Fairy tale — fisherman and water nymph (magical fly, marriage oath, waiting).

**Findings:** **70%** of scenes span 1–2 sentences. Opening idx 0–2: title + lantern command each BORDERed. Cluster idx 17–19: return home → prosperity summary → longing — three BORDERs across time jumps. idx 91–95: **five consecutive BORDERs** at story climax (prophecy / punishment beat).

**Assessment:** **Fairy-tale episodic structure** with explicit time markers («fortan», «fast ein Monat», «Als er wieder zu sich kam») — each beat is its own event. Same class as lyric montage outliers; merge candidate at idx 17–19 and 91–95. Not a pipeline defect. Rate below Wave 4 record (`dprose_1113` 41.4%).

---

#### `dprose_1712` — wave-worst 9× run at 29.5% BORDER

**Text:** Munich social satire — Herr Schefbeck's death and funeral (Olly, Frau von Börnerau).

**Findings:** Median scene **2**; **63%** 1–2-sent scenes. Max run idx 277–285: **nine consecutive BORDERs** — courtship climax → «unerhörte Stunde» → flashback «damals» → present funeral bed → wife summoned → phone montage → car → mortuary arrival. Each micro-shift (past/present, internal/external, location) is its own BORDER.

**Assessment:** **Death/funeral montage** with rapid past–present cuts — same montage pattern as `dprose_1060` and `dprose_979`. Good post-process merge candidate (collapse 277–285). Run length 9× is below corpus record (13×). No re-run needed.

---

#### `dprose_1855` — high BORDER (34.4%), frame narrator

**Text:** *Die Weissagung* — narrator visits Freiherr von Schottenegg's Tyrolean estate; character biography with acting past.

**Findings:** **62%** short scenes. Opening idx 0–7: chapter title + estate + narrator introduction + hobby list + acting flashback each BORDERed. Max run idx 106–111: **six consecutive BORDERs** in prophecy/vision sequence.

**Assessment:** **Framed biography** with explicit temporal shifts («in früherer Zeit», «gleich nach dem Tode des Vaters») — over-segmentation at exposition boundaries. Merge candidate at idx 106–111; not a parse issue.

---

#### `dprose_1925` — worst parse rate in wave (98.2%, 5 fails)

**Text:** Opens on November weather / illness — realist domestic sketch.

**Findings:** Five failed keys at idx 143–145, 155, 157 (clustered mid-text). BORDER rate normal (24.7%); parse failures only. Same prose/thinking-instead-of-JSON mode as prior waves.

**Assessment:** **Retry candidate** via `--retry_failed`; no full-book re-run. Cluster location suggests a dense dialogue or dialect passage — inspect after retry.

---

### Wave 5 conclusions

| Check | Result |
|-------|--------|
| All batch jobs succeeded | Yes (incl. in-flight resume for `dprose_1647`) |
| Parse rate ≥ 95% gate | Yes (all 59 books) |
| BORDER rate stable vs pilot | Yes (~24.3% vs 23.8%; slight uptick, within range) |
| Transient API failures | None this wave |
| Outliers indicate pipeline failure | No — text-structure driven |
| New corpus-wide records | None — worst run 9× (below Wave 4's 13×); highest rate 36.7% (below Wave 4's 41.4%) |

**Follow-ups before Wave 6:**

1. ~~Plan Wave 6~~ — done (`wave_06_eur100`, 2026-07-02 — 2026-07-03).
2. ~~Raise cumulative `--max_cost_usd` cap~~ — raised to ~$467.35.
3. Optional: corpus-wide `--retry_failed` on 42 books / 72 keys (~$0.29) if targeting 100% parse before merge — **not required** for the 95% gate.

---

## Wave 6 — `wave_06_eur100` (2026-07-02 — 2026-07-03)

**Manifest:** `data/manifests/waves/wave_06_eur100.json`  
**Log:** `logs/dprose/wave_wave_06_eur100_2026-07-02.log`  
**Books:** 58 (`dprose_1983` … `dprose_2312`)  
**Budget cap:** $467.35 — **not hit** (wave spend ~$88.90; cumulative $463.86)

All 58 books processed in a single session (~4.4h). No API incidents; no upload throttling.

### Aggregate metrics

| Metric | Wave 6 (58 books) | Wave 5 (59 books) | Wave 4 (55 books) | Wave 3 (51 books) | Pilot (3 books) |
|--------|-------------------|-------------------|-------------------|-------------------|-----------------|
| Sentences | 20,333 | 20,486 | 20,735 | 19,089 | 989 |
| Parse OK | 20,298 / 20,333 (99.83%) | 20,463 / 20,486 (99.89%) | 20,723 / 20,735 (99.9%) | 19,067 / 19,089 (99.9%) | 988 / 989 (99.9%) |
| BORDER rate | 25.7% | 24.3% | 22.2% | 21.8% | 23.8% |
| Median scene length | 1–4 (per book) | 1–4 (per book) | 1–5 (per book) | 1–5 (per book) | 2–3 |
| 1–2 sent scenes | 43.9–67.7% | 43.4–69.8% | 36.4–72.6% | 36.7–67.9% | 46–57% |
| Max consecutive BORDER | **9** (`dprose_2271`) | 9 (`dprose_1712`) | 13 (`dprose_1060`) | 11 (`dprose_979`) | 5 (`dprose_806`) |
| Batch jobs | 58 / 58 succeeded | 59 / 59 | 55 / 55 | 51 / 51 | — |
| Wave spend | ~$88.90 | ~$88.76 | ~$87.53 | ~$85.75 | — |

**Verdict:** Wave 6 **passed**. BORDER rate ticked up to ~25.7% (still within pilot range). Three books under 14% BORDER; **fifteen** over 30% (densest high-BORDER wave so far). New corpus-wide highest BORDER rate: **38.0%** on `dprose_2051` (prior 36.7% on `dprose_1913`). Wave 6 added **35** parse-fail keys across **20** books; worst book `dprose_2234` (7 fails, 97.1%). New corpus-wide lowest BORDER rate: **10.0%** on `dprose_2006`.

### Per-book summary

Aggregate parse 99.83% (35 failed keys across 20 books; all books ≥95% gate). Sorted by BORDER rate; Notes only when flagged.

| Book | Sents | Parse | BORDER | Med | Run | Notes |
|------|------:|------:|-------:|----:|----:|-------|
| dprose_2006 | 400 | 100% | **10.0%** | 4 | 3 | Low |
| dprose_2135 | 410 | 100% | **12.9%** | 4 | 4 | Low |
| dprose_2188 | 327 | 326/327 (99.7%) | **13.5%** | 4 | 5 | Low; 1 parse fail(s) |
| dprose_2309 | 343 | 100% | 15.5% | 2 | 4 |  |
| dprose_2185 | 211 | 100% | 16.1% | 3 | 3 |  |
| dprose_2004 | 393 | 392/393 (99.7%) | 16.3% | 3 | 6 | 1 parse fail(s) |
| dprose_2169 | 514 | 100% | 16.5% | 2 | 4 |  |
| dprose_2147 | 227 | 100% | 16.7% | 4 | 3 |  |
| dprose_2192 | 451 | 100% | 20.4% | 3 | 5 |  |
| dprose_2019 | 261 | 258/261 (98.9%) | 20.7% | 3 | 3 | 3 parse fail(s) |
| dprose_2136 | 326 | 100% | 20.9% | 2 | 5 |  |
| dprose_2312 | 385 | 384/385 (99.7%) | 21.0% | 3 | 4 | 1 parse fail(s) |
| dprose_2308 | 364 | 100% | 21.2% | 3 | 4 |  |
| dprose_2152 | 561 | 100% | 21.4% | 2 | 5 |  |
| dprose_2191 | 227 | 100% | 21.6% | 3 | 3 |  |
| dprose_2028 | 370 | 100% | 21.6% | 2 | 8 |  |
| dprose_2145 | 364 | 100% | 21.7% | 2 | 4 |  |
| dprose_2123 | 241 | 100% | 22.0% | 2 | 4 |  |
| dprose_2099 | 338 | 100% | 22.2% | 2 | 4 |  |
| dprose_2020 | 236 | 100% | 22.5% | 3 | 4 |  |
| dprose_1987 | 346 | 100% | 22.5% | 2 | 6 |  |
| dprose_1984 | 455 | 100% | 22.6% | 2 | 5 |  |
| dprose_1983 | 538 | 100% | 23.8% | 3 | 5 |  |
| dprose_1989 | 463 | 462/463 (99.8%) | 24.0% | 2 | 6 | 1 parse fail(s) |
| dprose_2236 | 312 | 100% | 24.0% | 3 | 5 |  |
| dprose_2061 | 438 | 433/438 (98.9%) | 24.7% | 2 | 6 | 5 parse fail(s) |
| dprose_2035 | 259 | 100% | 24.7% | 2 | 5 |  |
| dprose_2234 | 242 | 235/242 (97.1%) | 25.2% | 2 | 3 | 7 parse fail(s) |
| dprose_2055 | 374 | 373/374 (99.7%) | 25.7% | 1 | 7 | 1 parse fail(s) |
| dprose_2221 | 397 | 396/397 (99.7%) | 25.7% | 2 | 5 | 1 parse fail(s) |
| dprose_2266 | 428 | 100% | 26.9% | 2 | 4 |  |
| dprose_2012 | 349 | 100% | 26.9% | 2 | 4 |  |
| dprose_1985 | 370 | 369/370 (99.7%) | 27.0% | 2 | 5 | 1 parse fail(s) |
| dprose_2116 | 326 | 325/326 (99.7%) | 27.3% | 2 | 5 | 1 parse fail(s) |
| dprose_2230 | 241 | 100% | 27.4% | 2 | 5 |  |
| dprose_2003 | 295 | 100% | 27.5% | 3 | 4 |  |
| dprose_2050 | 404 | 100% | 28.5% | 2 | 7 |  |
| dprose_2226 | 196 | 100% | 28.6% | 2 | 4 |  |
| dprose_2177 | 355 | 354/355 (99.7%) | 28.7% | 2 | 4 | 1 parse fail(s) |
| dprose_2015 | 277 | 276/277 (99.6%) | 28.9% | 2 | 7 | 1 parse fail(s) |
| dprose_2005 | 333 | 332/333 (99.7%) | 29.4% | 2 | 6 | 1 parse fail(s) |
| dprose_2219 | 226 | 100% | 29.6% | 2 | 4 |  |
| dprose_2271 | 665 | 100% | 29.8% | 2 | 9 | run 9×; **worst run**; Longest in wave |
| dprose_2039 | 333 | 100% | **30.6%** | 2 | 5 | High |
| dprose_2008 | 361 | 359/361 (99.4%) | **30.7%** | 2 | 4 | High; 2 parse fail(s) |
| dprose_2307 | 311 | 100% | **31.2%** | 2 | 4 | High |
| dprose_2054 | 317 | 100% | **31.9%** | 2 | 5 | High |
| dprose_2288 | 260 | 259/260 (99.6%) | **31.9%** | 2 | 4 | High; 1 parse fail(s) |
| dprose_2269 | 422 | 100% | **32.5%** | 2 | 6 | High |
| dprose_2009 | 333 | 100% | **33.0%** | 2 | 7 | High |
| dprose_2100 | 233 | 100% | **33.5%** | 2 | 5 | High |
| dprose_2011 | 367 | 100% | **33.8%** | 2 | 7 | High |
| dprose_2010 | 516 | 515/516 (99.8%) | **35.1%** | 2 | 6 | High; 1 parse fail(s) |
| dprose_2013 | 256 | 255/256 (99.6%) | **35.2%** | 2 | 5 | High; 1 parse fail(s) |
| dprose_2007 | 266 | 100% | **35.3%** | 2 | 5 | High |
| dprose_2014 | 291 | 290/291 (99.7%) | **36.4%** | 2 | 5 | High; 1 parse fail(s) |
| dprose_2112 | 484 | 481/484 (99.4%) | **37.8%** | 1 | 8 | High; 3 parse fail(s) |
| dprose_2051 | 345 | 100% | **38.0%** | 1 | 8 | High; **highest rate** |

### Parse failures (deferred retry)

35 keys across 20 books failed initial parse (prose/thinking instead of JSON — same mode as Waves 1–5). All books still **≥95%** parse; no wave blocker. Worst: `dprose_2234` (7 fails, 97.1%). None retried yet — see [corpus inventory](#parse-failures--corpus-inventory-post-wave-6).

| Book | Parse | Failed keys |
|------|------:|-------------|
| dprose_2234 | 235/242 (97.1%) | :121, :122, :124, :125, :126, :129, :135 |
| dprose_2019 | 258/261 (98.9%) | :225, :186, :64 |
| dprose_2061 | 433/438 (98.9%) | :213, :5, :18, :316, :321 |
| dprose_2112 | 481/484 (99.4%) | :125, :146, :224 |
| dprose_2008 | 359/361 (99.4%) | :54, :56 |
| dprose_2013 | 255/256 (99.6%) | :63 |
| dprose_2288 | 259/260 (99.6%) | :196 |
| dprose_2015 | 276/277 (99.6%) | :202 |
| dprose_2014 | 290/291 (99.7%) | :29 |
| dprose_2116 | 325/326 (99.7%) | :96 |
| dprose_2188 | 326/327 (99.7%) | :104 |
| dprose_2005 | 332/333 (99.7%) | :256 |
| dprose_2177 | 354/355 (99.7%) | :18 |
| dprose_1985 | 369/370 (99.7%) | :187 |
| dprose_2055 | 373/374 (99.7%) | :53 |
| dprose_2312 | 384/385 (99.7%) | :321 |
| dprose_2004 | 392/393 (99.7%) | :253 |
| dprose_2221 | 396/397 (99.7%) | :320 |
| dprose_1989 | 462/463 (99.8%) | :187 |
| dprose_2010 | 515/516 (99.8%) | :328 |

---

### Manual spot-checks — BORDER outliers

Wave median ~26% BORDER. **Low** = under 14% (three books); **high** = over 30% (fifteen books).

#### `dprose_2006` — lowest BORDER rate (10.0%), median scene 4

**Text:** *Der Bettler* — reflective frame narrative («Es schien uns wenig darauf anzukommen»).

**Findings:** Mean scene **9.8** sentences (longest calm stretches in wave); only **44%** short scenes. Max run only 3× at idx 229–231. Twelve gaps ≥10 sentences.

**Assessment:** **Frame narrator / essayistic** prose with long unbroken exposition — same class as Wave 4 `dprose_1075`. New corpus-wide lowest BORDER rate. Plausible; no re-run.

---

#### `dprose_2051` — highest BORDER rate (38.0%), median scene 1

**Text:** Cousin-with-telescope comedy — mistaken pregnancy announcement via birdwatching.

**Findings:** **67%** of scenes span 1–2 sentences; median scene **1**. Opening idx 3–6: title cluster. Max run idx 10–17: **eight consecutive BORDERs** in the cousin's animated retelling (each dialogue beat and reaction BORDERed separately).

**Assessment:** **Stichomythic dialogue / comedy of errors** at sentence granularity — new corpus-wide highest BORDER rate (above Wave 5's `dprose_1913` 36.7%). Strong merge candidate at idx 10–17. Not a pipeline defect.

---

#### `dprose_2271` — wave-worst 9× run at 29.8% BORDER, longest book (665 sents)

**Text:** *Portepeefähnrich Schadius* — colonial military vignette (Senegal, Faidherbe).

**Findings:** Median scene **2**; **65%** 1–2-sent scenes. Max run idx 656–664: **nine consecutive BORDERs** at story close — night watch → window → patrol observations → alarm → each micro-shift BORDERed through the final sentences.

**Assessment:** **Military montage exit** — same pattern as `dprose_1712` and `dprose_1060`. Good post-process merge candidate (collapse 656–664). No re-run needed.

---

#### `dprose_2234` — worst parse rate in wave (97.1%, 7 fails)

**Text:** Mid-text cluster at idx 121–135.

**Findings:** Seven failed keys in a tight band (idx 121, 122, 124–126, 129, 135). BORDER rate normal (25.2%); parse failures only.

**Assessment:** **Retry candidate** via `--retry_failed`; no full-book re-run. Cluster suggests dense dialogue or dialect passage — inspect after retry.

---

### Wave 6 conclusions

| Check | Result |
|-------|--------|
| All batch jobs succeeded | Yes |
| Parse rate ≥ 95% gate | Yes (all 58 books) |
| BORDER rate stable vs pilot | Yes (~25.7% vs 23.8%; uptick, within range) |
| Transient API failures | None |
| Outliers indicate pipeline failure | No — text-structure driven |
| New corpus-wide records | Highest BORDER 38.0% (`dprose_2051`); lowest BORDER 10.0% (`dprose_2006`) |

**Follow-ups before Wave 7:**

1. ~~Plan Wave 7~~ — done (`wave_07_eur100`, 2026-07-03).
2. ~~Raise cumulative `--max_cost_usd` cap~~ — raised to $556.25.
3. ~~Optional corpus-wide `--retry_failed`~~ — done 2026-07-04 (130 keys; see [remediation](#parse-failure-remediation-2026-07-04)).

---

## Wave 7 — `wave_07_eur100` (2026-07-03) — **final wave**

**Manifest:** `data/manifests/waves/wave_07_eur100.json`  
**Log:** `logs/dprose/wave_wave_07_eur100_2026-07-02.log`  
**Run note:** `research_log/runs/2026-07-03__prompting__experiment__dprose-full-wave_07_eur100.md`  
**Books:** 31 (`dprose_2317` … `dprose_2505`)  
**Budget cap:** $556.25 — **not hit** (wave spend ~$49.95; cumulative **$513.81**)

All 31 books processed in a single session (~2.5h). No API incidents. **Full corpus complete: 327/327 books, 120,369/120,369 sentences.**

### Aggregate metrics

| Metric | Wave 7 (31 books) | Wave 6 (58 books) | Pilot (3 books) |
|--------|-------------------|-------------------|-----------------|
| Sentences | 11,846 | 20,333 | 989 |
| Parse OK (at wave end) | 11,823 / 11,846 (99.81%) | 20,298 / 20,333 (99.83%) | 988 / 989 (99.9%) |
| BORDER rate | 23.5% | 25.7% | 23.8% |
| Median scene length | 1–5 (per book) | 1–4 (per book) | 2–3 |
| 1–2 sent scenes | 42.6–64.1% | 43.9–67.7% | 46–57% |
| Max consecutive BORDER | **10** (`dprose_2386`) | 9 (`dprose_2271`) | 5 (`dprose_806`) |
| Batch jobs | 31 / 31 succeeded | 58 / 58 | — |
| Wave spend | ~$49.95 | ~$88.90 | — |

**Verdict:** Wave 7 **passed**. BORDER rate ~23.5% (back toward pilot baseline after Wave 6 uptick). Four books over 30% BORDER; none under 14%. Wave added **23** parse-fail keys across **13** books at completion (worst: `dprose_2443` 557/564, 98.8%). Post-wave remediation reduced Wave 7 failures to **11 keys / 6 books** (see inventory above).

### Per-book summary

Aggregate parse 99.81% at wave end (23 failed keys across 13 books; all books ≥95% gate). Sorted by BORDER rate; Notes only when flagged.

| Book | Sents | Parse | BORDER | Run | Notes |
|------|------:|------:|-------:|----:|-------|
| dprose_2319 | 380 | 100% | 15.5% | 5 |  |
| dprose_2329 | 493 | 492/493 | 17.2% | 4 | 1 parse fail(s) |
| dprose_2401 | 284 | 100% | 18.0% | 4 |  |
| dprose_2325 | 347 | 346/347 | 18.4% | 5 | 1 parse fail(s) |
| dprose_2472 | 375 | 374/375 | 19.5% | 4 | 1 parse fail(s) |
| dprose_2333 | 520 | 100% | 20.4% | 6 |  |
| dprose_2395 | 385 | 100% | 20.5% | 5 |  |
| dprose_2443 | 564 | 557/564 | 21.1% | 5 | 7 parse fail(s) |
| dprose_2317 | 450 | 100% | 21.3% | 7 |  |
| dprose_2322 | 478 | 100% | 21.3% | 7 |  |
| dprose_2413 | 557 | 100% | 21.4% | 6 |  |
| dprose_2505 | 279 | 278/279 | 21.9% | 3 | 1 parse fail(s) |
| dprose_2323 | 389 | 386/389 | 22.9% | 6 | 3 parse fail(s) |
| dprose_2439 | 468 | 100% | 22.9% | 5 |  |
| dprose_2402 | 330 | 100% | 23.3% | 7 |  |
| dprose_2441 | 498 | 100% | 23.5% | 5 |  |
| dprose_2318 | 348 | 100% | 24.4% | 7 |  |
| dprose_2386 | 236 | 100% | 24.6% | **10** | run 10×; **worst run** |
| dprose_2342 | 503 | 100% | 25.0% | 5 |  |
| dprose_2347 | 308 | 100% | 25.3% | 8 | run 8× |
| dprose_2380 | 355 | 100% | 25.9% | 4 |  |
| dprose_2444 | 404 | 403/404 | 26.2% | 5 | 1 parse fail(s) |
| dprose_2324 | 443 | 100% | 26.4% | 6 |  |
| dprose_2417 | 406 | 405/406 | 26.6% | 5 | 1 parse fail(s) |
| dprose_2320 | 381 | 378/381 | 26.8% | 6 | 3 parse fail(s) |
| dprose_2336 | 289 | 100% | 27.3% | 7 |  |
| dprose_2340 | 466 | 465/466 | 27.9% | 9 | 1 parse fail(s); run 9× |
| dprose_2473 | 206 | 205/206 | **30.6%** | 4 | High; 1 parse fail(s) |
| dprose_2348 | 263 | 262/263 | **31.2%** | 6 | High; 1 parse fail(s) |
| dprose_2471 | 195 | 100% | **34.4%** | 4 | High |
| dprose_2476 | 246 | 245/246 | **35.0%** | 5 | High; 1 parse fail(s); **highest rate** |

### Manual spot-checks — BORDER outliers

Wave median ~23.5% BORDER. **High** = over 30% (four books); no books under 14%.

#### `dprose_2476` — highest BORDER rate (35.0%), median scene 2

**Text:** *Es ging ein Engel durch das Haus* — Pfarrhaus vignette (angel visitation, domestic comedy).

**Findings:** **55%** of scenes span 1–2 sentences. Max run idx 75–79: **five consecutive BORDERs** in rapid dialogue exchange. Opening idx 7–8: consecutive BORDERs on title beat + first action.

**Assessment:** **Stichomythic dialogue / comedy** at sentence granularity — same class as Wave 6 `dprose_2051` (38.0%). Plausible over-segmentation; merge candidate at idx 75–79. Not a pipeline defect.

---

#### `dprose_2386` — wave-worst 10× run at 24.6% BORDER

**Text:** Short piece — dense narrative montage in closing section.

**Findings:** Median scene **2**; max run idx 115–124: **ten consecutive BORDERs** — each micro-shift (location, speaker, time) BORDERed separately through the closing sentences.

**Assessment:** **Montage exit** — same pattern as `dprose_2271` (9×) and `dprose_1060` (13× corpus record). Good post-process merge candidate (collapse 115–124). Parse 100%; no re-run needed.

---

#### `dprose_2443` — worst parse rate in wave (98.8%, 7 fails at completion)

**Text:** *Jost* — biblical/epic opening («Der Gebieter des Himmels ließ sein Donnerwort ergehen»).

**Findings:** Seven failed keys clustered mid-text (idx 434–456 band). BORDER rate normal (21.1%); parse failures only. Batch retry recovered 3 keys; sync retry recovered 2 more; **4 keys remain** (all `PROHIBITED_CONTENT` blocks).

**Assessment:** **Retry + patch candidate** — dense dramatic/religious prose triggers safety filters. Neighbor-consensus patch suggests NOBORDER for all 4 remaining keys (high/medium confidence). No full-book re-run.

---

### Wave 7 conclusions

| Check | Result |
|-------|--------|
| All batch jobs succeeded | Yes |
| Full corpus complete | **Yes — 327/327 books** |
| Parse rate ≥ 95% gate | Yes (all 31 books) |
| BORDER rate stable vs pilot | Yes (~23.5% vs 23.8%) |
| Transient API failures | None |
| Outliers indicate pipeline failure | No — text-structure driven |
| New corpus-wide records | Worst run **10×** (`dprose_2386`; prior 9×) |

**Follow-ups after Wave 7:**

1. ~~Corpus-wide `--retry_failed`~~ — done 2026-07-04 (`retry_dprose_corpus_failed.sh`).
2. ~~Sync retry on stubborn keys~~ — done 2026-07-04 (`retry_dprose_sync_failed.sh`; 18/58 recovered).
3. ~~Export neighbor-consensus patches~~ — **applied** 2026-07-04 (40 keys; 37 medium+ then 3 low on second pass → **100% parse OK**).

---

## Parse failure remediation (2026-07-04)

After Wave 7, **130** sentence-keys across **75** books still had `parse_ok=false`. Failures fall into three categories:

| Category | Typical `parse_error` | Count (of 130 initial) | Fix |
|----------|----------------------|------------------------|-----|
| Thinking overflow | prose/thinking instead of JSON | ~70 | Batch retry with higher token budget |
| API null / 503 | empty response, `503 UNAVAILABLE` | ~24 | Sync retry with backoff |
| Safety block | `blocked:PROHIBITED_CONTENT` | ~36 | Sync retry + neighbor patch |

### Tier 1 — Batch `--retry_failed`

**Script:** `scripts/sweeps/retry_dprose_corpus_failed.sh`  
**Runner:** `src/runners/run_dprose_batch_corpus.py --retry_failed --resume --max_output_tokens 4096`  
**Log:** `logs/dprose/retry_failed_2026-07-04.log`  
**Run note:** `research_log/runs/2026-07-04__prompting__retry__dprose-corpus-failed.md`

Re-submits only failed keys via Gemini Batch API. Uses `keys_filter` in `prepare_requests()` to build mini-batches per book; merges results back into existing `predictions.jsonl` via `merge_predictions()`. Raising `max_output_tokens` from 2048 → 4096 gives thinking mode room to emit valid JSON.

**Outcome:** 130 → **58** failed keys (72 recovered, 55%). ~2h 52m runtime.

### Tier 2 — Sync API retry

**Script:** `scripts/sweeps/retry_dprose_sync_failed.sh`  
**Runner:** `src/runners/run_dprose_sync_retry.py`  
**Keys snapshot:** `data/manifests/dprose_sync_retry_keys.json`  
**Log:** `logs/dprose/sync_retry_failed_2026-07-04.log`  
**Run note:** `research_log/runs/2026-07-04__prompting__retry__dprose-sync-failed.md`

Non-batch `generate_content` calls for keys that still fail after Tier 1. Settings: `max_output_tokens=8192`, `thinking_budget=1024` (required for Gemini 2.5 Pro), relaxed safety (`BLOCK_NONE` on all harm categories), 1s sleep between requests, 3× retry on 503.

Handles `blocked:` responses explicitly — records `parse_error=blocked:BlockedReason.PROHIBITED_CONTENT` rather than crashing. First attempt aborted on JSON serialization during merge; re-run completed successfully (~6 min).

**Outcome:** 58 → **40** failed keys (18 recovered). 36/58 were safety blocks; only 2/36 unblocked by sync retry.

### Tier 3 — Neighbor-consensus patch

**Script:** `scripts/evaluation/patch_failed_predictions.py`  
**Suggestions:** `outputs/runs/dprose_batch/dprose-full-corpus/patch_suggestions.{json,csv}`

For keys that cannot be re-inferred via API (persistent safety blocks), assigns labels from local context without additional API cost:

| Method | Confidence | Logic |
|--------|------------|-------|
| `thinking_prose_tail` | high | Recover label leaked in raw thinking prose |
| `neighbor_agreement` | high | Immediate ±1 parsed neighbors agree |
| `wide_neighbor_agreement` | medium | Nearest parsed neighbors within ±5 agree |
| `before/after_border_continuation` | medium | Sentence between parsed labels likely NOBORDER |
| `prev_only` / `next_only` | medium | Single-sided neighbor |
| `default_noborder` | low | No parsed neighbors; conservative fallback |
| `manual_override` | high | CSV/JSON overrides via `--overrides` |

Applied rows get `parse_ok=true`, `manual_fix=<method>`, `manual_fix_confidence=<level>`, and synthetic JSON in `raw_model_response`. Refreshes `book_review.json` after merge.

```bash
# Export suggestions for human review
.venv/bin/python scripts/evaluation/patch_failed_predictions.py \
  --export_json outputs/runs/dprose_batch/dprose-full-corpus/patch_suggestions.json \
  --export_csv  outputs/runs/dprose_batch/dprose-full-corpus/patch_suggestions.csv

# Apply medium+ confidence patches
.venv/bin/python scripts/evaluation/patch_failed_predictions.py \
  --export_json outputs/runs/dprose_batch/dprose-full-corpus/patch_suggestions.json \
  --apply --min_confidence medium
```

**Export (2026-07-04):** 40 keys — 18 high, 19 medium, 3 low confidence.

**Applied (2026-07-04):** Two-pass apply — first `--min_confidence medium` (37 keys), then `--min_confidence low` (3 keys; upgraded to **high** `neighbor_agreement` once adjacent patched rows existed). **0 failed keys remain.** All patched rows tagged `manual_fix` / `manual_fix_confidence` for audit.

### Remediation summary

| Stage | Failed keys | Parse OK (corpus) |
|-------|------------:|-------------------|
| After Wave 7 | 130 | 120,239 / 120,369 (99.89%) |
| After batch retry | 58 | 120,311 / 120,369 (99.95%) |
| After sync retry | 40 | 120,329 / 120,369 (99.97%) |
| After patch (medium+) | 3 | 120,366 / 120,369 (99.998%) |
| After patch (low, 2nd pass) | **0** | **120,369 / 120,369 (100%)** |

The 3 keys skipped on the first apply (`dprose_435:211`, `dprose_1925:144`, `dprose_2234:125`) had no parsed neighbors until adjacent keys were patched; the second pass immediately promoted them to high-confidence `neighbor_agreement`.

---

## Family L spot-rerun vs production B (2026-07-22)

**Purpose:** Transfer-check the Excel-gold finding that Family L (strict MAJOR-discontinuity definition) cuts over-segmentation, on a small contrasting subset of the production corpus.

**Run:** `outputs/runs/dprose_batch/2026-07-22-dprose-familyL-spot-rerun/`  
**Manifest:** `data/manifests/dprose_family_L_spot_rerun.json`  
**Config:** identical to production (`gemini-2.5-pro` batch, `context_sentences=12`, `temperature=0`, `max_output_tokens=2048`, `thinking_budget=-1`, `json_schema_label_reason.json`) — only prompt family = **L**.  
**Cost:** $4.19 / 941 sentences; parse-ok 939/941 (99.8%).  
**Run note:** [`research_log/runs/2026-07-22__prompting__experiment__dprose-familyL-spot-rerun.md`](../../research_log/runs/2026-07-22__prompting__experiment__dprose-familyL-spot-rerun.md)  
**Comparison:** `B_vs_L_comparison.json` (via `scripts/evaluation/compare_dprose_B_vs_L.py`)

### Texts chosen (deliberately non-representative)

| Slug | Spot-check role | Production B |
|------|-----------------|--------------|
| dprose_52 | Wave 1 highest BORDER (32.8%); fairy-tale travel montage | 75 / 229 |
| dprose_119 | Worst consecutive BORDER run (7) at frame/part boundary | 62 / 220 |
| dprose_137 | Wave 1 lowest BORDER (14.5%); dialogue-heavy | 48 / 331 |
| dprose_100 | Pilot book; mid-high rate; header pattern | 49 / 161 |

### B vs L

| slug | B rate | L rate | Δ | B bord | L bord | B maxRun | L maxRun | L∩B F1 | onlyB | onlyL |
|------|--------|--------|---|--------|--------|----------|----------|--------|-------|-------|
| dprose_52 | 32.8% | 23.6% | −9.2pp | 75 | 54 | 6 | 6 | 0.760 | 26 | 5 |
| dprose_119 | 28.2% | 16.8% | −11.4pp | 62 | 37 | 7 | 5 | 0.727 | 26 | 1 |
| dprose_137 | 14.5% | 7.6% | −7.0pp | 48 | 25 | 3 | 2 | 0.630 | 25 | 2 |
| dprose_100 | 30.4% | 23.0% | −7.4pp | 49 | 37 | 3 | 3 | 0.767 | 16 | 4 |

Aggregate on these four: **234 → 153 borders (−35%)**; mean BORDER rate **24.9% → 16.3%**.

### Flagged spots under L

| Spot | Production B | Family L |
|------|--------------|----------|
| dprose_52 montage idx 57–62 | 6× consecutive | 5× (57–61) — barely thinned |
| dprose_119 frame/part idx 155–161 | 7× consecutive | 5× (157–161) — dropped first two |
| dprose_137 gap idx 40–94 | borders at 40 and 94 | only 94 — more conservative |

### Assessment

- **L transfers:** border rate drops on every contrast type, including the already-low dialogue text. L is mostly a **subset of B** (only_L = 1–5 per book).
- **Not a full fix for montage/structural runs:** consecutive clusters shrink by 1–2 sentences, not dissolve — post-process merge rules remain necessary for those patterns.
- **Under-segmentation risk** on low-BORDER texts (dprose_137 → 7.6%) if event-level granularity is desired.
- **No full-corpus L re-run recommended** from this spot sample alone; useful Final-Remarks evidence that a stricter definition reduces over-segmentation on production texts under the same batch config.
