# Full Dataset Prompting Plan — Gemini 2.5 Pro with Reasoning ON

**Date:** 2026-06-05  
**Scope:** Complete prompting-only reproduction for all 41 texts in the NAACL 2025 paper corpus  
**Model:** `google/gemini-2.5-pro` via OpenRouter, reasoning ON (high effort)  
**Prompt family:** B (zero-shot JSON)  
**Reference docs:**
- [`SCENE_SEGMENTATION_DE_BOOK_LIST.md`](../corpora/SCENE_SEGMENTATION_DE_BOOK_LIST.md) — full title/author/split catalog
- [`SCENE_SEGMENTATION_DE_COST_ESTIMATE.md`](../corpora/SCENE_SEGMENTATION_DE_COST_ESTIMATE.md) — cost calculations
- [`REPRODUCIBILITY_GAP_REVIEW.md`](../reproducibility/REPRODUCIBILITY_GAP_REVIEW.md) — gap analysis

---

## 1) Objective

Run scene boundary classification on **every sentence** in all 41 texts from the paper's corpus using the best-performing configuration from Excel experiments:

| Setting | Value |
|---------|-------|
| Model | `google/gemini-2.5-pro` |
| Provider | OpenRouter |
| Prompt family | **B** (zero-shot JSON) |
| Reasoning mode | **ON** (high effort) |
| Temperature | 0.0 (deterministic) |
| Response format | JSON schema |
| max_tokens | 256 |

**Why Gemini 2.5 Pro with reasoning ON?**
- Best F1 performance in Excel experiments (see [`EXCEL_EXPERIMENTS_COMPARISON_REPORT.md`](../prompting/EXCEL_EXPERIMENTS_COMPARISON_REPORT.md))
- Reasoning mode improves boundary placement accuracy
- Stable JSON output via schema enforcement
- Competitive pricing on OpenRouter

---

## 2) Corpus Overview

From [`SCENE_SEGMENTATION_DE_BOOK_LIST.md`](../corpora/SCENE_SEGMENTATION_DE_BOOK_LIST.md):

| Paper subset | Texts | Est. sentences | Gold available |
|--------------|------:|---------------:|:--------------:|
| STSS-Test-2 | 2 | 892 | ✓ XMI |
| STSS-Test-1 | 4 | ~8,500 | Standoff only |
| OOD-Test | 3 | ~13,000 | Standoff only |
| **Test-Full** | **9** | **~22,400** | Partial |
| Train-Full | 32 | ~165,800 | Standoff only |
| **All 41 texts** | **41** | **~188,200** | Partial |

**Data locations:**
- Raw texts: `data/raw/scene_segmentation_de/` (40 files; Harry Potter chapters merged)
- Standoff annotations: `upstream/scene-segmentation/data/standoff/`
- Full XMI: `upstream/scene-segmentation/data/full/stss_test_2/` (STSS-Test-2 only)

---

## 3) Prerequisites

### 3.1 Data preparation

| Task | Script/tool | Output |
|------|-------------|--------|
| **Sentence segmentation** | New `prepare_full_corpus_inputs.py` | `data/processed/scene_segmentation_de/*.jsonl` |
| **MD5 verification** | Extend `verify_data_manifest.py` | Verify raw text matches standoff hashes |
| **Harry Potter split** | Manual or script | Separate Der Slug Club / Schleim chapters |
| **Deduplication** | Skip `Im Bann der Vampire` (duplicate of `Der Geisterfelsen`) | −8,938 sentences |
| **PDF/EPUB fixes** | Re-extract `Die Verwandlung`, `Hänsel und Gretel` | Proper sentence counts |

**Sentence segmentation requirements:**
- Use proper German tokenizer (e.g., `spacy de_core_news_sm` or `stanza`)
- Output format: JSONL with `sentence_index`, `sentence_text`, `left_context`, `right_context`
- Context window: ~500 tokens total (matching paper's 512 × 0.8 budget)

### 3.2 API setup

| Requirement | Details |
|-------------|---------|
| OpenRouter API key | Set in environment: `OPENROUTER_API_KEY` |
| Rate limits | Check current limits for `google/gemini-2.5-pro` |
| Batch API access | Optional; enables 50% cost reduction |
| Retry logic | Exponential backoff for 429/500 errors |

### 3.3 Infrastructure

| Requirement | Recommended |
|-------------|-------------|
| Concurrency | 10–50 parallel requests |
| Checkpointing | Resume from last completed sentence |
| Output storage | `outputs/runs/prompting/full_corpus_gemini/{text_name}/results.jsonl` |
| Logging | Per-text `summary.json` with cost/latency metrics |

---

## 4) Execution Phases

### Phase 0: Pilot (1–2 texts, ~3,000 sentences)

**Goal:** Validate preprocessing, API flow, and cost estimates before committing budget.

| Item | Details |
|------|---------|
| **Texts** | Pick 1–2 from Train-Full (e.g., `Die Abrechnung`, `Lass Blumen sprechen`) |
| **Sentences** | ~2,500–3,000 |
| **Est. cost** | ~$15 (batch) / ~$30 (standard) |
| **Est. runtime** | ~3 hours @ 10 concurrent |
| **Success criteria** | Valid JSON output, reasonable latency, cost matches estimate |

**Checklist:**
- [ ] Sentence segmentation produces expected count (compare to paper Table 5 if available)
- [ ] API calls succeed without persistent errors
- [ ] Output JSON parses correctly
- [ ] Per-request cost matches estimate (~$0.0044–$0.0089)
- [ ] Checkpoint/resume works

### Phase 1: Test-Full (9 texts, ~22,400 sentences)

**Goal:** Generate predictions for all test splits to enable paper-comparable evaluation.

| Step | Subset | Texts | Sentences | Cumulative cost (batch) |
|------|--------|------:|----------:|------------------------:|
| 1a | STSS-Test-2 | 2 | 892 | ~$4 |
| 1b | STSS-Test-1 | 4 | ~8,500 | ~$42 |
| 1c | OOD-Test | 3 | ~13,000 | ~$100 |

**Total Phase 1:** ~$100 batch / ~$200 standard

**Outputs:**
- `outputs/runs/prompting/full_corpus_gemini/test_full/` with per-text results
- Aggregated `metrics_test_full.json` with F1 @ tolerance 0/1/3

**Evaluation:**
- Compare to paper Table 2 (Test-Full zero-shot baseline: GPT-4o = 0.45 F1 @ t=3)
- Compare to paper Table 1 (STSS-Test-2 supervised GBERT-Large = 0.66 F1 @ t=3)

### Phase 2: Train-Full (32 texts, ~165,800 sentences)

**Goal:** Complete corpus coverage for potential leave-one-out analysis or training data generation.

| Item | Details |
|------|---------|
| **Texts** | All 32 Train-Full texts |
| **Sentences** | ~165,800 |
| **Est. cost** | ~$735 batch / ~$1,470 standard |
| **Est. runtime** | ~16 hours @ 50 concurrent |

**Total Phase 2 (cumulative):** ~$835 batch / ~$1,670 standard

**Outputs:**
- `outputs/runs/prompting/full_corpus_gemini/train_full/` with per-text results
- Per-text `predictions.csv` for downstream use

---

## 5) Output Schema

### Per-sentence API response

```json
{
  "label": "BORDER" | "NOBORDER",
  "confidence": 0.0–1.0,
  "reason": "Brief explanation..."
}
```

### Per-text results file (`results.jsonl`)

```json
{
  "sentence_index": 42,
  "sentence_text": "Am nächsten Morgen...",
  "prediction": "BORDER",
  "confidence": 0.92,
  "reason": "Time jump indicated by 'Am nächsten Morgen'",
  "input_tokens": 687,
  "output_tokens": 623,
  "latency_ms": 3420,
  "request_id": "req_abc123"
}
```

### Per-text summary (`summary.json`)

```json
{
  "text_name": "Die Abrechnung",
  "total_sentences": 2792,
  "predictions": {"BORDER": 45, "NOBORDER": 2747},
  "total_input_tokens": 1917624,
  "total_output_tokens": 1739016,
  "total_cost_usd": 24.76,
  "avg_latency_ms": 3430,
  "start_time": "2026-06-06T10:00:00Z",
  "end_time": "2026-06-06T12:45:00Z"
}
```

---

## 6) Evaluation Plan

### Metrics

| Metric | Definition |
|--------|------------|
| **F1 @ t=0** | Exact sentence match (strict) |
| **F1 @ t=1** | ±1 sentence tolerance |
| **F1 @ t=3** | ±3 sentence tolerance (paper headline) |
| **Precision** | Correct borders / predicted borders |
| **Recall** | Correct borders / gold borders |

### Gold comparison

| Subset | Gold source | Comparison method |
|--------|-------------|-------------------|
| STSS-Test-2 | XMI files | Direct sentence alignment |
| STSS-Test-1 | Standoff JSON | Match via MD5 + char offsets |
| OOD-Test | Standoff JSON | Match via MD5 + char offsets |
| Train-Full | Standoff JSON | For analysis only (no held-out eval) |

### Post-processing options

From [`EXCEL_EXPERIMENTS_COMPARISON_REPORT.md`](../prompting/EXCEL_EXPERIMENTS_COMPARISON_REPORT.md):

| Rule | Effect |
|------|--------|
| `min_scene_len_3` | Suppress borders within 3 sentences of prior border |
| `min_scene_len_5` | Suppress borders within 5 sentences (best tol5 F1) |

Apply post-processing as sensitivity analysis, not primary result.

---

## 7) Cost Summary

| Phase | Scope | Sentences | Batch cost | Standard cost |
|-------|-------|----------:|----------:|-------------:|
| **Pilot** | 1–2 texts | ~3,000 | ~$15 | ~$30 |
| **Phase 1** | Test-Full | ~22,400 | ~$100 | ~$200 |
| **Phase 2** | + Train-Full | ~165,800 | ~$735 | ~$1,470 |
| **Total** | All 41 texts | ~188,200 | **~$850** | **~$1,700** |

**Recommended budget with 15% buffer:**
- Batch pricing: **$980**
- Standard pricing: **$1,960**

---

## 8) Timeline (Estimated)

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Preprocessing | 1–2 days | — |
| Pilot | 0.5 days | — |
| Phase 1 (Test-Full) | 1 day | 2.5–3.5 days |
| Phase 2 (Train-Full) | 1–2 days | 3.5–5.5 days |
| Evaluation & reporting | 1 day | 4.5–6.5 days |

**Total:** ~1 week from start to final report.

---

## 9) Risk Mitigation

| Risk | Mitigation |
|------|------------|
| API rate limits | Start with 10 concurrent, scale to 50 if stable |
| Model unavailability | Pin model version; have Nemotron-Super-120B as fallback |
| Sentence count variance | Budget +15%; raw estimates may be ±10% |
| Checkpoint corruption | Write results incrementally; use atomic writes |
| Cost overrun | Monitor after pilot; stop if >20% above estimate |

---

## 10) Deliverables

| Deliverable | Location |
|-------------|----------|
| Preprocessed inputs | `data/processed/scene_segmentation_de/` |
| Predictions (per-text) | `outputs/runs/prompting/full_corpus_gemini/{subset}/{text}/` |
| Aggregated metrics | `outputs/runs/prompting/full_corpus_gemini/metrics_*.json` |
| Run notes | `research_log/runs/2026-06-XX__prompting__experiment__full-corpus-gemini-reasoning-on.md` |
| Final report | `docs/prompting/FULL_CORPUS_PROMPTING_REPORT.md` |

---

## 11) Success Criteria

| Criterion | Target |
|-----------|--------|
| Test-Full F1 @ t=3 | ≥ 0.50 (beat paper GPT-4o baseline of 0.45) |
| STSS-Test-2 F1 @ t=3 | ≥ 0.80 (match/beat Nemotron result of 0.83) |
| Coverage | 100% of 41 texts processed |
| Cost | ≤ $1,000 (batch) or ≤ $2,000 (standard) |
| Reproducibility | All runs logged per `rule.md` |

---

## 12) Next Steps

1. [ ] Build `prepare_full_corpus_inputs.py` with proper German sentence segmentation
2. [ ] Create `data/manifest_scene_segmentation_de.json` with file checksums and split labels
3. [ ] Fix Harry Potter chapter split and PDF extraction issues
4. [ ] Run pilot on 2 Train-Full texts
5. [ ] If pilot succeeds, proceed to Phase 1 (Test-Full)
6. [ ] Evaluate Test-Full results against paper baselines
7. [ ] If Phase 1 metrics are promising, proceed to Phase 2 (full corpus)
8. [ ] Generate final report with paper-comparable metrics

---

## References

- NAACL 2025 Paper: [Assessing the State of the Art in Scene Segmentation](https://aclanthology.org/2025.naacl-long.500/)
- Upstream repo: [LSX-UniWue/scene-segmentation](https://github.com/LSX-UniWue/scene-segmentation)
- OpenRouter Gemini pricing: [openrouter.ai/google/gemini-2.5-pro](https://openrouter.ai/google/gemini-2.5-pro)
