# Progress Report: Scene Segmentation Research

**Date:** 2026-04-09
**Project goal:** Replicate and extend LLM-based scene boundary detection from the NAACL 2025 paper (LSX-UniWue/scene-segmentation) using free-tier models via OpenRouter.

## Data Available

Only STSS-Test-2 (two public-domain German novels). The paper's full Test-Full corpus is not yet accessible.

| Novel | Total sentences | Gold BORDER | Natural BORDER rate |
|---|---|---|---|
| *Aus guter Familie* | 5,025 | 219 | 4.36% |
| *Effi Briest* | 5,906 | 227 | 3.84% |

## Work Completed

### Phase 0--2: Environment Setup (2026-03-31)

- Repository structure, dual virtual environments (`.venv` CPU, `.venv-gpu` GPU)
- Dependency pinning: `transformers==4.46.3`, `langchain==0.1.9`, `torch==2.5.1+cpu`
- GPU env validated: RTX 2070 Max-Q, Unsloth 2026.3.18, torch 2.10.0+cu128
- Full smoke tests documented in `docs/PHASE2_PHASE3_NOTES.md`

### Phase 3.1: SSC Baseline (2026-04-05)

BERT-German-cased trained on upstream data, evaluated on STSS-Test-2:

| Document | P | R | F1 |
|---|---|---|---|
| Aus guter Familie | 1.000 | 0.005 | 0.009 |
| Effi Briest | 1.000 | 0.004 | 0.009 |
| **Macro avg** | | | **0.009** |

Model predicts exactly one BORDER per novel. This is a training failure (undertrained / label imbalance), not an architecture failure. Paper's GBERT-Large achieves F1=0.66 on same data.

### Phase 3.2: Prompting Pipeline (2026-04-05 -- 2026-04-08)

**Pipeline validation** (2026-04-05): 20 sentences with Qwen3.6-Plus via OpenRouter. Pipeline works; 100% accuracy on trivial sample.

**Free model sweep** (2026-04-08): 8 models x 10 sentences.

| Model | Accuracy | Pred BORDERs | Verdict |
|---|---|---|---|
| nvidia/nemotron-3-super-120b-a12b:free | 0.9--1.0 | 1--2 | Best recall |
| openai/gpt-oss-120b:free | 1.0 | 1 | Precise, conservative |
| qwen/qwen3.6-plus:free | 0.9 | 0 | Misses border |
| google/gemma-4-26b-a4b-it:free | 0.9 | 0 | Misses border |
| liquid/lfm-2.5-1.2b-thinking:free | 0.3 | 8 | Hallucinating |

Only Nemotron and GPT-OSS warranted full evaluation.

**GPT-OSS pilot** (2026-04-08): n=60 stratified, macro F1=0.696 (P=1.000, R=0.533). Perfect precision but misses ~47% of borders.

**Nemotron full stratified** (2026-04-08): n=892 (all BORDERs + matched NOBORDERs):

| Tolerance | P | R | F1 |
|---|---|---|---|
| tol=0 | 0.890 | 0.652 | 0.753 |
| tol=1 | 0.901 | 0.659 | 0.761 |
| tol=3 | 0.933 | 0.688 | 0.792 |

Recall is the bottleneck (~35% of borders missed). Runtime: ~3 hours for 892 sentences on free tier.

### Phase 3.3: LLaMA Fine-tuning (2026-04-05)

Dry run of LLaMA-3 8B via Unsloth: OOM on RTX 2070 (8 GB VRAM). Needs larger GPU or quantization.

## Critical Caveat: Sampling Bias

Our stratified evaluation uses a 50/50 BORDER/NOBORDER sample. The paper evaluates the natural ~4% BORDER distribution. This inflates our precision because the model only sees 219 NOBORDER sentences instead of the real ~4,800+.

| | Aus guter Familie | Effi Briest |
|---|---|---|
| FP observed (219 NOBORDER) | 23 | 13 |
| FP rate | 10.5% | 5.7% |
| Real NOBORDER sentences | 4,806 | 5,679 |
| Extrapolated FPs (full doc) | ~504 | ~325 |
| Reported F1 (tol=0) | 0.730 | 0.775 |
| **Corrected F1 (tol=0, est.)** | **~0.32** | **~0.43** |

**Corrected macro F1 (tol=0): ~0.38.** At tol=3: estimated ~0.42--0.50.

## Comparison vs. Paper

| Approach | Model | F1 (tol=3) | Notes |
|---|---|---|---|
| Zero-shot (paper) | GPT-4o | 0.45 | Test-Full, natural distribution |
| Zero-shot (paper) | Llama3:70b / 405b | 0.34 | Test-Full |
| **Zero-shot (ours, corrected)** | **Nemotron-3-Super-120b** | **~0.42--0.50** | **STSS-Test-2 only; estimated** |
| Zero-shot (ours, as reported) | Nemotron-3-Super-120b | 0.792 | Inflated by stratified eval |
| Supervised (paper) | Llama3:8b CoT-List fine-tune | 0.63 | STSS-Test-2 |
| Supervised (paper) | GBERT-Large + Half Stride | 0.66 | STSS-Test-2 |
| Supervised (ours) | BERT-German-cased | ~0.009 | Training failure |

Nemotron zero-shot is roughly at GPT-4o level once corrected. A ~0.15--0.20 F1 gap remains between best zero-shot and the supervised ceiling.

## Next Experimental Protocol (Approved)

Going forward, experiments follow an OpenRouter baseline-first workflow:

1. **Prompt search:** run prompt families A--J with `openrouter/free`
2. **Model search:** keep top 2--3 prompt families, then run them on pinned free models by bucket (small instruct, larger instruct, reasoning-capable)
3. **Focused iteration:** continue only with top 1--2 model/prompt combinations

Fixed controls for fair comparison:

- same left/right context window
- same sentence marker format
- same evaluator and tolerance settings
- same output schema per prompt family
- decoding defaults: `temperature=0`, fixed `seed` when supported, short `max_tokens`

Important: historical numbers above were produced under the previous stratified-heavy protocol and should not be mixed with future full-eval numbers.

## Current Status

- Config C (CoT-List prompt + reasoning ON, context=4096) is in progress (partial cache for Aus guter Familie)
- Configs B and D not yet started
- Full-eval mode (natural class distribution) not yet implemented

## Known Issues

1. **Sampling bias** -- stratified evaluation inflates precision; must implement full-eval mode
2. **SSC baseline undertrained** -- F1=0.009 vs paper's 0.66; needs proper training run
3. **LLaMA OOM** -- 8B model does not fit RTX 2070; needs quantization or cloud GPU
4. **Rate limits** -- OpenRouter free tier: ~12s/sentence average; full novel takes ~17 hours
