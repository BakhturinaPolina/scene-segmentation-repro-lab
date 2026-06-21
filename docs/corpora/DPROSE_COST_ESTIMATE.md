# dProse Corpus Scene Segmentation — Cost Estimate

**Updated:** 2026-06-21 (post 2048-token pilot rerun)  
**Model:** Gemini 2.5 Pro, reasoning ON, Prompt Family B  
**Provider:** Direct [Gemini Batch API](https://ai.google.dev/gemini-api/docs/batch-api) (50% off standard rates)

No gold labels — output is model predictions only (BORDER / NOBORDER per sentence).

---

## Corpus

| Metric | Value |
|--------|-------|
| CSV files | 327 |
| Sentences | 120,369 |
| Chars / sentence (avg) | 120.2 |

---

## Configuration (pilot-validated)

| Setting | Value |
|---------|-------|
| Model | `gemini-2.5-pro` |
| Prompt | Family **B** + `json_schema_label_reason.json` |
| Provider | Gemini Batch API (`GEMINI_API_KEY`) |
| Context | 12 sentences each side (`context_sentences=12`) |
| Temperature | 0 |
| `max_output_tokens` | **2048** (1024 caused 12% parse failures) |
| Thinking | `thinking_budget=-1` (dynamic; cannot disable on 2.5 Pro) |

**Note:** On direct Gemini API, thinking and visible JSON share the `max_output_tokens` ceiling. OpenRouter/Excel `max_tokens=256` is not comparable.

---

## Token usage per request

| Component | Excel estimate | **Pilot actual @ 2048** (989 req) |
|-----------|----------------|-----------------------------------|
| Input | ~620 | **~934** |
| Visible JSON | ~85 | **~73** |
| Thinking | ~500–800 | **~701** |
| **Output (billed)** | **~700** | **~774** |

Pilot job (validated): `outputs/runs/dprose_batch/2026-06-20-dprose-batch-pilot-2048/pilot_summary.json`  
Prior 1024 run (superseded): `outputs/runs/dprose_batch/2026-06-19-dprose-batch-pilot/pilot_summary.json`

---

## Pricing (Gemini 2.5 Pro, batch tier)

| | Per 1M tokens |
|--|---------------|
| Input | $0.625 |
| Output (incl. thinking) | $5.00 |

---

## Cost projections

### Pilot (done)

| | |
|--|--|
| Files | `dprose_100`, `dprose_806`, `dprose_2158` |
| Sentences | 989 |
| Actual cost @ 2048 | **$4.40** |
| Parse rate @ 2048 tokens | **99.9%** (988/989) |
| Parse rate @ 1024 tokens | 88% (118 failures; fixed by 2048) |

### Full corpus (120,369 sentences)

Using pilot averages @ 2048 (934 in + 774 out):

| | Tokens | Batch cost |
|--|--------|------------|
| Input | 112.4M | ~$70 |
| Output | 91.2M | ~$456 |
| **Total** | | **~$526** |

Add ~$15–30 headroom for `max_output_tokens=2048` on long-thinking sentences → **~$540–560**.

**If thinking capped at 512** (cost-saving, quality risk): ~577 out/request → **~$417 batch**.

| Scenario | Batch cost |
|----------|------------|
| **Recommended** (2048 cap, dynamic thinking) | **$520–560** |
| Thinking capped (512–768) | $400–490 |
| Standard (non-batch) API | ~2× batch |

---

## Runtime

Batch API SLO: up to 24h. Pilot (989 req): **~4 min** wall (submit → complete; `job_meta.json` → `pilot_summary.json`). Extrapolated full corpus (120,369 req, same config): **~8 h** at pilot throughput (~4.1 req/s); likely **4–12 h** in practice (queue load, batch chunking). No concurrency tuning needed (async batch).

---

## Output format

```json
{
  "sentence_index": 42,
  "sentence_text_full": "...",
  "prediction_label": "BORDER",
  "prediction_bool": true,
  "raw_model_response": "{\"label\":\"BORDER\",\"reason\":\"...\"}",
  "parse_ok": true,
  "source_file": "dprose_100.csv"
}
```

Runner: `src/runners/run_dprose_batch_pilot.py`  
Prep: `scripts/data/prepare_dprose_prompting_inputs.py`

---

## Next steps

1. ~~Re-run pilot at `max_output_tokens=2048`; confirm parse rate ≥ 95%.~~ **Done** — 99.9% (988/989), $4.40 batch.
2. Full run: chunk 327 files into ~10–20 JSONL batches (~6k–12k req each).
3. Optional: re-run single residual failure (`dprose_100:22`, thought_tokens=1973) at 4096.
4. Optional post-process: `min_scene_len_5` (as in Excel experiments).
