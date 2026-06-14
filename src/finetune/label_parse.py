"""Shared label parsing and generation diagnostics for finetune eval."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

TARGET_FORMATS = ("cot_list", "json", "no_cot")
DEFAULT_MAX_NEW_TOKENS = 96
RECOMMENDED_MAX_NEW_TOKENS: Dict[str, int] = {
    "cot_list": 256,
    "no_cot": 128,
    "json": 96,
}


def recommended_max_new_tokens(target_format: str) -> int:
    return RECOMMENDED_MAX_NEW_TOKENS.get(target_format, DEFAULT_MAX_NEW_TOKENS)


def _extract_json_object(text: str) -> Optional[dict]:
    if not text:
        return None
    start = text.find("{")
    if start < 0:
        return None
    depth = 0
    for i in range(start, len(text)):
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                try:
                    obj = json.loads(text[start : i + 1])
                    return obj if isinstance(obj, dict) else None
                except Exception:  # noqa: BLE001
                    start = text.find("{", i + 1)
                    if start < 0:
                        return None
                    return _extract_json_object(text[start:])
    return None


def _label_from_json_object(obj: dict) -> Tuple[Optional[str], Optional[float]]:
    raw = str(obj.get("label", "")).strip().upper()
    label: Optional[str] = None
    if raw in {"BORDER", "TRUE", "YES"}:
        label = "BORDER"
    elif raw in {"NOBORDER", "NO_BORDER", "FALSE", "NO"}:
        label = "NOBORDER"
    conf: Optional[float] = None
    try:
        conf = float(obj["confidence"]) if obj.get("confidence") is not None else None
    except Exception:  # noqa: BLE001
        conf = None
    return label, conf


def parse_label_confidence(text: str) -> Tuple[str, Optional[float]]:
    """Tolerant parser: JSON object first, then regex BORDER/NOBORDER fallback."""
    obj = _extract_json_object(text or "")
    label: Optional[str] = None
    conf: Optional[float] = None
    if obj is not None:
        label, conf = _label_from_json_object(obj)
    if label is None:
        upper = (text or "").upper()
        if re.search(r"\bNOBORDER\b", upper):
            label = "NOBORDER"
        elif re.search(r"\bBORDER\b", upper):
            label = "BORDER"
        else:
            label = "NOBORDER"
    return label, conf


@dataclass
class EvalParseResult:
    label: str
    confidence: Optional[float]
    parse_ok: bool
    parse_error: str
    parse_method: str  # json | regex_fallback | default_noborder | strict


def parse_eval_label(
    text: str,
    *,
    family: str = "L",
    mode: str = "tolerant",
) -> EvalParseResult:
    """Parse a generation into BORDER/NOBORDER with diagnostic metadata."""
    if mode == "strict":
        from core.prompt_runtime import parse_family_output  # noqa: PLC0415

        parsed = parse_family_output(family, text or "")
        if parsed.is_valid and parsed.label:
            conf = None
            if isinstance(parsed.payload, dict):
                try:
                    raw = parsed.payload.get("confidence")
                    conf = float(raw) if raw is not None else None
                except Exception:  # noqa: BLE001
                    conf = None
            return EvalParseResult(
                label=parsed.label,
                confidence=conf,
                parse_ok=True,
                parse_error="",
                parse_method="strict",
            )
        return EvalParseResult(
            label="NOBORDER",
            confidence=None,
            parse_ok=False,
            parse_error=parsed.error or "strict_parse_failed",
            parse_method="default_noborder",
        )

    obj = _extract_json_object(text or "")
    if obj is not None:
        label, conf = _label_from_json_object(obj)
        if label is not None:
            return EvalParseResult(
                label=label,
                confidence=conf,
                parse_ok=True,
                parse_error="",
                parse_method="json",
            )

    upper = (text or "").upper()
    if re.search(r"\bNOBORDER\b", upper):
        return EvalParseResult(
            label="NOBORDER",
            confidence=None,
            parse_ok=True,
            parse_error="",
            parse_method="regex_fallback",
        )
    if re.search(r"\bBORDER\b", upper):
        return EvalParseResult(
            label="BORDER",
            confidence=None,
            parse_ok=True,
            parse_error="",
            parse_method="regex_fallback",
        )

    return EvalParseResult(
        label="NOBORDER",
        confidence=None,
        parse_ok=False,
        parse_error="no_json_or_label_token",
        parse_method="default_noborder",
    )


def _json_closed(text: str) -> bool:
    if "{" not in text:
        return False
    depth = 0
    for ch in text:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return True
    return False


def diagnose_generation(text: str, max_new_tokens: int) -> Dict[str, Any]:
    """Heuristic flags for truncated or malformed generations."""
    raw = text or ""
    has_json = "{" in raw
    closed = _json_closed(raw) if has_json else False
    truncation_suspect = False
    if has_json and not closed:
        truncation_suspect = True
    elif not has_json and raw.strip():
        # CoT-style output without reaching JSON is often truncation at low budgets.
        truncation_suspect = True
    return {
        "has_json": has_json,
        "json_closed": closed,
        "truncation_suspect": truncation_suspect,
        "output_chars": len(raw),
        "max_new_tokens": max_new_tokens,
    }


def summarize_parse_diagnostics(
    entries: Sequence[Dict[str, Any]],
    *,
    max_samples: int = 3,
) -> Dict[str, Any]:
    """Aggregate per-row parse metadata into report-level diagnostics."""
    n = len(entries)
    if n == 0:
        return {
            "parse_failure_count": 0,
            "parse_failure_rate": 0.0,
            "truncation_suspect_count": 0,
            "truncation_suspect_rate": 0.0,
            "avg_output_chars": 0.0,
            "sample_parse_failures": [],
        }

    parse_failures = [e for e in entries if not e.get("parse_ok", False)]
    trunc_suspects = [e for e in entries if e.get("truncation_suspect", False)]
    chars = [float(e.get("output_chars", 0) or 0) for e in entries]

    samples: List[Dict[str, Any]] = []
    for entry in parse_failures[:max_samples]:
        samples.append(
            {
                "source": entry.get("source", ""),
                "index": entry.get("index", 0),
                "raw": (entry.get("raw") or "")[:500],
                "parse_error": entry.get("parse_error", ""),
                "parse_method": entry.get("parse_method", ""),
            }
        )

    return {
        "parse_failure_count": len(parse_failures),
        "parse_failure_rate": round(len(parse_failures) / n, 4),
        "truncation_suspect_count": len(trunc_suspects),
        "truncation_suspect_rate": round(len(trunc_suspects) / n, 4),
        "avg_output_chars": round(sum(chars) / len(chars), 2),
        "sample_parse_failures": samples,
    }


def build_eval_warnings(
    *,
    n_gold_border: int,
    n_pred_border: int,
    parse_failure_rate: float,
    truncation_suspect_rate: float,
    target_format: str,
) -> List[str]:
    warnings: List[str] = []
    if n_gold_border > 0 and n_pred_border == 0:
        warnings.append(
            f"n_pred_border=0 but n_gold_border={n_gold_border} — check raw generations"
        )
    if parse_failure_rate > 0.5:
        warnings.append(
            f"parse_failure_rate={parse_failure_rate:.1%} — outputs may be truncated or malformed"
        )
    if target_format == "cot_list" and truncation_suspect_rate > 0.3:
        warnings.append(
            f"truncation_suspect_rate={truncation_suspect_rate:.1%} with cot_list — "
            "try --max_new_tokens 256"
        )
    return warnings


def load_job_meta(eval_path: Any) -> Dict[str, Any]:
    """Read sibling meta.json for an eval.jsonl path."""
    from pathlib import Path

    path = Path(eval_path)
    meta_path = path.parent / "meta.json"
    if not meta_path.exists():
        return {}
    return json.loads(meta_path.read_text(encoding="utf-8"))
