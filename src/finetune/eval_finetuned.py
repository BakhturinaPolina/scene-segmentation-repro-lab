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
from typing import Any, Dict, List, Optional

_FILE = Path(__file__).resolve()
_SRC_ROOT = _FILE.parents[1]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from finetune.label_parse import (  # noqa: E402
    DEFAULT_MAX_NEW_TOKENS,
    TARGET_FORMATS,
    build_eval_warnings,
    diagnose_generation,
    load_job_meta,
    parse_eval_label,
    recommended_max_new_tokens,
    summarize_parse_diagnostics,
)
from core.workflow_runtime import project_root
from finetune.run_log import append_jsonl, log, progress, row_key, upload_if_hub
from postprocess.postprocess import apply_scenario, evaluate_sampled

_DEFAULT_PARTIAL = (
    project_root(_FILE) / "outputs/runs/llama/eval-cache/eval_partial.jsonl"
)


def read_eval_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _dataset_sanity(rows: List[Dict[str, Any]], meta: Dict[str, Any]) -> Dict[str, int]:
    n_gold_border = sum(1 for r in rows if str(r.get("label", "")).upper() == "BORDER")
    n_gold_noborder = sum(1 for r in rows if str(r.get("label", "")).upper() == "NOBORDER")
    stats = {
        "n_rows": len(rows),
        "n_gold_border": n_gold_border,
        "n_gold_noborder": n_gold_noborder,
    }
    if meta:
        stats["meta_eval_border"] = int(meta.get("eval_border", 0))
        stats["meta_eval_noborder"] = int(meta.get("eval_noborder", 0))
        stats["meta_target_format"] = str(meta.get("target_format", ""))
    return stats


def _resolve_target_format(arg_format: str, meta: Dict[str, Any]) -> str:
    if arg_format != "auto":
        return arg_format
    tf = str(meta.get("target_format", "")).strip()
    return tf if tf in TARGET_FORMATS else "cot_list"


def _resolve_max_new_tokens(
    explicit: Optional[int],
    target_format: str,
    user_set_explicitly: bool,
) -> int:
    recommended = recommended_max_new_tokens(target_format)
    if user_set_explicitly:
        return explicit if explicit is not None else DEFAULT_MAX_NEW_TOKENS
    if recommended != DEFAULT_MAX_NEW_TOKENS:
        log(
            f"target_format={target_format}: using max_new_tokens={recommended} "
            f"(override with --max_new_tokens)"
        )
        return recommended
    return explicit if explicit is not None else DEFAULT_MAX_NEW_TOKENS


def _print_diagnostic_summary(
    entries: List[Dict[str, Any]],
    *,
    target_format: str,
    max_new_tokens: int,
    parse_mode: str,
    golds: List[str],
    preds: List[str],
) -> Dict[str, Any]:
    diag = summarize_parse_diagnostics(entries)
    n_gold_border = sum(1 for g in golds if g == "BORDER")
    n_pred_border = sum(1 for p in preds if p == "BORDER")
    warnings = build_eval_warnings(
        n_gold_border=n_gold_border,
        n_pred_border=n_pred_border,
        parse_failure_rate=diag["parse_failure_rate"],
        truncation_suspect_rate=diag["truncation_suspect_rate"],
        target_format=target_format,
    )
    log(
        f"Parse failures: {diag['parse_failure_count']}/{len(entries)} "
        f"({diag['parse_failure_rate']:.1%}), "
        f"truncation suspects: {diag['truncation_suspect_count']} "
        f"({diag['truncation_suspect_rate']:.1%}), "
        f"avg chars={diag['avg_output_chars']:.1f}, "
        f"n_pred_border={n_pred_border}, n_gold_border={n_gold_border}"
    )
    for warning in warnings:
        log(warning, level="warning")
    return {
        **diag,
        "n_gold_border": n_gold_border,
        "n_pred_border": n_pred_border,
        "warnings": warnings,
        "target_format": target_format,
        "max_new_tokens": max_new_tokens,
        "parse_mode": parse_mode,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--adapter", required=True, help="HF repo or local path of the LoRA adapter")
    parser.add_argument("--base_model", default=None,
                        help="Base model id (default: read adapter config)")
    parser.add_argument("--eval", type=Path, required=True, help="Path to fold eval.jsonl")
    parser.add_argument("--family", default="L", help="Prompt family used for parsing (default: L)")
    parser.add_argument("--parse_mode", choices=("tolerant", "strict"), default="tolerant",
                        help="Label parser: tolerant (JSON+regex) or strict family JSON (default: tolerant)")
    parser.add_argument("--target_format", choices=("auto", *TARGET_FORMATS), default="auto",
                        help="Training target format for token-budget hints (default: auto from meta.json)")
    parser.add_argument("--tolerances", type=int, nargs="+", default=[0, 1, 3])
    parser.add_argument("--postprocess", default="none",
                        help="Optional post-processing scenario before scoring")
    parser.add_argument("--confidence_threshold", type=float, default=0.85)
    parser.add_argument("--cluster_merge_radius", type=int, default=3)
    parser.add_argument("--max_new_tokens", type=int, default=None,
                        help=f"Generation budget (default: auto from target_format, else {DEFAULT_MAX_NEW_TOKENS})")
    parser.add_argument("--max_seq_len", type=int, default=1024)
    parser.add_argument("--batch_size", type=int, default=1,
                        help="Inference batch size (default 1; raise on larger GPUs)")
    parser.add_argument("--limit", type=int, default=0, help="Eval only first N rows (0 = all)")
    parser.add_argument("--spot_check", type=int, default=0,
                        help="Evaluate first N rows and print diagnostics (0 = off)")
    parser.add_argument("--spot_check_only", action="store_true",
                        help="Exit after spot_check without full eval")
    parser.add_argument("--allow_empty_gold", action="store_true",
                        help="Do not abort when eval set has zero BORDER labels")
    parser.add_argument("--resume", action="store_true",
                        help="Skip rows already in partial cache")
    parser.add_argument("--partial", type=Path, default=None,
                        help="Incremental eval cache JSONL (default: <out>.partial.jsonl)")
    parser.add_argument("--use_unsloth", action="store_true",
                        help="Load via Unsloth FastLanguageModel (faster inference)")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--upload_repo", default="",
                        help="Optional HF model repo to upload metrics JSON")
    args = parser.parse_args()

    import torch  # noqa: PLC0415

    meta = load_job_meta(args.eval)
    rows = read_eval_jsonl(args.eval)
    sanity = _dataset_sanity(rows, meta)
    log(
        f"Eval dataset: rows={sanity['n_rows']} "
        f"gold_BORDER={sanity['n_gold_border']} gold_NOBORDER={sanity['n_gold_noborder']}"
    )
    if meta:
        log(
            f"meta.json: target_format={meta.get('target_format', '?')} "
            f"eval_border={meta.get('eval_border', '?')}"
        )
    if sanity["n_gold_border"] == 0 and not args.allow_empty_gold:
        log(
            "Eval set has zero BORDER labels — metrics will be uninformative. "
            "Use --allow_empty_gold to proceed anyway.",
            level="error",
        )
        sys.exit(1)

    target_format = _resolve_target_format(args.target_format, meta)
    user_set_tokens = args.max_new_tokens is not None
    max_new_tokens = _resolve_max_new_tokens(args.max_new_tokens, target_format, user_set_tokens)

    if args.spot_check > 0:
        eval_rows = rows[: args.spot_check]
    elif args.limit > 0:
        eval_rows = rows[: args.limit]
    else:
        eval_rows = rows

    partial_path = args.partial
    if partial_path is None and args.out:
        partial_path = args.out.with_suffix(".partial.jsonl")
    elif partial_path is None:
        partial_path = _DEFAULT_PARTIAL

    cached: Dict[str, dict] = {}
    if args.resume and partial_path.exists():
        for line in partial_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                cached[row_key(row)] = row
        if cached:
            log(f"Resume: loaded {len(cached)} cached rows from {partial_path}")

    pending = [r for r in eval_rows if row_key(r) not in cached]

    if args.use_unsloth:
        from unsloth import FastLanguageModel  # noqa: PLC0415

        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=args.adapter, max_seq_length=args.max_seq_len, load_in_4bit=True, dtype=None
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
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"

    log(
        f"Evaluating {len(pending)} new rows ({len(cached)} cached, "
        f"batch_size={args.batch_size}, max_new_tokens={max_new_tokens}, "
        f"parse_mode={args.parse_mode})"
    )

    spot_check_done = False
    for start in progress(range(0, len(pending), args.batch_size), desc="eval"):
        batch = pending[start : start + args.batch_size]
        prompts = [
            tokenizer.apply_chat_template(
                [{"role": "user", "content": r["messages"][0]["content"]}],
                tokenize=False,
                add_generation_prompt=True,
            )
            for r in batch
        ]
        inputs = tokenizer(
            prompts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=args.max_seq_len,
        ).to(device)
        with torch.no_grad():
            gen = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=tokenizer.pad_token_id,
            )
        gen = gen[:, inputs["input_ids"].shape[1] :]
        texts = tokenizer.batch_decode(gen, skip_special_tokens=True)
        for row, text in zip(batch, texts):
            parsed = parse_eval_label(text, family=args.family, mode=args.parse_mode)
            gen_diag = diagnose_generation(text, max_new_tokens)
            idx = int(row.get("index", 0))
            gold = str(row["label"]).upper()
            entry = {
                "source": row.get("source", "doc"),
                "index": idx,
                "pred": parsed.label,
                "gold": gold,
                "confidence": parsed.confidence,
                "raw": text,
                "parse_ok": parsed.parse_ok,
                "parse_error": parsed.parse_error,
                "parse_method": parsed.parse_method,
                "output_chars": gen_diag["output_chars"],
                "truncation_suspect": gen_diag["truncation_suspect"],
            }
            cached[row_key(row)] = entry
            if partial_path:
                append_jsonl(partial_path, entry)

        if args.spot_check > 0 and not spot_check_done:
            spot_entries = [
                cached[row_key(r)] for r in eval_rows[: args.spot_check] if row_key(r) in cached
            ]
            if len(spot_entries) >= min(args.spot_check, len(eval_rows)):
                spot_golds = [e["gold"] for e in spot_entries]
                spot_preds = [e["pred"] for e in spot_entries]
                log(f"=== Spot-check diagnostics ({len(spot_entries)} rows) ===")
                _print_diagnostic_summary(
                    spot_entries,
                    target_format=target_format,
                    max_new_tokens=max_new_tokens,
                    parse_mode=args.parse_mode,
                    golds=spot_golds,
                    preds=spot_preds,
                )
                spot_check_done = True
                if args.spot_check_only:
                    log("spot_check_only set — exiting before full eval")
                    return

    indices = []
    preds = []
    golds = []
    confidences = []
    entry_list: List[Dict[str, Any]] = []
    for row in eval_rows:
        entry = cached.get(row_key(row))
        if not entry:
            continue
        indices.append(int(entry["index"]))
        preds.append(str(entry["pred"]))
        golds.append(str(entry["gold"]))
        confidences.append(entry.get("confidence"))
        entry_list.append(entry)

    if not indices:
        log("No rows evaluated.", level="warning")
        return

    size = max(indices) + 1
    full_gold = ["NOBORDER"] * size
    for idx, gold in zip(indices, golds):
        full_gold[idx] = gold

    final_preds = apply_scenario(
        preds,
        args.postprocess,
        confidences=confidences,
        confidence_threshold=args.confidence_threshold,
        cluster_merge_radius=args.cluster_merge_radius,
    )

    metrics = {
        f"tol_{t}": evaluate_sampled(indices, final_preds, full_gold, t)
        for t in args.tolerances
    }
    diag = _print_diagnostic_summary(
        entry_list,
        target_format=target_format,
        max_new_tokens=max_new_tokens,
        parse_mode=args.parse_mode,
        golds=golds,
        preds=final_preds,
    )
    report = {
        "adapter": args.adapter,
        "eval": str(args.eval),
        "family": args.family,
        "postprocess": args.postprocess,
        "n_eval": len(indices),
        "dataset_sanity": sanity,
        "metrics": metrics,
        **diag,
    }
    print(json.dumps(report, indent=2))
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        log(f"Wrote {args.out}")
    if args.upload_repo:
        token = __import__("os").environ.get("HF_TOKEN", "")
        upload_if_hub(args.out or Path("eval_report.json"), args.upload_repo, token)


if __name__ == "__main__":
    main()
