# Nemotron-3-Super-120B Parameter Memo

Reference for all Nemotron parameters relevant to our prompting experiments.
Source: [HF model card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16)

## Model Facts

| Property | Value |
|---|---|
| Total parameters | 120B (12B active) |
| Architecture | LatentMoE: Mamba-2 + MoE + Attention hybrid with MTP |
| Max context length | 1M tokens (default 256k) |
| Supported languages | English, French, **German**, Italian, Japanese, Spanish, Chinese |
| Min GPU requirement | 8x H100-80GB (BF16) |
| Release date | 2026-03-11 |
| License | NVIDIA Nemotron Open Model License |

## NVIDIA-Recommended Parameters

Use these for ALL tasks and serving backends:

```
temperature = 1.0
top_p = 0.95
```

Do not change these without a specific experiment justifying it.

## Experimental Overrides (for our protocol)

NVIDIA defaults are the reference point. For prompt-family evaluation sweeps, we
override some settings for reproducibility and cost control:

- `temperature=0` for deterministic comparisons
- fixed `seed` when supported
- short `max_tokens` to limit verbose reasoning spillover
- strict JSON output mode for structured prompt families when supported

Always log both requested settings and effective settings returned by provider.

## Reasoning Modes

The model generates an internal reasoning trace (`<think>...</think>`) before
the final answer. Three modes are available:

| Mode | Via OpenRouter | Via HF/vLLM direct | Behavior |
|---|---|---|---|
| Full reasoning (default) | `reasoning: {effort: "high"}` | `enable_thinking: True` | Extended chain-of-thought before answer |
| No reasoning | `reasoning: {effort: "none"}` | `enable_thinking: False` | Direct answer, minimal output tokens |
| Low-effort reasoning | `reasoning: {effort: "low"}` | `enable_thinking: True, low_effort: True` | Brief reasoning, fewer tokens |

### How we use it

In `run_prompting_stratified.py`, reasoning is controlled via `--reasoning on/off`:

```python
reasoning_kwargs = {
    "extra_body": {
        "reasoning": {"effort": "high"} if args.reasoning == "on"
        else {"effort": "none"},
    }
}
```

To add low-effort mode, use `{"effort": "low"}`.

## Budget-Controlled Reasoning

Cap thinking tokens with `reasoning_budget` (integer). The model closes the
reasoning trace at the next newline before budget is hit. Hard stop at
`reasoning_budget + 500` if no newline is found.

Example via OpenAI-compatible API:

```python
response = client.chat.completions.create(
    model=MODEL,
    messages=[...],
    max_tokens=1024,
    temperature=1.0,
    top_p=0.95,
    extra_body={"chat_template_kwargs": {"enable_thinking": True}},
)
```

For budget control, see the `ThinkingBudgetClient` pattern in the HF model card.

## Output Structure

For structured/short output in our classification task:

- The model supports tool-calling format and JSON mode
- For our binary classifier, force short answers via prompt instructions:
  "Reply with exactly True or False on the first line, then a one-sentence reason"
- Add `max_tokens=256` to prevent verbose output (our parser only reads the
  first line anyway)

## OpenRouter Interoperability and Caveats

OpenRouter provides a unified API, but feature support still varies by model.

### Structured outputs

- `response_format={"type":"json_object"}` is broadly available
- strict `json_schema` mode is only available on compatible models
- when unsupported, models may return free-form text even if JSON was requested

### Parameter variability

The following parameters are provider/model dependent in practice:

- `top_k`
- `min_p`
- `seed`
- `response_format`
- `stop`
- `max_tokens` limits

Some models silently ignore unsupported keys. For experimental integrity, store
request payload and raw response metadata with each run.

### Reasoning controls

For Nemotron via OpenRouter, reasoning is typically exposed through
`extra_body.reasoning.effort` values (`high`, `none`, and sometimes `low`).
Availability of low-effort behavior can differ by backend/router path.

## Context Window

- OpenRouter default: 262,144 tokens (more than enough for all our experiments)
- Our `context_size` parameter (409, 1024, 2048, 4096) controls how many tokens
  of surrounding narrative text are sent **per sentence**, not the model's
  internal context window
- The model handles up to 1M tokens if explicitly configured

## Key Links

- Model card: https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16
- Technical report: https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3-Super-Technical-Report.pdf
- OpenRouter (free): https://openrouter.ai/nvidia/nemotron-3-super-120b-a12b:free/api
- OpenRouter (paid): https://openrouter.ai/nvidia/nemotron-3-super-120b-a12b
- vLLM cookbook: https://github.com/NVIDIA-NeMo/Nemotron/blob/main/usage-cookbook/Nemotron-3-Super/vllm_cookbook.ipynb
- SGLang cookbook: https://github.com/NVIDIA-NeMo/Nemotron/blob/main/usage-cookbook/Nemotron-3-Super/sglang_cookbook.ipynb
- Advanced deployment: https://github.com/NVIDIA-NeMo/Nemotron/tree/main/usage-cookbook/Nemotron-3-Super/AdvancedDeploymentGuide
- NVFP4 quantized: https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-NVFP4
- arxiv (architecture): https://arxiv.org/abs/2512.20848
- arxiv (family overview): https://arxiv.org/abs/2512.20856

## Benchmarks (Relevant Subset)

| Benchmark | Nemotron 3 Super | GPT-OSS-120B |
|---|---|---|
| MMLU-Pro | 83.73 | 81.00 |
| GPQA (no tools) | 79.23 | 80.10 |
| IFBench (prompt) | 72.56 | 68.32 |
| MMLU-ProX (multilingual avg) | 79.36 | 76.59 |
| RULER @ 256k | 96.30 | 52.30 |

Nemotron excels at long-context and multilingual tasks. GPT-OSS is slightly
better on some reasoning benchmarks but much worse on long context.
