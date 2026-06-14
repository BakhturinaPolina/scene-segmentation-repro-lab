#!/usr/bin/env python3
"""Offline diagnostics for finetune eval JSONL and partial generation caches.

No GPU required. Inspect gold-label distribution, parse failures, and truncation
signals before or after running ``eval_finetuned.py``.

Example::

    python src/finetune/diagnose_eval.py \\
        --eval data/processed/finetune/fold_A/eval.jsonl \\
        --partial eval_report.partial.jsonl
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

from finetune.label_parse import (  # noqa: E402
    TARGET_FORMATS,
    build_eval_warnings,
    diagnose_generation,
    load_job_meta,
    parse_eval_label,
    recommended_max_new_tokens,
    summarize_parse_diagnostics,
)


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _eval_gold_stats(rows: List[Dict[str, Any]]) -> Dict[str, int]:
    n_border = sum(1 for r in rows if str(r.get("label", "")).upper() == "BORDER")
    n_noborder = sum(1 for r in rows if str(r.get("label", "")).upper() == "NOBORDER")
    return {
        "n_rows": len(rows),
        "n_gold_border": n_border,
        "n_gold_noborder": n_noborder,
    }


def _enrich_partial_entries(
    entries: List[Dict[str, Any]],
    *,
    max_new_tokens: int,
    family: str,
    parse_mode: str,
) -> List[Dict[str, Any]]:
    enriched: List[Dict[str, Any]] = []
    for entry in entries:
        raw = entry.get("raw", "")
        if "parse_ok" in entry:
            enriched.append(dict(entry))
            continue
        parsed = parse_eval_label(raw, family=family, mode=parse_mode)
        gen_diag = diagnose_generation(raw, max_new_tokens)
        enriched.append(
            {
                **entry,
                "pred": entry.get("pred", parsed.label),
                "parse_ok": parsed.parse_ok,
                "parse_error": parsed.parse_error,
                "parse_method": parsed.parse_method,
                "output_chars": gen_diag["output_chars"],
                "truncation_suspect": gen_diag["truncation_suspect"],
            }
        )
    return enriched


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--eval", type=Path, required=True, help="Path to eval.jsonl")
    parser.add_argument("--partial", type=Path, default=None,
                        help="Optional partial cache JSONL with raw generations")
    parser.add_argument("--family", default="L")
    parser.add_argument("--parse_mode", choices=("tolerant", "strict"), default="tolerant")
    parser.add_argument("--max_new_tokens", type=int, default=0,
                        help="Generation budget used (0 = infer from meta target_format)")
    parser.add_argument("--target_format", choices=("auto", *TARGET_FORMATS), default="auto")
    parser.add_argument("--max_fail_samples", type=int, default=5)
    args = parser.parse_args()

    meta = load_job_meta(args.eval)
    eval_rows = _read_jsonl(args.eval)
    gold_stats = _eval_gold_stats(eval_rows)

    target_format = args.target_format
    if target_format == "auto":
        target_format = str(meta.get("target_format", "cot_list"))
    max_new_tokens = args.max_new_tokens or recommended_max_new_tokens(target_format)

    report: Dict[str, Any] = {
        "eval": str(args.eval),
        "target_format": target_format,
        "recommended_max_new_tokens": recommended_max_new_tokens(target_format),
        "max_new_tokens_assumed": max_new_tokens,
        "parse_mode": args.parse_mode,
        "gold_stats": gold_stats,
        "meta": meta,
    }

    if args.partial and args.partial.exists():
        partial_rows = _enrich_partial_entries(
            _read_jsonl(args.partial),
            max_new_tokens=max_new_tokens,
            family=args.family,
            parse_mode=args.parse_mode,
        )
        diag = summarize_parse_diagnostics(partial_rows, max_samples=args.max_fail_samples)
        preds = [str(r.get("pred", "NOBORDER")) for r in partial_rows]
        golds = [str(r.get("gold", "NOBORDER")) for r in partial_rows]
        n_pred_border = sum(1 for p in preds if p == "BORDER")
        n_gold_border = sum(1 for g in golds if g == "BORDER")
        warnings = build_eval_warnings(
            n_gold_border=n_gold_border,
            n_pred_border=n_pred_border,
            parse_failure_rate=diag["parse_failure_rate"],
            truncation_suspect_rate=diag["truncation_suspect_rate"],
            target_format=target_format,
        )
        failures = [
            {
                "source": e.get("source", ""),
                "index": e.get("index", 0),
                "raw": (e.get("raw") or "")[:500],
                "parse_error": e.get("parse_error", ""),
                "truncation_suspect": e.get("truncation_suspect", False),
            }
            for e in partial_rows
            if not e.get("parse_ok", False)
        ][: args.max_fail_samples]
        report["partial"] = {
            "path": str(args.partial),
            "n_rows": len(partial_rows),
            "n_pred_border": n_pred_border,
            "n_gold_border": n_gold_border,
            **diag,
            "warnings": warnings,
            "sample_failures": failures,
        }
    else:
        report["partial"] = None
        report["suggestions"] = [
            f"Run eval with --max_new_tokens {recommended_max_new_tokens(target_format)}",
            "Use --parse_mode tolerant (default) for cot_list outputs",
            "Inspect partial cache: --partial <path>.partial.jsonl",
        ]

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
