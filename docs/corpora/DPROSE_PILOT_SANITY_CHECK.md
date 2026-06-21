# dProse Pilot Predictions — Sanity Check

**Updated:** 2026-06-21  
**Run:** `outputs/runs/dprose_batch/2026-06-20-dprose-batch-pilot-2048/`  
**Artifact:** `predictions.jsonl` (989 sentences, 3 pilot files)  
**Model:** Gemini 2.5 Pro, Prompt Family B, `max_output_tokens=2048`

No gold labels exist for dProse. This document summarizes manual sanity-check findings: text content, border quality, and recommended follow-ups before scaling to the full corpus (~120k sentences).

Related: [DPROSE_COST_ESTIMATE.md](./DPROSE_COST_ESTIMATE.md)

---

## Run summary

| Metric | Value |
|--------|-------|
| Requests | 989 |
| Parse OK | 988 (99.9%) |
| Parse failures | 1 (`dprose_100:22`) |
| BORDER | 235 (23.8%) |
| NOBORDER | 753 (76.2%) |
| Avg input tokens | ~934 |
| Avg output tokens | ~73 visible + ~701 thinking |
| Estimated cost | $4.40 |

**Task definition (Prompt B):** decide whether the target sentence **starts** a new event/scene segment — i.e. a significant change in time, location, participating characters, or ongoing action.

---

## Aggregate border statistics

| Source file | Sentences | BORDER | Rate |
|-------------|-----------|--------|------|
| `dprose_100.csv` | 161 | 48 | 29.8% |
| `dprose_2158.csv` | 76 | 20 | 26.3% |
| `dprose_806.csv` | 752 | 167 | 22.2% |

### Scene length (after treating each BORDER as a segment start)

| Source file | Median length | Mean length | Min | Max | Scenes of 1–2 sentences |
|-------------|---------------|-------------|-----|-----|-------------------------|
| `dprose_100.csv` | 3 | 3.4 | 1 | 12 | 46% |
| `dprose_2158.csv` | 2 | 3.8 | 1 | 15 | 55% |
| `dprose_806.csv` | 2 | 4.5 | 1 | 36 | 57% |

### Over-segmentation signals

| Signal | dprose_100 | dprose_2158 | dprose_806 |
|--------|------------|-------------|------------|
| Max consecutive BORDER run | 3 | 2 | 5 |
| Consecutive BORDER pairs (N and N+1 both BORDER) | 14 | 6 | 63 |
| Gap between borders ≥ 10 sentences | 1 | 2 | 22 |

**Interpretation:** reasoning in `raw_model_response` is usually coherent, but roughly **half of inferred “scenes” span only 1–2 sentences**. The model tracks paragraph-level focus shifts more than coarse human scene boundaries.

---

## Text content summaries

### `dprose_100.csv` — *Sturms Heimkehr* (161 sentences)

Allegorical prose: a personified **Sturm** (storm-wind) as foster-son of a crumbling mountain **Städtchen**. Structured with Roman sections **I–VII**.

| Section | Content |
|---------|---------|
| **I** | Valley town; storm-child grows up, leaves; town ages without him |
| **II–III** | Summer-evening return; nostalgic wanderings (market, tavern, gardens, poor outskirts) |
| **IV–VI** | Dark evening; “fliegender Schreck” (terror/disease metaphor) spreads panic; storm battles lightning/thundercloud |
| **VII + coda** | Storm calms the town; shift to first-person meta (“Junge Sturmgedanken”) on how storm-thoughts arise in writers |

Tone is dense metaphor — many apparent “scene” shifts are atmospheric rather than plot beats.

---

### `dprose_2158.csv` — *Die Bas* (76 sentences)

Compact Schwarzwald drama in deep winter. Single farm, few characters, strong through-line.

| Beat | Content |
|------|---------|
| Opening | Snowy landscape; silent isolated farm; raven on chimney |
| Interior | **Die Bas** (old woman) counts silver; **Finle** (young girl) sings; quarrel over money and temperament |
| Jakob arrives | Locked door; window dialogue; he enters; confrontation over keys and hoarded wealth |
| Violence | Physical struggle; Bas collapses; Jakob tends Finle; Bas prepares to leave |
| Nightmare | Money bag leaks outside; crowd accuses Jakob as **Dieb**; he wakes from trance |
| Ending | Reconciliation with Finle; men carry Bas’s corpse across the threshold |

---

### `dprose_806.csv` — *Die Erscheinung* (752 sentences)

Long novella about **Dr. Arnold Riedhammer**, German engineer/doctor returning from the South Seas.

| Beat | Approx. region | Content |
|------|---------------|---------|
| Port Said | idx 0–30 | Ship `Bussard` coaling; Riedhammer writes; flashbacks to Nauru/Marshall Islands |
| Ship voyage | idx 30–140 | Heat, dust, mood; games; he notices a white woman |
| Meeting | idx 140–200 | Dialogue with **Johne Stevens** (Amsterdam/Batavia); attraction; wedding ring |
| Storm / Naples | idx 200–284 | Disembarkation; travel plans; romantic idyll in Italy |
| Italy → Paris | idx 284–340 | Naples arrival; Granarolo; train toward Paris during **Weltausstellung** |
| Paris life | idx 340–440 | Apartment, jealousy, social exposure, work vs. passion |
| Crisis | idx 440–720 | Johne vanishes; search; consulates; police; violent confrontation; quarantine |
| Aftermath | idx 720–748 | Flight via Havre, London, islands; Thuringia; reclusive life; visionary ending |
| Epilogue | idx 749–751 | Police record: Johne died of **Pest**; room disinfected; Riedhammer removed from Paris |

Most narratively complex of the three: many time/place jumps, flashbacks, POV shifts.

---

## Border quality by text

### `dprose_100.csv` — mixed quality

**Good calls**

- Roman section headers **II, III, IV, V, VI, VII** marked BORDER — aligns with author structure
- Major phase shifts: storm’s departure (idx 14), return evening (15), winter vs. summer memory (44), storm–terror battle (68+), first-person meta shift (145)

**Questionable / over-segmentation**

| idx | Issue |
|-----|-------|
| 74–76 | Triple BORDER: music stops → looks around → terror appears — one continuous beat |
| 131–133 | Triple BORDER on section VII summary + general reflection |
| 48, 19, 33 | 1-sentence “scenes” on mood pivots (“Aber nachts!”, etc.) |
| 2–3 | Back-to-back BORDER within town exposition |

**Verdict:** literarily attentive but **too granular** for coarse scene labeling. Acceptable for fine-grained event segmentation.

---

### `dprose_2158.csv` — mostly reasonable

**Good calls**

- Exterior/interior shift (idx 3), Jakob at window (23), dream/accusation (71–72), funeral procession (75)
- Long dialogue blocks mostly NOBORDER (idx 10–19)

**Questionable**

| idx | Issue |
|-----|-------|
| 20, 21 | Double BORDER for one door-knock interruption |
| 24 | BORDER on “»Bas,« sprach er…” — same entrance scene as 23 |
| 8 | BORDER on Bas muttering about her eye — micro-shift in ongoing tableau |

**Verdict:** best fit of the three for intuitive scene sense; still ~55% micro-scenes.

---

### `dprose_806.csv` — coherent reasoning, heavy over-segmentation

**Good calls**

- Flashback entries (idx 8, 10, 13)
- Clear loc/time jumps: Neapel (284), train toward Paris (334), room 117 search (444)
- Clean epilogue break: idx 748 NOBORDER (vision) → 749 BORDER (police report)
- Long dialogue stretches correctly NOBORDER (e.g. idx 155–167)

**Systematic problems**

| Pattern | Example | Count |
|---------|---------|-------|
| Consecutive BORDER pairs | idx 13–15 (backstory split into 3 scenes) | 63 pairs |
| Single beat split multiple ways | idx 152–154 (stands → sees woman → walks over) | — |
| Comic interlude over-split | idx 138–141 (parrot chase) | 4 consecutive BORDER |
| Travel montage | idx 729–736 (Havre → London → islands → Germany) | ~1 border per sentence |

**Verdict:** strong narrative understanding in `reason` fields, but **167 scenes in 752 sentences** (~4.5 sent/scene mean). Useful as fine event boundaries; poor as chapter/scene boundaries without post-processing.

---

## Parse failure

| Key | Sentence | Likely label | Cause |
|-----|----------|--------------|-------|
| `dprose_100:22` | “Danach auf der Suche über Land…” | BORDER (temporal shift “Danach”) | JSON truncated mid-`reason`; `thought_tokens` exceeded visible output budget |

Re-run this key with higher `max_output_tokens` or capped `thinking_budget` before full-corpus aggregation.

---

## Sanity-check conclusions

| Check | Result |
|-------|--------|
| Labels parse and look internally consistent? | **Yes** (99.9%) |
| Reasons match text? | **Mostly yes** |
| Major plot transitions captured? | **Yes** |
| Border rate plausible for coarse scenes? | **No** — likely 2–3× denser than human scene labels |
| Cross-text consistency? | **806** less conservative despite longer continuous passages |
| Structural markers (roman numerals)? | **100:** good alignment |

---

## Recommended spot-check sentences

If reviewing ~20 predictions manually, prioritize:

| File | Sentence indices | Why |
|------|------------------|-----|
| `dprose_806.csv` | 138–141, 152–154, 729–736 | Consecutive BORDER clusters; travel montage |
| `dprose_2158.csv` | 20–24 | Redundant borders around Jakob’s entrance |
| `dprose_100.csv` | 74–76, 131–133 | Triple BORDER runs |
| `dprose_100.csv` | 22 | Parse failure |

---

## Recommended follow-ups

**Post-process merge:** collapse adjacent BORDER when gap ≤ 1–2 sentences and location/characters unchanged (could remove ~30–40% of borders in `dprose_806`).

---

## References

| Resource | Path |
|----------|------|
| Predictions | `outputs/runs/dprose_batch/2026-06-20-dprose-batch-pilot-2048/predictions.jsonl` |
| Summary | `outputs/runs/dprose_batch/2026-06-20-dprose-batch-pilot-2048/pilot_summary.json` |
| Manifest | `data/manifests/dprose_pilot.json` |
| Prompt B | `src/prompts/B_zero_shot_json.txt` |
| Runner | `src/runners/run_dprose_batch_pilot.py` |
| Run note | `research_log/runs/2026-06-20__prompting__experiment__dprose-batch-pilot-2048.md` |
