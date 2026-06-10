#!/usr/bin/env python3
"""Evaluate a fine-tuned (LoRA) model on a held-out fold with tolerant F1.

Loads a base model + LoRA adapter, runs greedy inference over a fold's
``eval.jsonl`` (the held-out novel at full natural distribution), parses the
BORDER/NOBORDER label from each generation, and scores P/R/F1 at tolerances
0/1/3 using the same scorer as the prompting runner
(``src.postprocess.evaluate_sampled``). Optionally applies a post-processing
scenario before scoring.

This runs on a local CUDA GPU (or HF Jobs). Heavy ML imports happen inside main so
the module stays importable for linting/smoke checks.

Run (e.g. after a train-only Job, or to re-score an adapter)::

    python src/finetune/eval_finetuned.py \\
        --adapter your-hf-user/scene-seg-llama-3-2-3b-instruct-fold_A \\
        --eval data/processed/finetune/fold_A/eval.jsonl \\
        --family L --tolerances 0 1 3 --postprocess min_scene_len_3
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

_FILE = Path(__file__).resolve()
_SRC_ROOT = _FILE.parents[1]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from core.prompt_runtime import parse_family_output
from postprocess.postprocess import apply_scenario, evaluate_sampled


def read_eval_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _confidence_of(parsed_payload: Any) -> float | None:
    if isinstance(parsed_payload, dict):
        value = parsed_payload.get("confidence")
        try:
            return float(value) if value is not None else None
        except Exception:  # noqa: BLE001
            return None
    return None


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--adapter", required=True, help="HF repo or local path of the LoRA adapter")
    parser.add_argument("--base_model", default=None,
                        help="Base model id (default: read adapter config)")
    parser.add_argument("--eval", type=Path, required=True, help="Path to fold eval.jsonl")
    parser.add_argument("--family", default="L", help="Prompt family used for parsing (default: L)")
    parser.add_argument("--tolerances", type=int, nargs="+", default=[0, 1, 3])
    parser.add_argument("--postprocess", default="none",
                        help="Optional post-processing scenario before scoring")
    parser.add_argument("--confidence_threshold", type=float, default=0.85)
    parser.add_argument("--max_new_tokens", type=int, default=96)
    parser.add_argument("--limit", type=int, default=0, help="Eval only first N rows (0 = all)")
    parser.add_argument("--use_unsloth", action="store_true",
                        help="Load via Unsloth FastLanguageModel (faster on Kaggle)")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    import torch  # noqa: PLC0415

    rows = read_eval_jsonl(args.eval)
    if args.limit > 0:
        rows = rows[: args.limit]

    if args.use_unsloth:
        from unsloth import FastLanguageModel  # noqa: PLC0415

        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=args.adapter, max_seq_length=1024, load_in_4bit=True, dtype=None
        )
        FastLanguageModel.for_inference(model)
    else:
        from peft import AutoPeftModelForCausalLM  # noqa: PLC0415
        from transformers import AutoTokenizer  # noqa: PLC0415

        model = AutoPeftModelForCausalLM.from_pretrained(
            args.adapter, device_map="auto", torch_dtype="auto", load_in_4bit=True
        )
        tokenizer = AutoTokenizer.from_pretrained(args.adapter)

    model.eval()
    device = next(model.parameters()).device

    indices: List[int] = []
    preds: List[str] = []
    golds: List[str] = []
    confidences: List[float | None] = []

    for n, row in enumerate(rows):
        user_msg = row["messages"][0]["content"]
        prompt = tokenizer.apply_chat_template(
            [{"role": "user", "content": user_msg}],
            tokenize=False,
            add_generation_prompt=True,
        )
        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        with torch.no_grad():
            gen = model.generate(
                **inputs, max_new_tokens=args.max_new_tokens, do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )
        text = tokenizer.decode(gen[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        parsed = parse_family_output(args.family, text)
        label = parsed.label if parsed.is_valid and parsed.label else "NOBORDER"
        indices.append(int(row.get("index", n)))
        preds.append(label)
        golds.append(str(row["label"]).upper())
        confidences.append(_confidence_of(parsed.payload))

    size = max(indices) + 1
    full_gold = ["NOBORDER"] * size
    for idx, gold in zip(indices, golds):
        full_gold[idx] = gold

    final_preds = apply_scenario(
        preds, args.postprocess, confidences=confidences,
        confidence_threshold=args.confidence_threshold,
    )

    metrics = {
        f"tol_{t}": evaluate_sampled(indices, final_preds, full_gold, t)
        for t in args.tolerances
    }
    report = {
        "adapter": args.adapter,
        "eval": str(args.eval),
        "family": args.family,
        "postprocess": args.postprocess,
        "n_eval": len(rows),
        "n_gold_border": sum(1 for g in golds if g == "BORDER"),
        "n_pred_border": sum(1 for p in final_preds if p == "BORDER"),
        "metrics": metrics,
    }
    print(json.dumps(report, indent=2))
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
