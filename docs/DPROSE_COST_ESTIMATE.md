# dProse Corpus Scene Segmentation — Cost Estimate

**Date:** 2026-06-05  
**Model:** Gemini 2.5 Pro with reasoning ON  
**Task:** Scene boundary annotation (BORDER / NOBORDER per sentence)

---

## 1) Corpus Summary

| Metric | Value |
|--------|-------|
| Total CSV files | 327 |
| Total sentences | 120,369 |
| Total characters | 14,469,653 |
| Average chars/sentence | 120.2 |
| Estimated tokens (chars/4) | ~3.6M |

**Note:** Unlike the Excel experiments (Gaensemagd + Kleist), there are **no gold labels** for dProse. The output will be model predictions only (BORDER/NOBORDER per sentence).

---

## 2) Approach

Following the best-performing configuration from the Excel experiments:

| Setting | Value |
|---------|-------|
| Model | `google/gemini-2.5-pro` |
| Provider | OpenRouter |
| Prompt family | **B** (zero-shot JSON) |
| Reasoning mode | **ON** (high effort) |
| Temperature | 0.0 (deterministic) |
| Response format | JSON schema |
| max_tokens | 256 |

**Prompt B structure:**
- Task instruction (~90 tokens)
- Left context (several preceding sentences)
- Target sentence
- Right context (several following sentences)
- JSON output request

---

## 3) Token Estimates per Request

Based on the Excel experiment data (`summary.json` from `2026-05-31-excel-gemini-reasoning-on`):

| Component | Tokens (estimated) |
|-----------|-------------------|
| Prompt template | ~90 |
| Left context (6-12 sentences) | ~250 |
| Target sentence | ~30 |
| Right context (6-12 sentences) | ~250 |
| **Total input** | **~620** |

| Output Component | Tokens (estimated) |
|------------------|-------------------|
| Visible response (JSON + reason) | ~85 |
| Thinking tokens (reasoning ON) | ~500-800 |
| **Total output** | **~700** |

**Reference from actual experiments:**
- `avg_output_chars`: 338.84 (~85 visible tokens)
- `avg_latency_seconds`: 3.43 (indicates substantial reasoning)
- Reasoning tokens typically 5-10x visible output

---

## 4) Pricing (Gemini 2.5 Pro via OpenRouter)

| Tier | Input (per 1M tokens) | Output (per 1M tokens) |
|------|----------------------|------------------------|
| Standard (≤200K context) | $1.25 | $10.00 |
| Batch/Flex (50% off) | $0.625 | $5.00 |

**Note:** Output pricing includes thinking tokens when reasoning is enabled.

---

## 5) Cost Calculation

### Conservative Estimate
Using 700 input + 800 output tokens per request:

| Component | Calculation | Cost |
|-----------|-------------|------|
| Input tokens | 120,369 × 700 = 84.26M | 84.26 × $1.25 = **$105.32** |
| Output tokens | 120,369 × 800 = 96.30M | 96.30 × $10.00 = **$962.95** |
| **Total (standard)** | | **$1,068.27** |

### With Batch Pricing (50% off)
| Component | Calculation | Cost |
|-----------|-------------|------|
| Input tokens | 84.26M | 84.26 × $0.625 = **$52.66** |
| Output tokens | 96.30M | 96.30 × $5.00 = **$481.48** |
| **Total (batch)** | | **$534.14** |

### Optimistic Estimate (lower reasoning tokens)
Using 600 input + 500 output tokens per request:

| Tier | Input Cost | Output Cost | **Total** |
|------|------------|-------------|-----------|
| Standard | $90.28 | $601.85 | **$692.12** |
| Batch | $45.14 | $300.92 | **$346.06** |

---

## 6) Summary: Expected Cost Range

| Scenario | Estimated Cost |
|----------|----------------|
| **Conservative (standard)** | **$1,000 - $1,100** |
| **Conservative (batch)** | **$500 - $550** |
| **Optimistic (standard)** | **$690 - $750** |
| **Optimistic (batch)** | **$345 - $380** |

**Recommended budget:** **$600 - $1,100** depending on:
- Whether batch pricing is available
- Actual reasoning token consumption

---

## 7) Runtime Estimate

Based on `avg_latency_seconds: 3.43` from Excel experiments:

| Metric | Calculation |
|--------|-------------|
| Latency per request | ~3.5 seconds |
| Sequential time | 120,369 × 3.5s = 421,292s ≈ **117 hours** |
| With parallelism (10 concurrent) | ~12 hours |
| With parallelism (50 concurrent) | ~2.5 hours |

**Note:** Rate limits apply (Tier 1: 150 RPM, Tier 2: 1000 RPM, Tier 3: 2000 RPM).

---

## 8) Output Format

Each sentence will receive:

```json
{
  "sentence_index": 42,
  "sentence_text_full": "...",
  "prediction_label": "BORDER" | "NOBORDER",
  "prediction_bool": true | false,
  "raw_model_response": "{ \"label\": \"BORDER\", \"reason\": \"...\" }",
  "parse_ok": true,
  "latency_seconds": 3.2,
  "source_file": "dprose_100.csv"
}
```

---

## 9) Comparison with Excel Experiments

| Metric | Excel (Kleist + Gaensemagd) | dProse (full corpus) |
|--------|----------------------------|---------------------|
| Sentences | 316 | 120,369 |
| Scale factor | 1× | **381×** |
| Est. cost (standard) | ~$3 | ~$1,000 |
| Has gold labels | ✓ | ✗ |

---

## 10) Recommendations

1. **Start with a pilot run** on 2-3 files (~1,000 sentences) to verify:
   - Token consumption matches estimates
   - Parse success rate
   - Output quality

2. **Use batch pricing** if available (halves the cost)

3. **Consider post-processing** with `min_scene_len_5` rule to reduce overprediction (as shown in Excel experiments)

4. **Budget allocation:**
   - Pilot: ~$10
   - Full run: $600-$1,100
   - **Total: $650-$1,200**
