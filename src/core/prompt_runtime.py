"""Shared prompt runtime utilities for experiment runners."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

PROMPT_FAMILIES = tuple("ABCDEFGHIJ")


@dataclass
class ParseResult:
    label: Optional[str]
    is_valid: bool
    error: str
    payload: Any


def load_prompt_registry(prompts_dir: Path) -> Dict[str, Any]:
    registry_path = prompts_dir / "registry.json"
    with open(registry_path, encoding="utf-8") as f:
        return json.load(f)


def get_template_text(prompts_dir: Path, family: str, registry: Dict[str, Any]) -> str:
    for item in registry.get("templates", []):
        if item.get("id") == family:
            path = prompts_dir / item["file"]
            with open(path, encoding="utf-8") as f:
                return f.read()
    raise ValueError(f"Unknown prompt family: {family}")


def split_sample_context(sample_text: str) -> Dict[str, str]:
    match = re.search(r"<sentence>(.*?)</sentence>", sample_text, flags=re.DOTALL)
    if not match:
        return {"left_context": sample_text, "target_sentence": "", "right_context": ""}
    start, end = match.span()
    return {
        "left_context": sample_text[:start].strip(),
        "target_sentence": match.group(1).strip(),
        "right_context": sample_text[end:].strip(),
    }


def render_prompt_for_family(
    family: str,
    template_text: str,
    sample_text: str,
    few_shot_examples: str = "",
    chunk_sentences: str = "",
) -> str:
    ctx = split_sample_context(sample_text)
    values = {
        "left_context": ctx["left_context"],
        "target_sentence": ctx["target_sentence"],
        "right_context": ctx["right_context"],
        "few_shot_examples": few_shot_examples,
        "chunk_sentences": chunk_sentences,
    }
    rendered = template_text
    for key, value in values.items():
        rendered = rendered.replace("{" + key + "}", value)
    return rendered


def normalize_label(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip().upper()
    if text in {"BORDER", "TRUE", "YES"}:
        return "BORDER"
    if text in {"NOBORDER", "NO_BORDER", "FALSE", "NO"}:
        return "NOBORDER"
    return None


def _extract_label_token(text: str) -> Optional[str]:
    """Find BORDER/NOBORDER token in noisy outputs."""
    if not text:
        return None
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    # Prefer compact lines first (typical for label-only prompts).
    for candidate in lines[:5]:
        label = normalize_label(candidate)
        if label:
            return label
    upper = text.upper()
    # Check NOBORDER first to avoid BORDER substring collisions.
    if re.search(r"\bNOBORDER\b", upper):
        return "NOBORDER"
    if re.search(r"\bBORDER\b", upper):
        return "BORDER"
    lower = text.lower()
    if re.search(r"\b(?:does\s+not|doesn't)\s+(?:start|mark|introduce)\b", lower):
        return "NOBORDER"
    if re.search(r"\b(?:not\s+a\s+new\s+segment|no\s+new\s+segment)\b", lower):
        return "NOBORDER"
    if re.search(r"\b(?:starts?|marks?|introduces?)\s+(?:a\s+)?new\s+(?:event|scene|segment)\b", lower):
        return "BORDER"
    return None


def _extract_h_sentence_id_or_none(text: str) -> Optional[str]:
    """Extract sentence id or NONE token from noisy H outputs."""
    if not text:
        return None
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    candidates = lines[:4] + [text.strip()]
    for item in candidates:
        if item.upper() == "NONE":
            return "NONE"
        match_none = re.search(r"\bNONE\b", item, flags=re.IGNORECASE)
        if match_none:
            return "NONE"
        match_int = re.search(r"\b(\d+)\b", item)
        if match_int:
            return match_int.group(1)
    return None


def _extract_json_candidate(text: str) -> Optional[str]:
    s = text.strip()
    if not s:
        return None
    if s[0] in "{[":
        return s
    first_obj = s.find("{")
    first_arr = s.find("[")
    starts = [i for i in (first_obj, first_arr) if i >= 0]
    if not starts:
        return None
    start = min(starts)
    opening = s[start]
    closing = "}" if opening == "{" else "]"
    depth = 0
    for idx in range(start, len(s)):
        ch = s[idx]
        if ch == opening:
            depth += 1
        elif ch == closing:
            depth -= 1
            if depth == 0:
                return s[start:idx + 1]
    return None


def _parse_json(text: str) -> Any:
    candidate = _extract_json_candidate(text)
    if candidate is None:
        raise ValueError("no_json_found")
    return json.loads(candidate)


def parse_family_output(family: str, text: str) -> ParseResult:
    family = family.upper()
    if family == "A":
        label = _extract_label_token(text or "")
        if label:
            return ParseResult(label=label, is_valid=True, error="", payload=text)
        try:
            payload = _parse_json(text or "")
            if isinstance(payload, dict):
                label = normalize_label(payload.get("label"))
                if label:
                    return ParseResult(label=label, is_valid=True, error="", payload=payload)
        except Exception:  # noqa: BLE001
            pass
        return ParseResult(label=None, is_valid=False, error="invalid_label", payload=text)

    if family in {"B", "C", "D", "E", "F", "G", "J"}:
        try:
            payload = _parse_json(text)
        except Exception as exc:  # noqa: BLE001
            return ParseResult(label=None, is_valid=False, error=f"json_parse_error:{exc}", payload=None)
        if not isinstance(payload, dict):
            return ParseResult(label=None, is_valid=False, error="json_not_object", payload=payload)
        label = normalize_label(payload.get("label"))
        if not label:
            return ParseResult(label=None, is_valid=False, error="missing_or_invalid_label", payload=payload)
        return ParseResult(label=label, is_valid=True, error="", payload=payload)

    if family == "H":
        token = _extract_h_sentence_id_or_none(text or "")
        if token is None:
            return ParseResult(label=None, is_valid=False, error="invalid_sentence_id_or_none", payload=text)
        if token.upper() == "NONE":
            return ParseResult(label="NOBORDER", is_valid=True, error="", payload=token)
        return ParseResult(label=None, is_valid=True, error="", payload=token)

    if family == "I":
        try:
            payload = _parse_json(text)
        except Exception as exc:  # noqa: BLE001
            return ParseResult(label=None, is_valid=False, error=f"json_parse_error:{exc}", payload=None)
        if not isinstance(payload, list):
            return ParseResult(label=None, is_valid=False, error="json_not_array", payload=payload)
        return ParseResult(label=None, is_valid=True, error="", payload=payload)

    return ParseResult(label=None, is_valid=False, error=f"unsupported_family:{family}", payload=None)


def build_openrouter_model_kwargs(
    *,
    reasoning: str,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    top_k: Optional[int] = None,
    min_p: Optional[float] = None,
    seed: Optional[int] = None,
    max_tokens: Optional[int] = None,
    stop: Optional[list[str]] = None,
    response_format: str = "none",
    json_schema: Optional[dict[str, Any]] = None,
) -> Dict[str, Any]:
    kwargs: Dict[str, Any] = {}
    if temperature is not None:
        kwargs["temperature"] = temperature
    if top_p is not None:
        kwargs["top_p"] = top_p
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens
    if seed is not None:
        kwargs["seed"] = seed
    if stop:
        kwargs["stop"] = stop

    if response_format == "json_object":
        kwargs["response_format"] = {"type": "json_object"}
    elif response_format == "json_schema":
        kwargs["response_format"] = {
            "type": "json_schema",
            "json_schema": json_schema or {
                "name": "scene_boundary",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {"label": {"type": "string"}},
                    "required": ["label"],
                    "additionalProperties": True,
                },
            },
        }

    effort = {"on": "high", "off": "none", "low": "low"}.get(reasoning, "high")
    extra_body: Dict[str, Any] = {"reasoning": {"effort": effort}}
    if top_k is not None:
        extra_body["top_k"] = top_k
    if min_p is not None:
        extra_body["min_p"] = min_p
    kwargs["extra_body"] = extra_body
    return kwargs
