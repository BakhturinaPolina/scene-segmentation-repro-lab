# Performance Optimization Note

**Date:** 2026-04-09

## Current Bottleneck

~12 s/sentence via OpenRouter free tier (rate limits + reasoning token overhead).
Full novel (~5,500 sentences) = ~18 hours per config. Two novels = ~36 hours.
With 4+ configs to test, this is ~6 days of sequential API calls.

## Optimization Options

### 1. Reasoning OFF or low-effort mode

Nemotron supports three modes: full reasoning, low-effort, and no reasoning.
Reasoning OFF (`enable_thinking: False`) skips the internal chain-of-thought,
cutting output tokens from ~2,000+ to ~50. This alone can halve latency.
Low-effort mode (`low_effort: True`) is a middle ground.

Already planned as Config B/D in our experimental design.

### 2. Constrain output length

Add `max_tokens=256` (or even 128) to prevent verbose responses. Our classifier
only needs "True"/"False" + a one-sentence reason. Currently the model sometimes
generates 500+ tokens of reasoning even when we only parse the first line.

Implementation: add `max_tokens` parameter to `get_chain()` in `classify.py`.

### 3. OpenRouter paid tier

- Pricing: $0.10/M input tokens, $0.50/M output tokens
- Removes rate limits entirely
- Estimated cost per full-eval config (~11k sentences):
  - Reasoning ON: ~$3--5
  - Reasoning OFF: ~$1--2
- Link: https://openrouter.ai/nvidia/nemotron-3-super-120b-a12b

### 4. Parallel requests

OpenRouter paid tier supports concurrent requests. Running 5--10 in parallel
would reduce wall-clock time by the same factor. Requires refactoring
`classify_sample()` to use `asyncio` + `aiohttp` or `concurrent.futures`.

### 5. Local model

Nemotron-3-Super-120B requires 8x H100-80GB for BF16. Not feasible on our
RTX 2070 (8 GB VRAM).

Alternatives:
- **NVFP4 quantized variant** — still needs B200 or DGX Spark.
  https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-NVFP4
- **Smaller models via Ollama** — Qwen3.6-Plus or Gemma-4-26B fit in 8 GB
  VRAM with 4-bit quantization, but quality drops significantly per our sweep
  (miss all borders).
- **Cloud GPU** — rent 8x H100 on Lambda, RunPod, or vast.ai (~$25/hour).
  Only worthwhile if we need many runs.

### 6. Budget-controlled reasoning

Cap thinking tokens with `reasoning_budget` parameter (e.g., 512 tokens) while
keeping reasoning ON. Model closes trace at next newline before budget; hard stop
at budget+500. Keeps some reasoning benefit at lower cost.

See HF model card `ThinkingBudgetClient` example:
https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16#quick-start-guide

### 7. Strict JSON outputs for sweep reliability

For prompt families with structured outputs (B, C, D, E, F, G, I, J), enforce
JSON mode whenever the selected model supports it. This reduces parse failures
and re-run overhead in large sweeps.

Use `response_format={"type":"json_object"}` (or `json_schema` for compatible
models) and keep response bodies short.

### 8. Two-stage run policy (screen then narrow)

For the A--J template grid, minimize runtime by separating exploration from
verification:

1. run broad screening with `openrouter/free` and strict short outputs
2. keep top 2--3 prompt families
3. rerun only those on pinned free models
4. continue with top 1--2 settings

This avoids expensive full sweeps on every model.

## Parameter support caveat

OpenRouter exposes parameters like `temperature`, `top_p`, `top_k`, `min_p`,
`seed`, `stop`, `max_tokens`, and structured response formats, but support can
vary by model/provider and can change over time. Treat unsupported settings as
best-effort and always log what was actually honored.

## Recommendation (current)

1. Start with **reasoning OFF** (Config B) to establish a speed baseline
2. Use strict JSON mode + `max_tokens<=256` for prompt-family sweeps
3. Use two-stage policy: `openrouter/free` screen, then narrowed reruns
4. If full-eval runs are needed at scale, switch to **paid tier** (~$2--5/run)
5. Parallelize requests only if paid tier is available and we need many configs
