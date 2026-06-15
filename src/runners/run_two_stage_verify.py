#!/usr/bin/env python3
"""Stage-2 verifier for predicted scene borders (precision booster).

Stage 1 (already done): a prompting run produced a per-document cache with a
predicted label per sentence. This script is Stage 2: it re-queries a verifier
model ONLY on the sentences predicted as BORDER (optionally only the
low-confidence ones), asking "is this BORDER correct?" with the SAME surrounding
context window. Borders the verifier rejects are demoted to NOBORDER; the result
is then re-scored at tolerances 0/1/3.

Cost note
---------
Each Stage-2 call still includes the full surrounding context (so the per-call
input size is unchanged vs Stage 1). The savings come from the NUMBER of calls:
only predicted borders (a few percent of sentences) are re-queried, not every
sentence. ``--confidence_below`` shrinks that further. ``--dry_run`` reports the
call count and an estimated cost WITHOUT calling the API.

Examples
--------
    # Estimate cost only (no API calls):
    python src/runners/run_two_stage_verify.py \\
        --cache outputs/runs/prompting/2026-06-06/full_.../cache_Aus_guter_Familie.json \\
        --confidence_below 0.85 --dry_run

    # Run verification with a free reasoning model:
    OPENROUTER_API_KEY=... python src/runners/run_two_stage_verify.py \\
        --cache .../cache_Aus_guter_Familie.json \\
        --verifier_model "nvidia/nemotron-3-super-120b-a12b:free" \\
        --context_window 4 --tolerances 0 1 3 --out review/verify.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

_FILE = Path(__file__).resolve()
_SRC_ROOT = _FILE.parents[1]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from postprocess.postprocess import evaluate_sampled

VERIFY_SYSTEM = (
    "You are a strict verifier for German scene-segmentation. You are shown a "
    "candidate scene border (the marked sentence) with its surrounding context. "
    "A border is correct ONLY if a MAJOR narrative discontinuity (clear change in "
    "time and/or place and/or character constellation) begins exactly at the marked "
    "sentence. Reject minor transitions, continued dialogue, flashbacks, and plans."
)

VERIFY_TEMPLATE_YES_NO = """Context before:
{left}

Candidate border sentence (marked with ★):
★ {target} ★

Context after:
{right}

Is the single sentence marked with ★ the FIRST sentence of a NEW scene?
Answer with JSON only: {{"answer": "Yes" or "No"}}
"""

VERIFY_TEMPLATE = """Context before:
{left}

Candidate border sentence:
<sentence>{target}</sentence>

Context after:
{right}

Is the marked sentence a correct scene border? Return JSON only:
{{"keep": true or false, "confidence": 0.0 to 1.0}}
"""


def _parse_confidence(reason: Any) -> Optional[float]:
    if not isinstance(reason, str):
        return None
    try:
        payload = json.loads(reason)
    except Exception:  # noqa: BLE001
        return None
    if isinstance(payload, dict) and payload.get("confidence") is not None:
        try:
            return float(payload["confidence"])
        except Exception:  # noqa: BLE001
            return None
    return None


def load_cache(path: Path) -> Dict[str, List[Any]]:
    cache = json.loads(path.read_text(encoding="utf-8"))
    indices = sorted(int(k) for k in cache.keys())
    sentences, preds, golds, confs = [], [], [], []
    for i in indices:
        entry = cache[str(i)]
        sentences.append(str(entry.get("sentence", "")).strip())
        preds.append(str(entry.get("pred", "NOBORDER")).upper())
        golds.append(str(entry.get("gold", "NOBORDER")).upper())
        confs.append(_parse_confidence(entry.get("reason")))
    return {"indices": indices, "sentences": sentences, "preds": preds, "golds": golds, "confidences": confs}


def build_context(sentences: List[str], pos: int, window: int) -> Dict[str, str]:
    left = "\n".join(sentences[max(0, pos - window):pos])
    right = "\n".join(sentences[pos + 1: pos + 1 + window])
    return {"left": left, "target": sentences[pos], "right": right}


def parse_keep(text: str, *, verify_style: str = "keep_json") -> Optional[bool]:
    if verify_style == "yes_no":
        return parse_yes_no(text)
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        payload = json.loads(text[start:end])
    except Exception:  # noqa: BLE001
        low = text.lower()
        if "true" in low and "false" not in low:
            return True
        if "false" in low and "true" not in low:
            return False
        return None
    value = payload.get("keep")
    if isinstance(value, bool):
        return value
    return None


def parse_yes_no(text: str) -> Optional[bool]:
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        payload = json.loads(text[start:end])
        if isinstance(payload, dict):
            ans = str(payload.get("answer", "")).strip().lower()
            if ans in {"yes", "ja"}:
                return True
            if ans in {"no", "nein"}:
                return False
    except Exception:  # noqa: BLE001
        pass
    low = (text or "").strip().lower()
    if re.search(r"\byes\b", low) and not re.search(r"\bno\b", low):
        return True
    if re.search(r"\bno\b", low) and not re.search(r"\byes\b", low):
        return False
    return None


def estimate_cost(n_calls: int, context_window: int, price_in: float, price_out: float) -> Dict[str, float]:
    # Rough: ~ (2*window+1) sentences * ~25 tokens + ~120 prompt overhead in; ~30 out.
    in_tokens = n_calls * ((2 * context_window + 1) * 25 + 120)
    out_tokens = n_calls * 30
    cost = in_tokens / 1e6 * price_in + out_tokens / 1e6 * price_out
    return {"in_tokens": in_tokens, "out_tokens": out_tokens, "est_usd": round(cost, 4)}


def verify_one_cache(
    cache_path: Path,
    *,
    verifier_model: str,
    context_window: int,
    confidence_below: Optional[float],
    tolerances: List[int],
    temperature: float,
    max_tokens: int,
    request_delay: float,
    price_in: float,
    price_out: float,
    dry_run: bool,
    verify_style: str,
    client: Any = None,
) -> Dict[str, Any]:
    data = load_cache(cache_path)
    indices = data["indices"]
    sentences = data["sentences"]
    preds = data["preds"]
    golds = data["golds"]
    confs = data["confidences"]

    pos_by_index = {idx: p for p, idx in enumerate(indices)}
    to_verify: List[int] = []
    for p, (idx, label) in enumerate(zip(indices, preds)):
        if label != "BORDER":
            continue
        if confidence_below is not None:
            c = confs[p]
            if c is not None and c >= confidence_below:
                continue
        to_verify.append(idx)

    size = max(indices) + 1
    full_gold = ["NOBORDER"] * size
    for idx, gold in zip(indices, golds):
        full_gold[idx] = gold

    cost = estimate_cost(len(to_verify), context_window, price_in, price_out)
    n_pred = sum(1 for p in preds if p == "BORDER")
    print(f"[{cache_path.name}] pred borders={n_pred} verify={len(to_verify)} est=${cost['est_usd']}")

    before = {f"tol_{t}": evaluate_sampled(indices, preds, full_gold, t) for t in tolerances}
    template = VERIFY_TEMPLATE_YES_NO if verify_style == "yes_no" else VERIFY_TEMPLATE

    report: Dict[str, Any] = {
        "cache": str(cache_path),
        "verifier_model": verifier_model,
        "context_window": context_window,
        "verify_style": verify_style,
        "confidence_below": confidence_below,
        "n_pred_border": n_pred,
        "n_verified": len(to_verify),
        "cost_estimate": cost,
        "metrics_before": before,
        "decisions": [],
    }

    if dry_run:
        return report

    if client is None:
        raise RuntimeError("client required for non-dry-run verification")

    verified_preds = list(preds)
    rejected = 0
    for n, idx in enumerate(to_verify, start=1):
        pos = pos_by_index[idx]
        ctx = build_context(sentences, pos, context_window)
        user = template.format(**ctx)
        resp = client.chat.completions.create(
            model=verifier_model,
            messages=[{"role": "system", "content": VERIFY_SYSTEM},
                      {"role": "user", "content": user}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        text = resp.choices[0].message.content or ""
        keep = parse_keep(text, verify_style=verify_style)
        decision = {"index": idx, "keep": keep, "raw": text[:200]}
        if keep is False:
            verified_preds[pos] = "NOBORDER"
            rejected += 1
        report["decisions"].append(decision)
        if n % 25 == 0:
            print(f"  verified {n}/{len(to_verify)} (rejected: {rejected})")
        if request_delay:
            time.sleep(request_delay)

    after = {f"tol_{t}": evaluate_sampled(indices, verified_preds, full_gold, t) for t in tolerances}
    report["n_rejected"] = rejected
    report["metrics_after"] = after
    print(f"  rejected {rejected}/{len(to_verify)}")
    for t in tolerances:
        b, a = before[f"tol_{t}"], after[f"tol_{t}"]
        print(f"  tol{t}: F1 {b['f1']:.3f}->{a['f1']:.3f} P {b['precision']:.3f}->{a['precision']:.3f}")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--cache", type=Path, help="Stage-1 per-document cache JSON")
    src.add_argument(
        "--run_dir",
        type=Path,
        help="Stage-1 output dir; verify all cache_*.json (Excel batch mode)",
    )
    parser.add_argument("--verifier_model", default="nvidia/nemotron-3-super-120b-a12b:free")
    parser.add_argument("--context_window", type=int, default=4, help="Sentences each side (default: 4)")
    parser.add_argument("--confidence_below", type=float, default=None,
                        help="Only verify predicted borders with confidence below this value")
    parser.add_argument(
        "--verify_style",
        choices=["keep_json", "yes_no"],
        default="keep_json",
        help="Verifier prompt style (yes_no = Stage-6 OFAT template)",
    )
    parser.add_argument("--tolerances", type=int, nargs="+", default=[0, 1, 3])
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max_tokens", type=int, default=64)
    parser.add_argument("--request_delay", type=float, default=0.0)
    parser.add_argument("--price_in", type=float, default=0.0, help="USD per 1M input tokens")
    parser.add_argument("--price_out", type=float, default=0.0, help="USD per 1M output tokens")
    parser.add_argument("--dry_run", action="store_true", help="Report call count + cost; no API calls")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    cache_paths: List[Path] = []
    if args.cache:
        cache_paths = [args.cache]
    else:
        cache_paths = sorted(args.run_dir.glob("cache_*.json"))
        if not cache_paths:
            print(f"No cache_*.json under {args.run_dir}")
            sys.exit(1)

    client = None
    if not args.dry_run:
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            print("ERROR: set OPENROUTER_API_KEY for a non-dry-run verification.")
            sys.exit(1)
        from openai import OpenAI  # noqa: PLC0415
        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

    batch_report: Dict[str, Any] = {"documents": {}}
    for cache_path in cache_paths:
        report = verify_one_cache(
            cache_path,
            verifier_model=args.verifier_model,
            context_window=args.context_window,
            confidence_below=args.confidence_below,
            tolerances=args.tolerances,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            request_delay=args.request_delay,
            price_in=args.price_in,
            price_out=args.price_out,
            dry_run=args.dry_run,
            verify_style=args.verify_style,
            client=client,
        )
        batch_report["documents"][cache_path.stem] = report

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(batch_report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
