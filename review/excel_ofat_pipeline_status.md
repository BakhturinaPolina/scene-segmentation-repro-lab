# Excel OFAT improvement pipeline — status

**Updated:** 2026-06-15 (in progress)

## Step 1 — Prompt O full eval

| Model | Status | Notes |
|-------|--------|-------|
| Nemotron Super | **In progress** | Gänsemagd 71/71 done; Kleist **175/245** cached |
| Laguna XS | Pending | After Nemotron |

**Early Gänsemagd signal (O vs Q):**

| | F3@3 | R@3 | Over-pred |
|---|------|-----|---------|
| O | 0.429 | **0.86** | **4.1×** |
| Q | 0.615 | 0.57 | 1.0× |

O recovers recall on fairy tale but over-segments again → step 3 condition **met**.

**Blocker:** OpenRouter `free-models-per-day` rate limit on Kleist.

Resume:
```bash
DATE_TAG=2026-06-14-excel-ofat-O RESUME=1 bash scripts/sweeps/excel_ofat_prompt_O_top2.sh
```

## Step 2 — Verify Q caches ✓

| Model | Verified borders | Rejected | F3@3 change |
|-------|------------------|----------|-------------|
| Nemotron Super + Q | 19 | 0 | unchanged (0.604) |
| Laguna XS + Q | 31 | 0 | unchanged (0.591) |

Verify keeps all borders — no precision gain on under-predicting Q runs.

Reports: `review/verify_Q_nemotron.json`, `review/verify_Q_laguna_xs.json`

## Step 3 — min_gap on Laguna XS Kleist ✓

Condition met (O recall↑, over-pred↑ vs Q). Applied offline on **Laguna XS Kleist Q** cache:

| min_gap | F3@3 | Pred borders |
|---------|------|--------------|
| raw | 0.514 | 22 |
| **2–3** | **0.545** | 19 |

Report: `review/postprocess_laguna_xs_kleist_min_gap.json`

## Step 4 — Context windows (pending)

Best F3 so far: **0.604** (Nemotron Super + Q) < gate 0.76.

Will run after step 1 completes (avoid API contention):
```bash
python scripts/evaluation/excel_ofat_improve_pipeline.py --step context
```

Or full resume:
```bash
bash scripts/sweeps/excel_ofat_resume_pipeline.sh
```

## Best candidates (F3@3)

1. Nemotron Super + Q — **0.604** (over-pred 0.9×)
2. Laguna XS + Q — 0.591 (over-pred 1.5×)
3. Laguna XS Kleist + min_gap — 0.545 (partial doc only)
