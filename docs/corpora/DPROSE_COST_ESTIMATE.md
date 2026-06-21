# dProse Corpus Scene Segmentation — Cost Estimate

**Updated:** 2026-06-21  
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

## Configuration

| Setting | Value |
|---------|-------|
| Model | `gemini-2.5-pro` |
| Prompt | Family **B** + `json_schema_label_reason.json` |
| Provider | Gemini Batch API (`GEMINI_API_KEY`) |
| Context | 12 sentences each side (`context_sentences=12`) |
| Temperature | 0 |
| `max_output_tokens` | 2048 |
| Thinking | `thinking_budget=-1` (dynamic) |

---

## Token usage per request (pilot @ 2048, 989 requests)

| Component | Tokens |
|-----------|--------|
| Input | ~934 |
| Visible JSON | ~73 |
| Thinking | ~701 |
| **Output (billed)** | **~774** |

Pilot summary: `outputs/runs/dprose_batch/2026-06-20-dprose-batch-pilot-2048/pilot_summary.json`

---

## Pricing (Gemini 2.5 Pro, batch tier)

| | Per 1M tokens |
|--|---------------|
| Input | $0.625 |
| Output (incl. thinking) | $5.00 |

---

## Pilot (done)

| | |
|--|--|
| Files | `dprose_100`, `dprose_806`, `dprose_2158` |
| Sentences | 989 |
| Cost | **$4.40** |
| Parse rate | **99.9%** (988/989) |

---

## Full corpus estimate (120,369 sentences)

Using pilot averages (934 in + 774 out):

| | Tokens | Batch cost |
|--|--------|------------|
| Input | 112.4M | ~$70 |
| Output | 91.2M | ~$456 |
| **Total** | | **~$526** |

With headroom for long-thinking sentences: **~$540–560**.

### Label only (no `reason` in output)

If only BORDER / NOBORDER is kept per sentence (no visible `reason` field; internal thinking still billed on 2.5 Pro):

| | Tokens / req | Full corpus tokens | Batch cost |
|--|--------------|-------------------|------------|
| Input | ~934 | 112.4M | ~$70 |
| Output (thinking + label JSON) | ~706 (~701 thinking + ~5 visible) | 85.0M | ~$425 |
| **Total** | | | **~$495** |

Pilot @ label-only visible output: **~$4.07** (vs $4.40 with reason). Saves **~$40** on full run (~8%) — most cost is internal thinking, not the printed reason.

---

## Runtime

Pilot (989 req): **~4 min** (submit → complete).  
Full corpus (120,369 req): **~8 h** at pilot throughput; likely **4–12 h** in practice (queue load, batch chunking).

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
