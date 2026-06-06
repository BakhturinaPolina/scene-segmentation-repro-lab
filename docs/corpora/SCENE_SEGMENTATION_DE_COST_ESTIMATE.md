# scene_segmentation_de — Cost Estimate

**Date:** 2026-06-05  
**Model:** Gemini 2.5 Pro with reasoning ON  
**Task:** Scene boundary annotation (BORDER / NOBORDER per sentence)  
**Data folder:** `data/raw/scene_segmentation_de/`

---

## 1) Corpus Summary

Unlike `raw/dprose/` (pre-segmented CSV with a `sentence` column), this folder contains **40 raw book files** named `.txt` but in mixed formats (plain text, EPUB, PDF, RTF). Sentence counts below were estimated by:

1. Extracting text (EPUB unzip + HTML strip, `pdftotext` for PDF, plain read for UTF-8 text)
2. Splitting on German sentence boundaries with `(?<=[.!?])\s+` after whitespace normalization

| Metric | Value |
|--------|-------|
| Total files | 40 |
| Total sentences (estimated) | **197,140** |
| Total characters | 18,530,815 |
| Average chars/sentence | 94.0 |
| Estimated tokens (chars/4) | ~4.6M |

**No gold labels** — output would be model predictions only.

### Format breakdown

| Format | Files | Sentences | Characters |
|--------|------:|----------:|-----------:|
| Plain text | 21 | 77,511 | 8,573,618 |
| EPUB (misnamed `.txt`) | 11 | 12,555 | 2,984,663 |
| PDF (misnamed `.txt`) | 7 | 67,256 | 6,844,820 |
| RTF | 1 | 1,795 | 175,262 |

### Data quality notes

- **2 PDFs could not be parsed** (`Die Verwandlung`, `Hänsel und Gretel`); sentence counts for those files were **fallback-estimated from file size** using the dProse average (120.2 chars/sentence).
- **1 duplicate pair detected:** `Der Geisterfelsen im Baikal-See` and `Im Bann der Vampire` are byte-identical (8,938 sentences each). If deduplicated before running, subtract **8,938 sentences** → **188,202 unique sentences**.
- Several EPUB/PDF extractions may differ slightly from a dedicated sentence tokenizer; treat counts as **±10%** for budgeting.

---

## 2) Approach

Same best-performing setup as the Excel experiments (see `docs/prompting/EXCEL_EXPERIMENTS_COMPARISON_REPORT.md`):

| Setting | Value |
|---------|-------|
| Model | `google/gemini-2.5-pro` |
| Provider | OpenRouter |
| Prompt family | **B** (zero-shot JSON) |
| Reasoning mode | **ON** (high effort) |
| Temperature | 0.0 |
| Response format | JSON schema |
| max_tokens | 256 |

**Prerequisite:** Raw files must be converted to one sentence per row (or equivalent prompting input) before inference — same per-sentence API call pattern as dProse/Excel runs.

---

## 3) Token Estimates per Request

Based on `outputs/runs/prompting/2026-05-31-excel-gemini-reasoning-on/.../summary.json`:

| Component | Tokens (estimated) |
|-----------|-------------------|
| Prompt template | ~90 |
| Left + right context | ~500 |
| Target sentence | ~30 |
| **Total input** | **~620–700** |

| Output component | Tokens (estimated) |
|------------------|-------------------|
| Visible JSON + reason | ~85 |
| Thinking tokens (reasoning ON) | ~500–800 |
| **Total output** | **~600–800** |

Reference: `avg_output_chars: 338.84`, `avg_latency_seconds: 3.43`.

---

## 4) Pricing (Gemini 2.5 Pro via OpenRouter)

| Tier | Input (per 1M tokens) | Output (per 1M tokens) |
|------|----------------------|------------------------|
| Standard (≤200K context) | $1.25 | $10.00 |
| Batch/Flex (50% off) | $0.625 | $5.00 |

Output pricing includes thinking tokens when reasoning is enabled.

---

## 5) Cost Calculation (197,140 sentences)

### Conservative (700 input + 800 output tokens/request)

| Component | Calculation | Standard | Batch |
|-----------|-------------|----------|-------|
| Input | 197,140 × 700 = 138.0M | $172.50 | $86.25 |
| Output | 197,140 × 800 = 157.7M | $1,577.12 | $788.56 |
| **Total** | | **$1,749.62** | **$874.81** |

### Optimistic (600 input + 500 output tokens/request)

| Tier | Input | Output | **Total** |
|------|-------|--------|-----------|
| Standard | $147.86 | $985.70 | **$1,133.55** |
| Batch | $73.93 | $492.85 | **$566.78** |

### If duplicate file is skipped (188,202 sentences)

| Scenario | Standard | Batch |
|----------|----------|-------|
| Conservative | **$1,670** | **$835** |
| Optimistic | **$1,082** | **$541** |

---

## 6) Summary: Expected Cost Range

| Scenario | Estimated cost |
|----------|----------------|
| **Conservative (standard)** | **$1,650 – $1,750** |
| **Conservative (batch)** | **$825 – $875** |
| **Optimistic (standard)** | **$1,080 – $1,135** |
| **Optimistic (batch)** | **$540 – $570** |

**Recommended budget:** **$900 – $1,750** (batch vs standard pricing).

---

## 7) Runtime Estimate

Based on `avg_latency_seconds: 3.43`:

| Metric | 197,140 sentences |
|--------|-------------------|
| Latency per request | ~3.5 s |
| Sequential | ~192 hours |
| 10 concurrent | ~19 hours |
| 50 concurrent | ~3.8 hours |

---

## 8) Per-file sentence counts (estimated)

| File | Format | Sentences | Avg chars | Notes |
|------|--------|----------:|----------:|-------|
| Hänsel und Gretel - Brüder Grimm.txt | pdf | 33,624 | 120.2 | size fallback |
| Die Verwandlung - Franz Kafka.txt | pdf | 15,811 | 120.2 | size fallback |
| Harry Potter VI - J. K. Rowling.txt | text | 12,308 | 90.5 | |
| Wenn Tote plötzlich wieder sprechen - Chrissie Black.txt | text | 9,537 | 60.2 | |
| Ein sündiges Erbe - Jack Slade.txt | text | 9,225 | 78.5 | |
| Der Geisterfelsen im Baikal-See - Walther Kabel, W. Belka.txt | text | 8,938 | 80.8 | duplicate |
| Im Bann der Vampire - Emily Blake.txt | text | 8,938 | 80.8 | duplicate of above |
| Im Dschungel der Lust - Amy J. Fetzer.txt | text | 8,750 | 69.0 | |
| Griseldis - Hedwig Courths-Mahler.txt | epub | 6,450 | 55.7 | |
| Als der Meister starb - Wolfgang Hohlbein.txt | epub | 5,975 | 86.8 | |
| Der Schimmelreiter - Theodor Storm.txt | pdf | 6,500 | 40.1 | |
| Ein Weihnachtslied für Dr. Bergen - Marina Anders.txt | text | 1,808 | 249.2 | |
| Immer wenn der Sturm kommt - O. S. Winterfield.txt | text | 1,814 | 277.6 | |
| Die Abrechnung - Frank Callahan.txt | text | 2,792 | 155.5 | |
| Lass Blumen sprechen - Verena Kufsteiner.txt | text | 2,684 | 137.2 | |
| Prophet der Apokalypse - Manfred Weinland.txt | pdf | 2,988 | 55.8 | |
| Die Begegnung - Alfred Bekker.txt | pdf | 3,223 | 45.8 | |
| Die Judenbuche - Annette von Droste-Hülshoff.txt | pdf | 2,979 | 57.6 | |
| Der Turm der 1000 Schrecken - Jason Dark.txt | rtf | 1,795 | 97.6 | |
| Der Sohn des Kometen - Hugh Walker.txt | pdf | 2,131 | 73.3 | |
| Tausend Pferde - G. F. Unger.txt | text | 2,143 | 185.7 | |
| Nur noch eine heiße Nacht mit dir! - Katherine Garbera.txt | text | 1,694 | 144.5 | |
| Bezaubernde neue Mutti - Regine König.txt | text | 1,242 | 360.1 | |
| In den Dreck getreten - H. C. Hollister.txt | text | 1,290 | 66.3 | |
| Agenten und Spione - Günter Dönges.txt | text | 1,118 | 167.3 | |
| Wechselhaft wie der April - Andreas Kufsteiner.txt | text | 1,354 | 304.6 | |
| Effi Briest - Theodor Fontane.txt | epub | 49 | 13,798.6 | coarse EPUB split |
| Aus guter Familie - Gabriele Reuter.txt | epub | 34 | 13,428.1 | coarse EPUB split |
| *(remaining 12 files)* | mixed | *≤1,300 each* | | |

*Effi Briest* and *Aus guter Familie* show very high avg chars/sentence — likely under-segmented in EPUB extraction; true sentence counts may be higher (and cost slightly above table for those two).

---

## 9) Cost by Reproducibility Gap Step

Based on [`SCENE_SEGMENTATION_DE_BOOK_LIST.md`](SCENE_SEGMENTATION_DE_BOOK_LIST.md) and [`REPRODUCIBILITY_GAP_REVIEW.md`](../reproducibility/REPRODUCIBILITY_GAP_REVIEW.md), the prompting-only reproduction can be staged as follows.

### Sentence estimates by paper split

| Split | Texts | Estimated sentences | Source |
|-------|------:|--------------------:|--------|
| **STSS-Test-2** | 2 | 892 | XMI gold annotation (verified) |
| **STSS-Test-1** | 4 | ~8,500 | Raw file estimates, adjusted |
| **OOD-Test** | 3 | ~13,000 | Harry Potter 12,308 + Hänsel und Gretel ~500 |
| **Test-Full** | 9 | **~22,400** | Sum of above |
| **Train-Full** | 32 | **~165,800** | 188,202 total − Test-Full |
| **All 41 texts** | 41 | **~188,200** | Deduplicated total |

**Notes:**
- STSS-Test-2 count comes from verified XMI files; raw EPUB extraction yielded only 83 coarse segments.
- Hänsel und Gretel raw estimate (33,624 via PDF fallback) is implausible for a fairy tale; revised to ~500.
- Train-Full includes high-literature additions (Krambambuli, Verwandlung, etc.) plus dime novels.

### Gap-closing steps and incremental cost

Using **conservative (700 input + 800 output tokens/request)** pricing:

| Step | Target scope | Sentences added | Cumulative sentences | Standard cost | Batch cost |
|------|--------------|----------------:|---------------------:|--------------:|----------:|
| **0 (done)** | STSS-Test-2 (XMI) | 892 | 892 | ~$8 | ~$4 |
| **1** | + STSS-Test-1 | ~8,500 | ~9,400 | ~$84 | ~$42 |
| **2** | + OOD-Test → **Test-Full** | ~13,000 | ~22,400 | ~$200 | ~$100 |
| **3** | + Train-Full → **All 41 texts** | ~165,800 | ~188,200 | ~$1,670 | ~$835 |

*Per-sentence cost: ~$0.00887 standard, ~$0.00444 batch.*

### Cost formula (conservative)

For any subset with **N** sentences:

```
Standard: N × 700 × $1.25/1M + N × 800 × $10.00/1M
        = N × ($0.000875 + $0.008) = N × $0.008875

Batch:    N × $0.004438
```

### Recommended phased budget (prompting only)

| Phase | Scope | Est. cost (batch) | Milestone |
|-------|-------|------------------:|-----------|
| **Pilot** | 1–2 Train-Full texts (~3k sentences) | ~$15 | Verify preprocessing + API flow |
| **Phase 1** | Test-Full (9 texts) | ~$100 | Paper-comparable test evaluation |
| **Phase 2** | Full corpus (41 texts) | ~$835 | Complete prompting coverage |

**Recommended total budget:** **$950** (batch) to **$1,900** (standard) including buffer.

---

## 10) Comparison with other corpora

| Corpus | Files | Sentences | Est. cost (conservative, standard) | Gold labels |
|--------|------:|----------:|-----------------------------------:|:-----------:|
| Excel (Kleist + Gaensemagd) | 2 | 316 | ~$3 | ✓ |
| scene_segmentation_de | 40 | 197,140 | **~$1,750** | ✗ |
| dprose | 327 | 120,369 | ~$1,070 | ✗ |

scene_segmentation_de is **~1.6×** the sentence volume of dProse and **~624×** the Excel pilot set.

---

## 11) Recommendations

1. **Preprocess first:** Build sentence-level inputs (like `prepare_excel_prompting_inputs.py` for Excel) with a proper German sentence splitter; do not rely on raw line breaks.
2. **Deduplicate** `Der Geisterfelsen` / `Im Bann der Vampire` before a full run.
3. **Fix or replace** the two broken PDFs before production.
4. **Pilot run:** 1–2 medium texts (~3,000 sentences) → ~$15–30 batch/standard pricing.
5. **Use batch pricing** if turnaround time allows (~50% savings).
6. **Optional post-processing:** `min_scene_len_5` gap rule (see Excel report) if reviewers tolerate near-match boundaries.
7. **Stage by gap steps:** Follow Section 9 phased approach to incrementally close reproducibility gaps.

**Suggested budget:** pilot ~$15–30 + Test-Full ~$100–200 + full run **$835–$1,670** → **$950–$1,900 total**.
