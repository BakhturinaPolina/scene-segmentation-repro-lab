# Prompting Free-Model Sweep (10 Sentences, Ordered)

- **Dataset slice:** first 10 sentences of `Aus guter Familie.xmi.zip`
- **Run folder:** `outputs/prompting/2026-04-08/free_model_sweep_10_ordered_fast/`
- **Important:** This is a tiny, highly imbalanced slice (`true_borders=1`), so accuracy alone is not robust.

| Order | Model | Accuracy | Predicted Borders | Failed to Classify | Elapsed (s) | Notes |
|---|---|---:|---:|---:|---:|---|
| 1 | `nvidia/nemotron-3-super-120b-a12b:free` | 1.00 | 1 | 0 | 127.8 | Strong + stable |
| 2 | `google/gemma-4-26b-a4b-it:free` | 0.90 | 0 | 5 | 196.9 | Heavy rate limits |
| 3 | `qwen/qwen3.6-plus:free` | 0.90 | 0 | 10 | 2.5 | Fully failed, defaulted NOBORDER |
| 4 | `nvidia/nemotron-3-super-120b-a12b:free` | 1.00 | 1 | 0 | 175.0 | Repeat confirms stability |
| 5 | `liquid/lfm-2.5-1.2b-thinking:free` | 0.30 | 8 | 0 | 21.5 | Over-predicts BORDER |
| 6 | `qwen/qwen3-next-80b-a3b-instruct:free` | 0.90 | 0 | 10 | 309.1 | Fully failed, defaulted NOBORDER |
| 7 | `openai/gpt-oss-120b:free` | 1.00 | 1 | 0 | 36.0 | Best speed/reliability tradeoff |
| 8 | `cognitivecomputations/dolphin-mistral-24b-venice-edition:free` | 0.90 | 0 | 10 | 312.9 | Fully failed, defaulted NOBORDER |

## Recommendation

Try first: `openai/gpt-oss-120b:free`

Why:
- 0 failed classifications on this sweep
- Correct border behavior (`predicted_borders=1` for `true_borders=1`)
- Fastest among reliable models (36.0s for 10 sentences)

Second choice: `nvidia/nemotron-3-super-120b-a12b:free` (also reliable, but slower).

## Next Stratified Trial (>=30 sentences with richer metrics)

Use `src/run_prompting_stratified.py` to get tolerance metrics (`tol_0`, `tol_1`, `tol_3`) and class-balanced sampling:

```bash
OPENROUTER_API_KEY=... .venv/bin/python src/run_prompting_stratified.py \
  --model "openai/gpt-oss-120b:free" \
  --max_per_class 15 \
  --date 2026-04-08-stratified-gptoss
```

This gives **30 sampled sentences per novel** (15 BORDER + 15 NOBORDER), i.e. 60 total across both novels, with precision/recall/F1 at multiple tolerances.
