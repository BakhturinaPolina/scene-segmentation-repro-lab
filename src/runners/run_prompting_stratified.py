"""Stratified prompting evaluation on full corpus.

Classifies a stratified sample (all BORDERs + matched NOBORDERs) from each
novel in data/full/stss_test_2 using Nemotron via OpenRouter free tier,
then computes precision/recall/F1 at tolerance 0, 1, and 3.

Supports resume: intermediate results are cached per-document so the run can
be interrupted and restarted without losing progress.

Run from project root:
    OPENROUTER_API_KEY=sk-or-... python src/runners/run_prompting_stratified.py

Options:
    --max_per_class N   Max BORDER (and NOBORDER) sentences per novel (0 = all)
    --dry_run N         Classify only N sentences total then stop (for testing)
    --date YYYY-MM-DD   Override the output date folder (default: today)
    --prompt {no-cot,cot-list}  Prompt style (default: no-cot)
    --reasoning {on,off}        Model-level thinking (default: on)
"""
import argparse
import csv
import json
import os
import random
import re
import sys
import time
from datetime import date, datetime
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

_FILE = Path(__file__).resolve()
_SRC_ROOT = _FILE.parents[1]
_ROOT_DIR = _SRC_ROOT.parent
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))
sys.path.insert(0, str(_ROOT_DIR / "upstream" / "scene-segmentation"))

from wuenlp.impl.UIMANLPStructs import UIMADocument, UIMAScene, UIMASentence
from prompting.classify import (
    build_sentence_sample, get_chain, Model, prompt_classify, prompt_classify_cot,
)
from utils.constants import Label
from core.prompt_runtime import (
    PROMPT_FAMILIES,
    build_openrouter_model_kwargs,
    get_template_text,
    load_prompt_registry,
    parse_family_output,
    render_prompt_for_family,
)
from core.workflow_runtime import project_root, prompting_run_root, prompts_dir, stss_test2_data_dir, write_repro_files

DEFAULT_MODEL = Model("nvidia/nemotron-3-super-120b-a12b:free", int(512 * 0.8), json=False, openai=False, openrouter=True)

ROOT_DIR = project_root(Path(__file__))
DATA_DIR = stss_test2_data_dir(ROOT_DIR)
SEED = 1337


@dataclass
class SyntheticSentence:
    text: str
    previous: "SyntheticSentence | None" = None
    next: "SyntheticSentence | None" = None


@dataclass
class SyntheticDoc:
    path: Path
    sentences: list[SyntheticSentence]


def log(msg):
    """Timestamped, unbuffered terminal logging."""
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def _debug_log(run_id: str, hypothesis_id: str, location: str, message: str, data: dict[str, Any]) -> None:
    payload = {
        "sessionId": DEBUG_SESSION_ID,
        "runId": run_id,
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
        "timestamp": int(time.time() * 1000),
    }
    try:
        DEBUG_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=True, default=str) + "\n")
    except Exception as e:
        log(f"[debug-log-write-failed] {type(e).__name__}: {str(e)[:160]}")


def progress_bar(done: int, total: int, width: int = 20) -> str:
    total = max(1, total)
    done = max(0, min(done, total))
    filled = int((done / total) * width)
    return "[" + ("#" * filled) + ("-" * (width - filled)) + f"] {done}/{total}"


_ANSWER_YES_RE = re.compile(r"\bAnswer\s*:\s*Yes\b", re.IGNORECASE)
_ANSWER_NO_RE = re.compile(r"\bAnswer\s*:\s*No\b", re.IGNORECASE)
_ANSWER_BORDER_RE = re.compile(r"\b(?:Answer|Final\s*Answer)\s*:\s*BORDER\b", re.IGNORECASE)
_ANSWER_NOBORDER_RE = re.compile(r"\b(?:Answer|Final\s*Answer)\s*:\s*NOBORDER\b", re.IGNORECASE)
_FINAL_BORDER_RE = re.compile(r"\b(?:BORDER|Yes|True)\b", re.IGNORECASE)
_FINAL_NOBORDER_RE = re.compile(r"\b(?:NOBORDER|No|False)\b", re.IGNORECASE)
_NOT_START_RE = re.compile(
    r"\b(?:does\s+(?:\*{0,2})not(?:\*{0,2})|doesn't)\s+"
    r"(?:start|introduce|mark\b)", re.IGNORECASE)
_STARTS_RE = re.compile(
    r"\b(?:starts?|introduces?|marks?)\s+(?:a\s+new\s+scene|the\s+beginning)",
    re.IGNORECASE)
_STRICT_SUFFIX = (
    "\n\nReturn your final decision as exactly one token on the last line: "
    "BORDER or NOBORDER."
)

DEFAULT_MAX_PARSE_RETRIES = 15
DEFAULT_MAX_RATE_LIMIT_RETRIES = 40
DEFAULT_MAX_CONSECUTIVE_RATE_LIMITS = 8
DEFAULT_RATE_LIMIT_BURST_THRESHOLD = 5
DEFAULT_RATE_LIMIT_COOLDOWN_SEC = 180
DEBUG_LOG_PATH = Path("/home/polina/Documents/Cursor_Projects/scene-segmentation-research/.cursor/debug-a7f45b.log")
DEBUG_SESSION_ID = "a7f45b"
AGENT_DEBUG_LOG_PATH = Path("/home/polina/Documents/Cursor_Projects/scene-segmentation-research/.cursor/debug-d978b4.log")
AGENT_DEBUG_SESSION_ID = "d978b4"

_RETRY_AFTER_JSON_RE = re.compile(
    r'"retry_after_seconds(?:_raw)?"\s*:\s*([\d.]+)', re.IGNORECASE)
_RETRY_AFTER_HEADER_RE = re.compile(r"Retry-After['\"]?\s*[:=]\s*['\"]?(\d+)", re.IGNORECASE)


def _is_rate_limit_error(err_str: str) -> bool:
    lo = err_str.lower()
    return (
        "429" in err_str
        or "rate limit" in lo
        or "rate-limit" in lo
        or "rate limited" in lo
    )


def _parse_retry_after_seconds(err_str: str, rate_limit_attempt: int) -> float:
    """Extract provider-suggested wait from OpenRouter/LangChain error text."""
    for pattern in (_RETRY_AFTER_JSON_RE, _RETRY_AFTER_HEADER_RE):
        match = pattern.search(err_str)
        if match:
            try:
                return max(1.0, float(match.group(1)))
            except ValueError:
                pass
    return float(min(60, 5 * (2 ** min(rate_limit_attempt, 6))))


def _agent_debug_log(
    run_id: str,
    hypothesis_id: str,
    location: str,
    message: str,
    data: dict[str, Any],
) -> None:
    payload = {
        "sessionId": AGENT_DEBUG_SESSION_ID,
        "runId": run_id,
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
        "timestamp": int(time.time() * 1000),
    }
    try:
        AGENT_DEBUG_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(AGENT_DEBUG_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=True, default=str) + "\n")
    except Exception:
        pass


def _compact_decision(reason: str) -> str:
    """Extract a short, human-readable decision summary."""
    if not reason:
        return ""
    lines = [line.strip() for line in reason.splitlines() if line.strip()]
    if not lines:
        return ""
    return lines[0][:240]


def _review_schema() -> dict[str, Any]:
    return {
        "sentence_index": "int (0-based sentence index in original document)",
        "sentence_text_full": "str (full sentence text, not truncated)",
        "prediction_label": "str (BORDER|NOBORDER)",
        "prediction_bool": "bool",
        "ground_truth_label": "str",
        "parse_ok": "bool",
        "parse_error": "str",
        "compact_decision": "str (short parsed/normalized rationale)",
        "raw_model_response": "str (full raw model output)",
        "latency_seconds": "float",
        "output_chars": "float",
        "input_mode": "str (xmi)",
        "prompt_mode": "str",
        "prompt_family": "str|null",
        "model": "str",
        "source_file": "str",
    }


def parse_response(text, prompt_mode):
    """Return (scene_change: bool|None, reason: str) from model output."""
    stripped = text.strip()
    first_line = stripped.split("\n")[0] if stripped else ""
    line_norm = re.sub(r"[^\w]+", "", first_line).lower()

    # High-confidence explicit formats.
    if line_norm in {"border", "yes", "true"}:
        return True, text
    if line_norm in {"noborder", "no", "false"}:
        return False, text
    if _ANSWER_BORDER_RE.search(text):
        return True, text
    if _ANSWER_NOBORDER_RE.search(text):
        return False, text

    if prompt_mode == "cot-list":
        if _ANSWER_NO_RE.search(text):
            return False, text
        if _ANSWER_YES_RE.search(text):
            return True, text
        if _NOT_START_RE.search(text):
            return False, text
        if _STARTS_RE.search(text):
            return True, text
    if "True" in first_line:
        return True, text
    if "False" in first_line:
        return False, text
    if first_line.strip().startswith("Yes"):
        return True, text
    if first_line.strip().startswith("No"):
        return False, text
    return None, text


def parse_response_loose(text: str) -> bool | None:
    """Fallback parser for verbose outputs when strict parsing fails."""
    stripped = text.strip()
    if not stripped:
        return None
    lines = [ln.strip() for ln in stripped.splitlines() if ln.strip()]
    candidates = []
    if lines:
        candidates.append(lines[-1])
    candidates.append(stripped)
    for chunk in candidates:
        if _ANSWER_BORDER_RE.search(chunk):
            return True
        if _ANSWER_NOBORDER_RE.search(chunk):
            return False
        if _FINAL_BORDER_RE.fullmatch(chunk):
            return True
        if _FINAL_NOBORDER_RE.fullmatch(chunk):
            return False
        if _NOT_START_RE.search(chunk):
            return False
        if _STARTS_RE.search(chunk):
            return True
    return None


# ---------------------------------------------------------------------------
# Gold label helper (avoids importing ssc.dataset which pulls in Unsloth)
# ---------------------------------------------------------------------------

def get_label_simple(sentence, coarse=True):
    covering_scenes = sentence.covering(UIMAScene)
    if not covering_scenes:
        return Label.NOBORDER
    current_scene = covering_scenes[0]
    covered_sentences = current_scene.covered(UIMASentence)
    if covered_sentences and covered_sentences[0] == sentence:
        if coarse:
            return Label.BORDER
    return Label.NOBORDER


# ---------------------------------------------------------------------------
# Stratified sampling
# ---------------------------------------------------------------------------

def build_stratified_sample(doc, seed, max_per_class=0):
    """Return sorted list of (original_index, sentence, gold_label_str).

    Includes all BORDER sentences and an equal number of evenly-spaced
    NOBORDER sentences.  If max_per_class > 0, cap each class.
    """
    rng = random.Random(seed)
    borders, noborders = [], []

    for i, sent in enumerate(doc.sentences):
        lab = get_label_simple(sent, coarse=True)
        if lab == Label.BORDER:
            borders.append((i, sent, "BORDER"))
        else:
            noborders.append((i, sent, "NOBORDER"))

    if max_per_class > 0 and len(borders) > max_per_class:
        borders = sorted(rng.sample(borders, max_per_class), key=lambda x: x[0])

    n_need = len(borders)
    if max_per_class > 0:
        n_need = min(n_need, max_per_class)

    # Evenly-spaced NOBORDER selection for positional coverage
    if len(noborders) <= n_need:
        selected_nb = noborders
    else:
        step = len(noborders) / n_need
        selected_nb = [noborders[int(i * step)] for i in range(n_need)]

    sample = sorted(borders + selected_nb, key=lambda x: x[0])
    return sample


def build_full_sample(doc):
    """Return all sentences with gold labels (full-eval mode)."""
    sample = []
    for i, sent in enumerate(doc.sentences):
        lab = get_label_simple(sent, coarse=True)
        sample.append((i, sent, "BORDER" if lab == Label.BORDER else "NOBORDER"))
    return sample


def _normalize_gold_label(value: str) -> str:
    token = value.strip().upper()
    return "BORDER" if token == "BORDER" else "NOBORDER"


def build_stratified_sample_from_labels(
    sentences: list[SyntheticSentence],
    labels: list[str],
    seed: int,
    max_per_class: int = 0,
):
    rng = random.Random(seed)
    borders: list[tuple[int, SyntheticSentence, str]] = []
    noborders: list[tuple[int, SyntheticSentence, str]] = []
    for i, (sent, label) in enumerate(zip(sentences, labels)):
        triplet = (i, sent, label)
        if label == "BORDER":
            borders.append(triplet)
        else:
            noborders.append(triplet)

    if max_per_class > 0 and len(borders) > max_per_class:
        borders = sorted(rng.sample(borders, max_per_class), key=lambda x: x[0])

    n_need = len(borders)
    if max_per_class > 0:
        n_need = min(n_need, max_per_class)

    if len(noborders) <= n_need:
        selected_nb = noborders
    else:
        step = len(noborders) / n_need
        selected_nb = [noborders[int(i * step)] for i in range(n_need)]

    return sorted(borders + selected_nb, key=lambda x: x[0])


def build_full_sample_from_labels(
    sentences: list[SyntheticSentence],
    labels: list[str],
):
    return [(i, sent, label) for i, (sent, label) in enumerate(zip(sentences, labels))]


def _resolve_excel_txt_path(name: str) -> Path:
    candidate = ROOT_DIR / "data" / name
    if candidate.exists():
        return candidate
    fallback = ROOT_DIR / name
    if fallback.exists():
        return fallback
    raise FileNotFoundError(f"TXT from manifest not found: {name}")


def _gold_path_for_txt(txt_path: Path) -> Path:
    if txt_path.name.endswith("__for_prompting.txt"):
        return txt_path.with_name(txt_path.name.replace("__for_prompting.txt", "__gold_labels.csv"))
    return txt_path.with_suffix(".gold.csv")


def load_excel_manifest_docs(manifest_path: Path) -> list[dict[str, Any]]:
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = payload.get("files", [])
    docs: list[dict[str, Any]] = []
    for item in files:
        name = item.get("name")
        if not isinstance(name, str) or not name:
            continue
        txt_path = _resolve_excel_txt_path(name)
        gold_path = _gold_path_for_txt(txt_path)
        if not gold_path.exists():
            raise FileNotFoundError(f"Gold CSV missing for TXT input: {gold_path}")

        rows: list[dict[str, str]] = []
        scene_ids: list[str] = []
        with gold_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                text = str(row.get("sentence_text_full", "")).strip()
                if not text:
                    continue
                rows.append(row)
                scene_ids.append(str(row.get("scene_id_raw", "")).strip())
        if not rows:
            raise ValueError(f"No usable rows in gold CSV: {gold_path}")

        sentences = [SyntheticSentence(text=str(r["sentence_text_full"]).strip()) for r in rows]
        for i in range(len(sentences)):
            if i > 0:
                sentences[i].previous = sentences[i - 1]
            if i + 1 < len(sentences):
                sentences[i].next = sentences[i + 1]

        full_gold = [_normalize_gold_label(str(r.get("ground_truth_label", ""))) for r in rows]
        stem = txt_path.stem.replace("__for_prompting", "")
        # #region agent log
        _agent_debug_log(
            run_id=f"manifest_load_{stem}",
            hypothesis_id="H2_H3",
            location="run_prompting_stratified.py:load_excel_manifest_docs",
            message="excel_manifest_doc_profile",
            data={
                "stem": stem,
                "rows_used": len(rows),
                "gold_borders": sum(1 for g in full_gold if g == "BORDER"),
                "unique_scene_ids": len({sid for sid in scene_ids if sid}),
                "avg_sentence_chars": round(
                    sum(len(s.text) for s in sentences) / len(sentences), 2
                ) if sentences else 0.0,
            },
        )
        # #endregion
        docs.append(
            {
                "stem": stem,
                "source_file": txt_path.name,
                "doc": SyntheticDoc(path=txt_path, sentences=sentences),
                "sentences": sentences,
                "full_gold": full_gold,
                "input_mode": "excel_manifest",
            }
        )
    if not docs:
        raise ValueError(f"No files found in excel manifest: {manifest_path}")
    return docs


def build_chunk_sentences(sentences, center_idx, chunk_window):
    start = max(0, center_idx - chunk_window)
    end = min(len(sentences), center_idx + chunk_window + 1)
    lines = []
    for idx in range(start, end):
        local_id = idx - start + 1
        sent_text = sentences[idx].text.replace("\n", " ").strip()
        lines.append(f"{local_id}. {sent_text}")
    target_local_id = center_idx - start + 1
    return "\n".join(lines), target_local_id


def infer_chunk_family_label(family, parsed_payload, target_local_id, score_threshold):
    if family == "H":
        token = str(parsed_payload).strip()
        if token.upper() == "NONE":
            return False, ""
        try:
            pred_local_id = int(token)
        except ValueError:
            return None, "invalid_sentence_id"
        return pred_local_id == target_local_id, ""

    if family == "I":
        if not isinstance(parsed_payload, list):
            return None, "scores_not_array"
        target_score = None
        for item in parsed_payload:
            if not isinstance(item, dict):
                continue
            sid = item.get("sentence_id")
            if sid is None:
                continue
            try:
                sid_int = int(sid)
            except (TypeError, ValueError):
                continue
            if sid_int == target_local_id:
                try:
                    target_score = float(item.get("score"))
                except (TypeError, ValueError):
                    return None, "invalid_target_score"
                break
        if target_score is None:
            return None, "missing_target_score"
        return target_score >= score_threshold, ""

    return None, "unsupported_chunk_family"


# ---------------------------------------------------------------------------
# Evaluation (mirrors upstream ssc/evaluation.py but works on sparse samples)
# ---------------------------------------------------------------------------

def evaluate_sampled(sampled_indices, sampled_preds, full_gold_labels, tolerance):
    """Compute P/R/F1 on sampled positions with tolerance over original indices.

    sampled_indices:  list[int]  -- original sentence indices that were sampled
    sampled_preds:    list[str]  -- "BORDER" or "NOBORDER" for each sampled pos
    full_gold_labels: list[str]  -- gold label for every sentence in the document
    """
    pred_by_idx = dict(zip(sampled_indices, sampled_preds))
    sampled_set = set(sampled_indices)

    tp = fp = fn = 0

    # Recall side: for each sampled gold BORDER, is there a predicted BORDER nearby?
    for idx in sampled_indices:
        if full_gold_labels[idx] != "BORDER":
            continue
        window = range(max(0, idx - tolerance), min(len(full_gold_labels), idx + tolerance + 1))
        found = any(pred_by_idx.get(j) == "BORDER" for j in window if j in sampled_set)
        if found:
            tp += 1
        else:
            fn += 1

    # Precision side: for each sampled predicted BORDER, is there a gold BORDER nearby?
    for idx in sampled_indices:
        if pred_by_idx[idx] != "BORDER":
            continue
        window = range(max(0, idx - tolerance), min(len(full_gold_labels), idx + tolerance + 1))
        if not any(full_gold_labels[j] == "BORDER" for j in window):
            fp += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return {"tp": tp, "fp": fp, "fn": fn,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4)}


# ---------------------------------------------------------------------------
# Classification loop
# ---------------------------------------------------------------------------

def classify_sample(
    sample,
    doc,
    chain,
    model,
    cache_path,
    dry_run=0,
    prompt_mode="no-cot",
    prompt_family: Optional[str] = None,
    template_text: str = "",
    few_shot_examples: str = "",
    chunk_window: int = 2,
    score_threshold: float = 50.0,
    request_delay: float = 0.0,
    max_parse_retries: int = DEFAULT_MAX_PARSE_RETRIES,
    max_rate_limit_retries: int = DEFAULT_MAX_RATE_LIMIT_RETRIES,
    max_consecutive_rate_limits: int = DEFAULT_MAX_CONSECUTIVE_RATE_LIMITS,
    rate_limit_burst_threshold: int = DEFAULT_RATE_LIMIT_BURST_THRESHOLD,
    rate_limit_cooldown: float = DEFAULT_RATE_LIMIT_COOLDOWN_SEC,
):
    """Classify each sentence in the stratified sample. Resumes from cache."""
    if cache_path.exists():
        with open(cache_path, encoding="utf-8") as f:
            cache = json.load(f)
        log(f"Loaded cache: {cache_path} ({len(cache)} entries)")
    else:
        cache = {}
        log(f"No cache found, starting fresh: {cache_path}")

    total = len(sample)
    if dry_run > 0:
        total = min(total, dry_run)
    log(f"Classifying up to {total} sampled sentences")
    all_sentences = list(doc.sentences)
    last_success_ts: float | None = None
    debug_run_id = f"classify_{int(time.time())}"
    # #region agent log
    _debug_log(
        run_id=debug_run_id,
        hypothesis_id="H0",
        location="run_prompting_stratified.py:classify_sample:start",
        message="classification_loop_start",
        data={
            "sample_total": len(sample),
            "effective_total": total,
            "request_delay": request_delay,
            "max_rate_limit_retries": max_rate_limit_retries,
            "max_consecutive_rate_limits": max_consecutive_rate_limits,
            "burst_threshold": rate_limit_burst_threshold,
            "rate_limit_cooldown": rate_limit_cooldown,
            "prompt_mode": prompt_mode,
            "prompt_family": prompt_family,
            "model": model.name if hasattr(model, "name") else str(model),
        },
    )
    # #endregion

    for count, (orig_idx, sentence, gold) in enumerate(sample):
        if count >= total:
            break
        key = str(orig_idx)
        if key in cache:
            log(f"{progress_bar(count + 1, total)} idx={orig_idx} already cached, skipping")
            continue

        sent_preview = sentence.text[:80].replace("\n", " ")
        log(f"{progress_bar(count + 1, total)} idx={orig_idx} start (gold={gold}) :: {sent_preview}")
        if prompt_family in {"H", "I"}:
            chunk_sentences, target_local_id = build_chunk_sentences(
                all_sentences, orig_idx, chunk_window
            )
            text_sample = render_prompt_for_family(
                prompt_family,
                template_text,
                "",
                few_shot_examples=few_shot_examples,
                chunk_sentences=chunk_sentences,
            )
        else:
            target_local_id = None
            base_sample = build_sentence_sample(sentence, model)
            if prompt_family:
                text_sample = render_prompt_for_family(
                    prompt_family,
                    template_text,
                    base_sample,
                    few_shot_examples=few_shot_examples,
                )
            else:
                text_sample = base_sample
        # #region agent log
        if count < 2:
            _agent_debug_log(
                run_id=debug_run_id,
                hypothesis_id="H3_H4",
                location="run_prompting_stratified.py:classify_sample",
                message="sample_context_profile",
                data={
                    "idx": orig_idx,
                    "gold": gold,
                    "sentence_chars": len(sentence.text),
                    "sample_chars": len(text_sample),
                    "prompt_family": prompt_family,
                },
            )
        # #endregion
        scene_change = None
        reason = ""
        parse_ok = False
        parse_error = ""
        output_chars = 0
        parse_retries = 0
        rate_limit_retries = 0
        consecutive_rate_limits = 0
        rate_limit_streak = 0
        rate_limit_exhausted = False
        sent_t0 = time.time()

        while scene_change is None and parse_retries < max_parse_retries:
            active_sample = text_sample
            if parse_retries >= 2 and prompt_family in {None, "A"}:
                active_sample = text_sample + _STRICT_SUFFIX
            if request_delay > 0:
                time.sleep(request_delay)
            # #region agent log
            _debug_log(
                run_id=debug_run_id,
                hypothesis_id="H1_H5",
                location="run_prompting_stratified.py:classify_sample:before_chain_call",
                message="request_attempt",
                data={
                    "idx": orig_idx,
                    "count": count + 1,
                    "parse_retries": parse_retries,
                    "rate_limit_retries": rate_limit_retries,
                    "consecutive_rate_limits": consecutive_rate_limits,
                    "active_sample_chars": len(active_sample),
                    "seconds_since_last_success": (
                        None if last_success_ts is None else round(time.time() - last_success_ts, 3)
                    ),
                },
            )
            # #endregion
            try:
                response = chain(active_sample)
            except Exception as e:
                err_str = str(e)
                if _is_rate_limit_error(err_str):
                    rate_limit_retries += 1
                    consecutive_rate_limits += 1
                    rate_limit_streak += 1
                    parsed_retry_after = _parse_retry_after_seconds(err_str, rate_limit_retries)
                    # #region agent log
                    log(
                        f"  [rate limit debug] idx={orig_idx} retry={rate_limit_retries} "
                        f"cons={consecutive_rate_limits} parsed_retry_after={parsed_retry_after:.1f}s "
                        f"err={err_str[:260].replace(chr(10), ' ')}"
                    )
                    # #endregion
                    if rate_limit_streak >= max_consecutive_rate_limits:
                        log(f"  [rate limit] idx={orig_idx} consecutive limit reached "
                            f"({rate_limit_streak}/{max_consecutive_rate_limits}), skipping sentence")
                        parse_error = "rate_limit_exhausted"
                        reason = "RATE_LIMIT_EXHAUSTED"
                        rate_limit_exhausted = True
                        break
                    if rate_limit_retries > max_rate_limit_retries:
                        log(f"  [rate limit] idx={orig_idx} exceeded max "
                            f"({max_rate_limit_retries}), giving up")
                        break
                    if consecutive_rate_limits >= rate_limit_burst_threshold:
                        wait = rate_limit_cooldown
                        log(f"  [rate limit] idx={orig_idx} burst "
                            f"{consecutive_rate_limits} — cooldown {wait:.0f}s")
                        consecutive_rate_limits = 0
                    else:
                        wait = parsed_retry_after
                        log(f"  [rate limit] idx={orig_idx} attempt={rate_limit_retries} "
                            f"waiting {wait:.0f}s")
                    # #region agent log
                    _debug_log(
                        run_id=debug_run_id,
                        hypothesis_id="H1_H2_H3_H4_H5",
                        location="run_prompting_stratified.py:classify_sample:rate_limit_exception",
                        message="rate_limit_detected",
                        data={
                            "idx": orig_idx,
                            "parse_retries": parse_retries,
                            "rate_limit_retries": rate_limit_retries,
                            "consecutive_rate_limits": consecutive_rate_limits,
                            "chosen_wait_seconds": wait,
                            "parsed_retry_after_seconds": parsed_retry_after,
                            "error_excerpt": err_str[:400],
                            "error_len": len(err_str),
                            "seconds_since_last_success": (
                                None if last_success_ts is None else round(time.time() - last_success_ts, 3)
                            ),
                        },
                    )
                    # #endregion
                    time.sleep(wait)
                    continue
                consecutive_rate_limits = 0
                rate_limit_streak = 0
                parse_retries += 1
                log(f"  [error] idx={orig_idx} parse_retry={parse_retries} {err_str[:120]}")
                time.sleep(2)
                continue

            consecutive_rate_limits = 0
            rate_limit_streak = 0
            chain.memory.chat_memory.messages = chain.memory.chat_memory.messages[:-2]
            text = response["text"]
            output_chars = len(text)
            last_success_ts = time.time()
            # #region agent log
            _debug_log(
                run_id=debug_run_id,
                hypothesis_id="H2_H5",
                location="run_prompting_stratified.py:classify_sample:response_success",
                message="request_success",
                data={
                    "idx": orig_idx,
                    "parse_retries": parse_retries,
                    "rate_limit_retries": rate_limit_retries,
                    "output_chars": output_chars,
                },
            )
            # #endregion
            if prompt_family:
                parsed = parse_family_output(prompt_family, text)
                parse_ok = parsed.is_valid
                parse_error = parsed.error
                reason = text
                if parsed.label in ("BORDER", "NOBORDER"):
                    scene_change = parsed.label == "BORDER"
                elif prompt_family in {"H", "I"} and parsed.is_valid:
                    inferred, infer_error = infer_chunk_family_label(
                        prompt_family,
                        parsed.payload,
                        target_local_id=target_local_id if target_local_id is not None else 1,
                        score_threshold=score_threshold,
                    )
                    if inferred is None:
                        scene_change = None
                        parse_ok = False
                        parse_error = infer_error
                    else:
                        scene_change = inferred
                        parse_ok = True
                        parse_error = ""
                else:
                    loose = parse_response_loose(text)
                    if loose is not None:
                        scene_change = loose
                        parse_ok = True
                        parse_error = ""
                    else:
                        scene_change = None
            else:
                scene_change, reason = parse_response(text, prompt_mode)
                parse_ok = scene_change is not None
                parse_error = "" if parse_ok else "parse_response_none"
                if scene_change is None:
                    loose = parse_response_loose(text)
                    if loose is not None:
                        scene_change = loose
                        parse_ok = True
                        parse_error = ""
            if scene_change is None:
                parse_retries += 1
                first_line = text.split("\n")[0]
                log(f"  [parse retry {parse_retries}] idx={orig_idx} invalid response: "
                    f"{first_line[:80]}")
                time.sleep(1)

        if scene_change is None:
            scene_change = False
            if not reason:
                reason = "FAILED_TO_CLASSIFY"
            parse_ok = False
            if not parse_error:
                parse_error = "failed_to_classify"
            # #region agent log
            _debug_log(
                run_id=debug_run_id,
                hypothesis_id="H2_H4",
                location="run_prompting_stratified.py:classify_sample:classification_failed",
                message="sentence_failed_after_retries",
                data={
                    "idx": orig_idx,
                    "parse_retries": parse_retries,
                    "rate_limit_retries": rate_limit_retries,
                    "consecutive_rate_limits": consecutive_rate_limits,
                    "rate_limit_streak": rate_limit_streak,
                    "rate_limit_exhausted": rate_limit_exhausted,
                    "parse_error": parse_error,
                },
            )
            # #endregion

        pred_str = "BORDER" if scene_change else "NOBORDER"
        match = "OK" if pred_str == gold else "MISS"
        log(f"{progress_bar(count + 1, total)} idx={orig_idx} done "
            f"pred={pred_str} gold={gold} {match} "
            f"(elapsed {time.time() - sent_t0:.1f}s)")

        cache[key] = {
            "pred": pred_str,
            "reason": reason,
            "gold": gold,
            "sentence": sentence.text,
            "parse_ok": parse_ok,
            "parse_error": parse_error,
            "output_chars": output_chars,
            "latency_seconds": round(time.time() - sent_t0, 4),
            "chunk_target_local_id": target_local_id,
        }

        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
        log(f"{progress_bar(count + 1, total)} checkpoint saved ({len(cache)} cached)")

    log(f"Finished classification loop ({len(cache)} cached entries total)")
    return cache


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--max_per_class", type=int, default=0,
                        help="Cap per class per novel (0 = all borders + matched noborders)")
    parser.add_argument("--dry_run", type=int, default=0,
                        help="Classify only N sentences total per novel (0 = all)")
    parser.add_argument("--date", type=str, default=None,
                        help="Override output date folder (default: today)")
    parser.add_argument("--model", type=str, default=None,
                        help="OpenRouter model name (default: nvidia/nemotron-3-super-120b-a12b:free)")
    parser.add_argument("--prompt", choices=["no-cot", "cot-list"], default="no-cot",
                        help="Prompt style: no-cot (default) or cot-list (step-by-step)")
    parser.add_argument("--reasoning", choices=["on", "off", "low"], default="on",
                        help="Model-level thinking/reasoning: on (default) or off")
    parser.add_argument("--context_size", type=int, default=None,
                        help="Context window in tokens (default: 409 = 512*0.8)")
    parser.add_argument("--full_eval", action="store_true",
                        help="Evaluate all sentences (natural distribution) instead of stratified sample")
    parser.add_argument("--prompt_family", choices=list(PROMPT_FAMILIES), default=None,
                        help="Prompt template family ID from src/prompts (A..J)")
    parser.add_argument("--prompts_dir", type=Path,
                        default=prompts_dir(Path(__file__)),
                        help="Directory containing prompt templates and registry.json")
    parser.add_argument("--few_shot_file", type=Path, default=None,
                        help="Path to few-shot examples text inserted into D/E templates")
    parser.add_argument("--temperature", type=float, default=0.0,
                        help="Decoding temperature (default: 0.0)")
    parser.add_argument("--top_p", type=float, default=1.0,
                        help="Decoding top_p (default: 1.0)")
    parser.add_argument("--top_k", type=int, default=None,
                        help="Optional top_k (provider/model dependent)")
    parser.add_argument("--min_p", type=float, default=None,
                        help="Optional min_p (provider/model dependent)")
    parser.add_argument("--seed", type=int, default=SEED,
                        help=f"Random seed for sampling/requests (default: {SEED})")
    parser.add_argument("--max_tokens", type=int, default=256,
                        help="Max output tokens per request (default: 256)")
    parser.add_argument("--stop", action="append", default=[],
                        help="Optional stop sequence(s); may be provided multiple times")
    parser.add_argument("--response_format", choices=["none", "json_object", "json_schema"], default="none",
                        help="Structured output mode when supported by model/provider")
    parser.add_argument("--schema_file", type=Path, default=None,
                        help="Optional JSON schema file used when --response_format=json_schema")
    parser.add_argument("--chunk_window", type=int, default=2,
                        help="Chunk half-window (sentences on each side) for H/I families")
    parser.add_argument("--score_threshold", type=float, default=50.0,
                        help="Boundary threshold for I family score mode (0-100)")
    parser.add_argument("--request_delay", type=float, default=0.0,
                        help="Seconds to sleep after each successful API response (default: 0)")
    parser.add_argument("--max_parse_retries", type=int, default=DEFAULT_MAX_PARSE_RETRIES,
                        help="Max parse/format retries per sentence (default: 15)")
    parser.add_argument("--max_rate_limit_retries", type=int, default=DEFAULT_MAX_RATE_LIMIT_RETRIES,
                        help="Max 429/rate-limit retries per sentence (default: 40)")
    parser.add_argument("--max_consecutive_rate_limits", type=int,
                        default=DEFAULT_MAX_CONSECUTIVE_RATE_LIMITS,
                        help="Skip sentence after this many consecutive 429/rate-limit errors (default: 8)")
    parser.add_argument("--rate_limit_burst_threshold", type=int,
                        default=DEFAULT_RATE_LIMIT_BURST_THRESHOLD,
                        help="Consecutive 429s before a long cooldown (default: 5)")
    parser.add_argument("--rate_limit_cooldown", type=float, default=DEFAULT_RATE_LIMIT_COOLDOWN_SEC,
                        help="Long cooldown seconds after a 429 burst (default: 180)")
    parser.add_argument("--excel_manifest", type=Path, default=None,
                        help="Optional processed Excel manifest JSON to run stratified prompting without XMI.")
    parser.add_argument("--documents", type=str, default=None,
                        help="Comma-separated document stems to run (default: all in data dir)")
    args = parser.parse_args()

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key or api_key == "Your OpenRouter API Key":
        log("ERROR: Set OPENROUTER_API_KEY environment variable")
        sys.exit(1)

    ctx = args.context_size or int(512 * 0.8)
    model = DEFAULT_MODEL
    if args.model:
        model = Model(args.model, ctx, json=False, openai=False, openrouter=True)
    elif args.context_size:
        model = Model(model.name, ctx, json=model.json, openai=model.openai, openrouter=model.openrouter)

    prompt_family = args.prompt_family
    template_text = ""
    few_shot_examples = ""
    if prompt_family:
        registry = load_prompt_registry(args.prompts_dir)
        template_text = get_template_text(args.prompts_dir, prompt_family, registry)
        if args.few_shot_file:
            few_shot_examples = args.few_shot_file.read_text(encoding="utf-8")
        prompt_text = (
            "You are a precise scene segmentation assistant. "
            "Follow the requested output format exactly."
        )
    else:
        prompt_text = prompt_classify if args.prompt == "no-cot" else prompt_classify_cot

    json_schema = None
    if args.response_format == "json_schema" and args.schema_file:
        json_schema = json.loads(args.schema_file.read_text(encoding="utf-8"))
    model_kwargs = build_openrouter_model_kwargs(
        reasoning=args.reasoning,
        temperature=args.temperature,
        top_p=args.top_p,
        top_k=args.top_k,
        min_p=args.min_p,
        seed=args.seed,
        max_tokens=args.max_tokens,
        stop=args.stop or None,
        response_format=args.response_format,
        json_schema=json_schema,
    )

    run_date = args.date or date.today().isoformat()
    model_slug = model.name.replace("/", "_").replace(":", "_")
    prompt_tag = f"family{prompt_family}" if prompt_family else args.prompt.replace("-", "")
    reasoning_tag = f"reasoning-{args.reasoning}"
    mode_tag = "full" if args.full_eval else "strat"
    output_dir = prompting_run_root(ROOT_DIR, run_date) / f"{mode_tag}_{model_slug}_{prompt_tag}_{reasoning_tag}"
    output_dir.mkdir(parents=True, exist_ok=True)
    run_config = {
        "max_per_class": args.max_per_class,
        "dry_run": args.dry_run,
        "date": run_date,
        "model": model.name,
        "prompt": args.prompt,
        "reasoning": args.reasoning,
        "context_size": model.context_size,
        "full_eval": args.full_eval,
        "prompt_family": args.prompt_family,
        "prompts_dir": str(args.prompts_dir),
        "few_shot_file": str(args.few_shot_file) if args.few_shot_file else None,
        "temperature": args.temperature,
        "top_p": args.top_p,
        "top_k": args.top_k,
        "min_p": args.min_p,
        "seed": args.seed,
        "max_tokens": args.max_tokens,
        "stop": args.stop,
        "response_format": args.response_format,
        "schema_file": str(args.schema_file) if args.schema_file else None,
        "chunk_window": args.chunk_window,
        "score_threshold": args.score_threshold,
        "request_delay": args.request_delay,
        "max_parse_retries": args.max_parse_retries,
        "max_rate_limit_retries": args.max_rate_limit_retries,
        "max_consecutive_rate_limits": args.max_consecutive_rate_limits,
        "rate_limit_burst_threshold": args.rate_limit_burst_threshold,
        "rate_limit_cooldown": args.rate_limit_cooldown,
        "excel_manifest": str(args.excel_manifest) if args.excel_manifest else None,
        "output_dir": str(output_dir),
        "data_dir": str(DATA_DIR),
    }
    run_id = f"run_{int(time.time())}"
    # #region agent log
    _agent_debug_log(
        run_id=run_id,
        hypothesis_id="H1_H5",
        location="run_prompting_stratified.py:main",
        message="run_configuration",
        data={
            "model": model.name,
            "prompt_family": args.prompt_family,
            "reasoning": args.reasoning,
            "full_eval": args.full_eval,
            "max_per_class": args.max_per_class,
            "excel_manifest": str(args.excel_manifest) if args.excel_manifest else None,
            "response_format": args.response_format,
            "context_size": model.context_size,
        },
    )
    # #endregion
    write_repro_files(output_dir, sys.argv, run_config)
    log(f"Model: {model.name}")
    log(f"Context size: {model.context_size} tokens")
    log(f"Prompt: {args.prompt}")
    if prompt_family:
        log(f"Prompt family: {prompt_family}")
    log(f"Reasoning: {args.reasoning}")
    log(f"Eval mode: {'full_eval' if args.full_eval else 'stratified'}")
    log(f"Decode: temp={args.temperature}, top_p={args.top_p}, max_tokens={args.max_tokens}")
    if prompt_family in {"H", "I"}:
        log(f"Chunk mode: window={args.chunk_window}, score_threshold={args.score_threshold}")
    if args.request_delay > 0:
        log(f"Request pacing: delay={args.request_delay}s before each API attempt")
    log(f"Rate limits: burst_threshold={args.rate_limit_burst_threshold}, "
        f"cooldown={args.rate_limit_cooldown}s, max_429_retries={args.max_rate_limit_retries}, "
        f"max_consecutive_429={args.max_consecutive_rate_limits}")
    log(f"Output: {output_dir}")

    docs_to_run: list[dict[str, Any]] = []
    if args.excel_manifest:
        manifest_path = args.excel_manifest.expanduser()
        if not manifest_path.is_absolute():
            manifest_path = ROOT_DIR / manifest_path
        manifest_path = manifest_path.resolve()
        if not manifest_path.exists():
            log(f"ERROR: Excel manifest not found: {manifest_path}")
            sys.exit(1)
        docs_to_run = load_excel_manifest_docs(manifest_path)
    else:
        xmi_files = sorted(DATA_DIR.glob("*.xmi.zip"))
        if not xmi_files:
            log(f"ERROR: No .xmi.zip files in {DATA_DIR}")
            sys.exit(1)
        for xmi_path in xmi_files:
            docs_to_run.append(
                {
                    "stem": xmi_path.name.replace(".xmi.zip", ""),
                    "source_file": xmi_path.name,
                    "xmi_path": xmi_path,
                    "input_mode": "xmi",
                }
            )

    if args.documents:
        allowed = {s.strip() for s in args.documents.split(",") if s.strip()}
        docs_to_run = [d for d in docs_to_run if d["stem"] in allowed]
        if not docs_to_run:
            log(f"ERROR: No documents matched --documents={args.documents!r}")
            sys.exit(1)

    all_doc_results = {}

    for item in docs_to_run:
        stem = item["stem"]
        log(f"{'='*60}")
        log(f"Document: {stem}")
        log(f"{'='*60}")
        input_mode = item["input_mode"]
        if input_mode == "xmi":
            xmi_path = item["xmi_path"]
            log(f"Loading XMI: {xmi_path}")
            doc_t0 = time.time()
            doc = UIMADocument.from_xmi(xmi_path)
            log(f"Loaded XMI in {time.time() - doc_t0:.1f}s")
            sentences = list(doc.sentences)
            full_gold = [get_label_simple(s, coarse=True).value for s in sentences]
        else:
            doc = item["doc"]
            sentences = item["sentences"]
            full_gold = item["full_gold"]
            log(f"Loaded manifest text source: {item['source_file']} ({len(sentences)} sentences)")
        total_sents = len(sentences)
        n_gold_borders = sum(1 for g in full_gold if g == "BORDER")
        border_positions = [i for i, g in enumerate(full_gold) if g == "BORDER"]
        border_gaps = [
            border_positions[i] - border_positions[i - 1]
            for i in range(1, len(border_positions))
        ]
        avg_border_gap = (
            round(sum(border_gaps) / len(border_gaps), 2) if border_gaps else None
        )
        min_border_gap = min(border_gaps) if border_gaps else None
        max_border_gap = max(border_gaps) if border_gaps else None

        if args.full_eval:
            if input_mode == "xmi":
                sample = build_full_sample(doc)
            else:
                sample = build_full_sample_from_labels(sentences, full_gold)
        else:
            if input_mode == "xmi":
                sample = build_stratified_sample(doc, args.seed, max_per_class=args.max_per_class)
            else:
                sample = build_stratified_sample_from_labels(
                    sentences, full_gold, args.seed, max_per_class=args.max_per_class
                )
        n_border_sampled = sum(1 for _, _, g in sample if g == "BORDER")
        n_noborder_sampled = sum(1 for _, _, g in sample if g == "NOBORDER")
        # #region agent log
        _agent_debug_log(
            run_id=run_id,
            hypothesis_id="H1_H2",
            location="run_prompting_stratified.py:main",
            message="document_sampling_profile",
            data={
                "stem": stem,
                "input_mode": input_mode,
                "total_sentences": total_sents,
                "gold_borders": n_gold_borders,
                "sampled_total": len(sample),
                "sampled_borders": n_border_sampled,
                "sampled_noborders": n_noborder_sampled,
            },
        )
        _agent_debug_log(
            run_id=run_id,
            hypothesis_id="H6",
            location="run_prompting_stratified.py:main",
            message="gold_boundary_structure",
            data={
                "stem": stem,
                "input_mode": input_mode,
                "border_rate": round(
                    (n_gold_borders / total_sents), 4
                ) if total_sents else 0.0,
                "n_gold_borders": n_gold_borders,
                "avg_border_gap": avg_border_gap,
                "min_border_gap": min_border_gap,
                "max_border_gap": max_border_gap,
            },
        )
        # #endregion

        log(f"  Total sentences: {total_sents}")
        log(f"  Gold borders: {n_gold_borders}")
        log(f"  Sampled: {len(sample)} ({n_border_sampled} BORDER + {n_noborder_sampled} NOBORDER)")

        cache_path = output_dir / f"cache_{stem.replace(' ', '_')}.json"
        chain = get_chain(model, prompt_text, extra_model_kwargs=model_kwargs)
        cache = classify_sample(sample, doc, chain, model, cache_path,
                                dry_run=args.dry_run, prompt_mode=args.prompt,
                                prompt_family=prompt_family,
                                template_text=template_text,
                                few_shot_examples=few_shot_examples,
                                chunk_window=args.chunk_window,
                                score_threshold=args.score_threshold,
                                request_delay=args.request_delay,
                                max_parse_retries=args.max_parse_retries,
                                max_rate_limit_retries=args.max_rate_limit_retries,
                                max_consecutive_rate_limits=args.max_consecutive_rate_limits,
                                rate_limit_burst_threshold=args.rate_limit_burst_threshold,
                                rate_limit_cooldown=args.rate_limit_cooldown)

        sampled_indices = []
        sampled_preds = []
        sampled_golds = []
        reasons = []
        compact_decisions = []
        sent_texts = []
        parse_flags = []
        parse_errors = []
        output_chars_list = []
        latencies = []

        for orig_idx, _sent, gold in sample:
            key = str(orig_idx)
            if key not in cache:
                continue
            entry = cache[key]
            sampled_indices.append(orig_idx)
            sampled_preds.append(entry["pred"])
            sampled_golds.append(entry["gold"])
            reasons.append(entry["reason"])
            compact_decisions.append(_compact_decision(entry["reason"]))
            sent_texts.append(entry["sentence"])
            parse_flags.append(bool(entry.get("parse_ok", False)))
            parse_errors.append(entry.get("parse_error", ""))
            output_chars_list.append(float(entry.get("output_chars", 0) or 0))
            latencies.append(float(entry.get("latency_seconds", 0) or 0))

        n_classified = len(sampled_indices)
        n_correct = sum(1 for p, g in zip(sampled_preds, sampled_golds) if p == g)
        parse_failure_count = sum(1 for ok in parse_flags if not ok)
        parse_failure_rate = (parse_failure_count / n_classified) if n_classified else 0.0
        avg_output_chars = (sum(output_chars_list) / len(output_chars_list)) if output_chars_list else 0.0
        avg_latency_seconds = (sum(latencies) / len(latencies)) if latencies else 0.0

        metrics = {}
        for tol in (0, 1, 3):
            metrics[f"tol_{tol}"] = evaluate_sampled(
                sampled_indices, sampled_preds, full_gold, tol)

        doc_result = {
            "file": item["source_file"],
            "total_sentences": total_sents,
            "gold_borders": n_gold_borders,
            "sample_mode": "full_eval" if args.full_eval else "stratified",
            "sampled": n_classified,
            "sampled_borders": sum(1 for g in sampled_golds if g == "BORDER"),
            "sampled_noborders": sum(1 for g in sampled_golds if g == "NOBORDER"),
            "accuracy": round(n_correct / n_classified, 4) if n_classified else 0,
            "parse_failure_count": parse_failure_count,
            "parse_failure_rate": round(parse_failure_rate, 4),
            "avg_output_chars": round(avg_output_chars, 2),
            "avg_latency_seconds": round(avg_latency_seconds, 3),
            "metrics": metrics,
        }
        all_doc_results[stem] = doc_result

        results_path = output_dir / f"results_{stem.replace(' ', '_')}.json"
        results_data = {
            "model": model.name,
            "provider": "openrouter",
            "file": item["source_file"],
            "original_indices": sampled_indices,
            "labels": [p == "BORDER" for p in sampled_preds],
            "predictions": sampled_preds,
            "ground_truth": sampled_golds,
            "reasons": reasons,
            "compact_decisions": compact_decisions,
            "sentences": sent_texts,
            "parse_ok": parse_flags,
            "parse_error": parse_errors,
            "output_chars": output_chars_list,
            "latency_seconds": latencies,
            "metrics": metrics,
        }
        results_path.write_text(json.dumps(results_data, indent=2, ensure_ascii=False))
        review_schema_path = output_dir / "review_schema.json"
        if not review_schema_path.exists():
            review_schema_path.write_text(
                json.dumps(_review_schema(), indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
        review_path = output_dir / f"review_{stem.replace(' ', '_')}.jsonl"
        with review_path.open("w", encoding="utf-8") as handle:
            for idx, orig_idx in enumerate(sampled_indices):
                pred_bool = sampled_preds[idx] == "BORDER"
                record = {
                    "sentence_index": orig_idx,
                    "sentence_text_full": sent_texts[idx],
                    "prediction_label": sampled_preds[idx],
                    "prediction_bool": pred_bool,
                    "ground_truth_label": sampled_golds[idx],
                    "parse_ok": bool(parse_flags[idx]),
                    "parse_error": parse_errors[idx],
                    "compact_decision": compact_decisions[idx],
                    "raw_model_response": reasons[idx],
                    "latency_seconds": float(latencies[idx]),
                    "output_chars": float(output_chars_list[idx]),
                    "input_mode": input_mode,
                    "prompt_mode": args.prompt,
                    "prompt_family": prompt_family,
                    "model": model.name,
                    "source_file": item["source_file"],
                }
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")

        log(f"  Results for {stem}:")
        log(f"    Classified: {n_classified}, Accuracy: {doc_result['accuracy']:.1%}")
        log(
            f"    Parse failures: {parse_failure_count}/{n_classified} "
            f"({parse_failure_rate:.1%}), avg chars={avg_output_chars:.1f}, "
            f"avg latency={avg_latency_seconds:.2f}s"
        )
        for tol_key, m in metrics.items():
            log(
                f"    {tol_key}: P={m['precision']:.3f} R={m['recall']:.3f} F1={m['f1']:.3f}"
                f"  (TP={m['tp']} FP={m['fp']} FN={m['fn']})"
            )

    # Aggregate summary
    summary = {
        "model": model.name,
        "provider": "openrouter",
        "prompt_family": prompt_family,
        "prompt_mode": args.prompt,
        "reasoning": args.reasoning,
        "seed": args.seed,
        "full_eval": args.full_eval,
        "decode": {
            "temperature": args.temperature,
            "top_p": args.top_p,
            "top_k": args.top_k,
            "min_p": args.min_p,
            "max_tokens": args.max_tokens,
            "stop": args.stop,
            "response_format": args.response_format,
        },
        "date": run_date,
        "documents": all_doc_results,
    }

    # Compute macro-average metrics across documents
    if all_doc_results:
        for tol in (0, 1, 3):
            key = f"tol_{tol}"
            vals = [d["metrics"][key] for d in all_doc_results.values()]
            summary[f"macro_avg_{key}"] = {
                "precision": round(sum(v["precision"] for v in vals) / len(vals), 4),
                "recall": round(sum(v["recall"] for v in vals) / len(vals), 4),
                "f1": round(sum(v["f1"] for v in vals) / len(vals), 4),
            }
        summary["avg_parse_failure_rate"] = round(
            sum(d.get("parse_failure_rate", 0.0) for d in all_doc_results.values()) / len(all_doc_results), 4
        )
        summary["avg_output_chars"] = round(
            sum(d.get("avg_output_chars", 0.0) for d in all_doc_results.values()) / len(all_doc_results), 2
        )
        summary["avg_latency_seconds"] = round(
            sum(d.get("avg_latency_seconds", 0.0) for d in all_doc_results.values()) / len(all_doc_results), 3
        )

    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))

    log(f"{'='*60}")
    log("AGGREGATE RESULTS")
    log(f"{'='*60}")
    for tol in (0, 1, 3):
        key = f"macro_avg_tol_{tol}"
        if key in summary:
            m = summary[key]
            log(f"  {key}: P={m['precision']:.3f} R={m['recall']:.3f} F1={m['f1']:.3f}")
    log(f"Summary: {summary_path}")
    log(f"Output dir: {output_dir}")


if __name__ == "__main__":
    main()
