"""Minimal prompting baseline runner for Phase 3.2.

Uses OpenRouter with nvidia/nemotron-3-super-120b-a12b:free to classify scene
boundaries on a small subset of sentences from an XMI file or local TXT file.

Run from project root:
    OPENROUTER_API_KEY=sk-or-... python src/runners/run_prompting_baseline.py

Options:
    --prompt {no-cot,cot-list}  Prompt style (default: no-cot)
    --reasoning {on,off}        Model-level thinking (default: on)
"""
import json
import argparse
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

_FILE = Path(__file__).resolve()
_SRC_ROOT = _FILE.parents[1]
_ROOT_DIR = _SRC_ROOT.parent
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))
sys.path.insert(0, str(_ROOT_DIR / "upstream" / "scene-segmentation"))

from wuenlp.impl.UIMANLPStructs import UIMADocument
from prompting.classify import (
    build_sentence_sample, get_chain, nemotron, prompt_classify, prompt_classify_cot, Model
)
from utils.constants import Label, SCENE_TYPES, NONSCENE_TYPES
from core.prompt_runtime import (
    PROMPT_FAMILIES,
    build_openrouter_model_kwargs,
    get_template_text,
    load_prompt_registry,
    parse_family_output,
    render_prompt_for_family,
)
from core.workflow_runtime import (
    output_dir_for,
    project_root,
    prompts_dir,
    stss_test2_data_dir,
    write_repro_files,
)


def get_label_simple(sentence, coarse=True):
    """Simplified get_label that avoids importing ssc.dataset (Unsloth dep)."""
    from wuenlp.impl.UIMANLPStructs import UIMAScene, UIMASentence
    covering_scenes = sentence.covering(UIMAScene)
    if not covering_scenes:
        return Label.NOBORDER
    current_scene = covering_scenes[0]
    previous_scene = current_scene.previous
    covered_sentences = current_scene.covered(UIMASentence)
    if covered_sentences and covered_sentences[0] == sentence:
        if coarse:
            return Label.BORDER
    return Label.NOBORDER

ROOT_DIR = project_root(Path(__file__))
DATA_DIR = stss_test2_data_dir(ROOT_DIR)

MAX_SENTENCES = 20
TXT_CONTEXT_WINDOW = 1


def log(msg):
    """Timestamped, unbuffered terminal logging."""
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


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
_STRICT_SUFFIX_H = (
    "\n\nReturn exactly one token on the last line: a sentence number or NONE."
)
_STRICT_SUFFIX_I = (
    "\n\nReturn JSON array only. One object per sentence in the chunk with keys "
    "sentence_id (int) and score (0-100). No prose."
)

_SCHEMA_A_LABEL_ONLY = {
    "name": "scene_boundary_label_only",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "label": {"type": "string", "enum": ["BORDER", "NOBORDER"]}
        },
        "required": ["label"],
        "additionalProperties": False,
    },
}

_SCHEMA_I_SCORE_ARRAY = {
    "name": "scene_boundary_scores",
    "strict": True,
    "schema": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "sentence_id": {"type": "integer", "minimum": 1},
                "score": {"type": "number", "minimum": 0, "maximum": 100},
            },
            "required": ["sentence_id", "score"],
            "additionalProperties": False,
        },
    },
}


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
        "sentence_index": "int (0-based sentence index)",
        "sentence_text_full": "str (full sentence text, not truncated)",
        "prediction_label": "str (BORDER|NOBORDER)",
        "prediction_bool": "bool",
        "ground_truth_label": "str|null",
        "parse_ok": "bool",
        "parse_error": "str",
        "compact_decision": "str (short parsed/normalized rationale)",
        "raw_model_response": "str (full raw model output)",
        "latency_seconds": "float",
        "output_chars": "int",
        "input_mode": "str (xmi|txt)",
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


def _resolve_txt_source(args: argparse.Namespace) -> Path:
    if args.txt_file is not None:
        txt_path = args.txt_file.expanduser()
        if not txt_path.is_absolute():
            txt_path = ROOT_DIR / txt_path
        txt_path = txt_path.resolve()
        if not txt_path.exists():
            raise FileNotFoundError(f"TXT file not found: {txt_path}")
        return txt_path

    manifest_path = args.txt_manifest.expanduser()
    if not manifest_path.is_absolute():
        manifest_path = ROOT_DIR / manifest_path
    manifest_path = manifest_path.resolve()
    if not manifest_path.exists():
        raise FileNotFoundError(f"TXT manifest not found: {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = manifest.get("files", [])
    if not files:
        raise ValueError(f"No files in TXT manifest: {manifest_path}")
    first_entry = files[0]
    first_name = first_entry.get("name")
    if not isinstance(first_name, str) or not first_name:
        raise ValueError("TXT manifest first entry missing valid 'name'.")

    candidates: list[Path] = []
    rel_path = first_entry.get("path")
    if isinstance(rel_path, str) and rel_path:
        candidates.append(ROOT_DIR / "data" / rel_path)
    candidates.extend(
        [
            ROOT_DIR / "data" / "raw" / "kleist_multilingual" / first_name,
            ROOT_DIR / "data" / "raw" / first_name,
            manifest_path.parent / "raw" / first_name,
        ]
    )
    for txt_path in candidates:
        if txt_path.exists():
            return txt_path.resolve()
    raise FileNotFoundError(f"TXT file from manifest not found: {first_name}")


def _split_txt_sentences(text: str) -> list[str]:
    # Prefer line-preserving segmentation when input is one sentence per line
    # (e.g., preprocessed Excel sentence exports). This keeps indices aligned
    # with external gold labels.
    line_based = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if len(line_based) > 1:
        return line_based

    flat_text = re.sub(r"\s+", " ", text).strip()
    if not flat_text:
        return []
    parts = re.split(r"(?<=[.!?])\s+", flat_text)
    sentences = [part.strip() for part in parts if part.strip()]
    return sentences if sentences else [flat_text]


def _build_txt_sample(sentences: list[str], index: int) -> str:
    start = max(0, index - TXT_CONTEXT_WINDOW)
    end = min(len(sentences), index + TXT_CONTEXT_WINDOW + 1)
    context = []
    for i in range(start, end):
        if i == index:
            context.append(f"<sentence>{sentences[i]}</sentence>")
        else:
            context.append(sentences[i])
    return " ".join(context)


def _strict_suffix_for_family(family: Optional[str]) -> str:
    if family == "H":
        return _STRICT_SUFFIX_H
    if family == "I":
        return _STRICT_SUFFIX_I
    return _STRICT_SUFFIX


def _build_chunk_sentences(sentences: list[str], center_idx: int, chunk_window: int) -> tuple[str, int]:
    start = max(0, center_idx - chunk_window)
    end = min(len(sentences), center_idx + chunk_window + 1)
    lines: list[str] = []
    for idx in range(start, end):
        local_id = idx - start + 1
        lines.append(f"{local_id}. {sentences[idx]}")
    target_local_id = center_idx - start + 1
    return "\n".join(lines), target_local_id


def _infer_chunk_family_label(
    family: str,
    parsed_payload: Any,
    *,
    target_local_id: int,
    score_threshold: float,
) -> tuple[Optional[bool], str]:
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
        if len(parsed_payload) == 0:
            return None, "scores_empty"
        by_id: dict[int, float] = {}
        for row in parsed_payload:
            if not isinstance(row, dict):
                continue
            sid = row.get("sentence_id")
            score = row.get("score")
            try:
                sid_i = int(sid)
                score_f = float(score)
            except (TypeError, ValueError):
                continue
            by_id[sid_i] = score_f
        if target_local_id not in by_id:
            return None, "target_sentence_missing_in_scores"
        return by_id[target_local_id] >= score_threshold, ""

    return None, "unsupported_chunk_family"


def main():
    parser = argparse.ArgumentParser(description="Run prompting baseline on first N sentences.")
    parser.add_argument("--model", type=str, default=None, help="OpenRouter model name override.")
    parser.add_argument("--output_dir", type=Path, default=None, help="Output directory override.")
    parser.add_argument("--max_sentences", type=int, default=MAX_SENTENCES,
                        help=f"Number of leading sentences to classify (default: {MAX_SENTENCES}).")
    parser.add_argument("--max_retries", type=int, default=10,
                        help="Max retries per sentence when API fails (default: 10).")
    parser.add_argument("--max_wait", type=int, default=30,
                        help="Max rate-limit wait seconds per retry (default: 30).")
    parser.add_argument("--prompt", choices=["no-cot", "cot-list"], default="no-cot",
                        help="Prompt style: no-cot (default) or cot-list (step-by-step)")
    parser.add_argument("--reasoning", choices=["on", "off", "low"], default="on",
                        help="Model-level thinking/reasoning: on (default) or off")
    parser.add_argument("--context_size", type=int, default=None,
                        help="Context window in tokens (default: 409 = 512*0.8)")
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
    parser.add_argument("--seed", type=int, default=1337,
                        help="Seed for request reproducibility when supported")
    parser.add_argument("--max_tokens", type=int, default=256,
                        help="Max output tokens per request (default: 256)")
    parser.add_argument("--stop", action="append", default=[],
                        help="Optional stop sequence(s); may be provided multiple times")
    parser.add_argument("--response_format", choices=["none", "json_object", "json_schema"], default="none",
                        help="Structured output mode when supported by model/provider")
    parser.add_argument("--schema_file", type=Path, default=None,
                        help="Optional JSON schema file used when --response_format=json_schema")
    parser.add_argument("--input_mode", choices=["xmi", "txt"], default="xmi",
                        help="Input format: xmi (default) or txt")
    parser.add_argument("--txt_manifest", type=Path, default=Path("data/manifests/raw_txt.json"),
                        help="TXT manifest path used when --input_mode txt and --txt_file is not set")
    parser.add_argument("--txt_file", type=Path, default=None,
                        help="Single TXT file path override for --input_mode txt")
    parser.add_argument("--chunk_window", type=int, default=2,
                        help="Chunk half-window for H/I families (sentences each side)")
    parser.add_argument("--score_threshold", type=float, default=50.0,
                        help="Boundary threshold for family I score mode (0-100)")
    args = parser.parse_args()

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key or api_key == "Your OpenRouter API Key":
        log("ERROR: Set OPENROUTER_API_KEY environment variable")
        sys.exit(1)

    xmi_file = DATA_DIR / "Aus guter Familie.xmi.zip"
    txt_file: Path | None = None
    if args.input_mode == "xmi":
        if not xmi_file.exists():
            log(f"ERROR: File not found: {xmi_file}")
            sys.exit(1)
    else:
        try:
            txt_file = _resolve_txt_source(args)
        except Exception as exc:  # noqa: BLE001
            log(f"ERROR: {exc}")
            sys.exit(1)

    ctx = args.context_size or int(512 * 0.8)
    model = nemotron
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

    effective_response_format = args.response_format
    json_schema = None
    if args.response_format == "json_schema" and args.schema_file:
        json_schema = json.loads(args.schema_file.read_text(encoding="utf-8"))
    elif args.response_format == "none" and prompt_family == "A":
        effective_response_format = "json_schema"
        json_schema = _SCHEMA_A_LABEL_ONLY
    elif args.response_format == "none" and prompt_family == "I":
        effective_response_format = "json_schema"
        json_schema = _SCHEMA_I_SCORE_ARRAY
    model_kwargs = build_openrouter_model_kwargs(
        reasoning=args.reasoning,
        temperature=args.temperature,
        top_p=args.top_p,
        top_k=args.top_k,
        min_p=args.min_p,
        seed=args.seed,
        max_tokens=args.max_tokens,
        stop=args.stop or None,
        response_format=effective_response_format,
        json_schema=json_schema,
    )

    run_date = datetime.now().date().isoformat()
    out_dir = args.output_dir or output_dir_for(ROOT_DIR, "prompting", run_date, "baseline_qwen3")
    out_dir.mkdir(parents=True, exist_ok=True)
    data_file = str(xmi_file if args.input_mode == "xmi" else txt_file)
    run_config = {
        "input_mode": args.input_mode,
        "model": args.model or nemotron.name,
        "max_sentences": args.max_sentences,
        "max_retries": args.max_retries,
        "max_wait": args.max_wait,
        "prompt": args.prompt,
        "reasoning": args.reasoning,
        "context_size": args.context_size,
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
        "response_format_effective": effective_response_format,
        "schema_file": str(args.schema_file) if args.schema_file else None,
        "output_dir": str(out_dir),
        "data_file": data_file,
        "txt_manifest": str(args.txt_manifest),
        "txt_file": str(args.txt_file) if args.txt_file else None,
        "chunk_window": args.chunk_window,
        "score_threshold": args.score_threshold,
    }
    write_repro_files(out_dir, sys.argv, run_config)
    log(f"Model: {model.name}")
    log(f"Context size: {model.context_size} tokens")
    log(f"Prompt: {args.prompt}")
    if prompt_family:
        log(f"Prompt family: {prompt_family}")
    log(f"Reasoning: {args.reasoning}")
    log(
        f"Decode: temp={args.temperature}, top_p={args.top_p}, "
        f"max_tokens={args.max_tokens}, response_format={effective_response_format}"
    )
    if prompt_family in {"H", "I"}:
        log(f"Chunk mode: window={args.chunk_window}, score_threshold={args.score_threshold}")
    log(f"Output dir: {out_dir}")

    text_sentences: list[str] = []
    doc: UIMADocument | None = None
    if args.input_mode == "xmi":
        log(f"Loading document: {xmi_file.name}")
        load_t0 = time.time()
        doc = UIMADocument.from_xmi(xmi_file)
        log(f"Loaded document in {time.time() - load_t0:.1f}s")
        total_sentences = len(doc.sentences)
    else:
        assert txt_file is not None
        log(f"Loading TXT: {txt_file.name}")
        load_t0 = time.time()
        text_sentences = _split_txt_sentences(txt_file.read_text(encoding="utf-8"))
        log(f"Loaded TXT in {time.time() - load_t0:.1f}s")
        total_sentences = len(text_sentences)
        if total_sentences == 0:
            log(f"ERROR: No sentences parsed from {txt_file}")
            sys.exit(1)
    all_sentences: list[str]
    if args.input_mode == "xmi":
        assert doc is not None
        all_sentences = [s.text for s in doc.sentences]
    else:
        all_sentences = text_sentences
    max_sentences = max(1, min(args.max_sentences, total_sentences))
    log(f"Input has {total_sentences} sentences, classifying first {max_sentences}")

    chain = get_chain(model, prompt_text, extra_model_kwargs=model_kwargs)
    results = {
        "labels": [],
        "reasons": [],
        "compact_decisions": [],
        "ground_truth": [],
        "sentences": [],
        "parse_ok": [],
        "parse_error": [],
        "output_chars": [],
        "latency_seconds": [],
    }
    t0 = time.time()

    for i in range(max_sentences):
        if args.input_mode == "xmi":
            assert doc is not None
            sentence = doc.sentences[i]
            sent_text = sentence.text
            base_sample = build_sentence_sample(sentence, model)
            true_label = get_label_simple(sentence, coarse=True)
        else:
            sent_text = text_sentences[i]
            base_sample = _build_txt_sample(text_sentences, i)
            true_label = None

        sent_preview = sent_text[:80].replace("\n", " ")
        log(f"{progress_bar(i + 1, max_sentences)} start :: {sent_preview}")
        target_local_id: Optional[int] = None
        if prompt_family:
            if prompt_family in {"H", "I"}:
                chunk_sentences, target_local_id = _build_chunk_sentences(
                    all_sentences, i, args.chunk_window
                )
                sample = render_prompt_for_family(
                    prompt_family,
                    template_text,
                    "",
                    few_shot_examples=few_shot_examples,
                    chunk_sentences=chunk_sentences,
                )
            else:
                sample = render_prompt_for_family(
                    prompt_family,
                    template_text,
                    base_sample,
                    few_shot_examples=few_shot_examples,
                )
        else:
            sample = base_sample

        scene_change = None
        reason = ""
        parse_ok = False
        parse_error = ""
        output_chars = 0
        retry_count = 0
        sent_t0 = time.time()
        while scene_change is None and retry_count < args.max_retries:
            active_sample = sample
            if retry_count >= 2:
                active_sample = sample + _strict_suffix_for_family(prompt_family)
            try:
                response = chain(active_sample)
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "rate" in err_str.lower():
                    wait = min(args.max_wait, 5 * (retry_count + 1))
                    log(f"  [rate limit] retry={retry_count+1}, waiting {wait}s")
                    time.sleep(wait)
                    retry_count += 1
                    continue
                else:
                    log(f"  [error] retry={retry_count+1} {err_str[:120]}")
                    retry_count += 1
                    continue
            chain.memory.chat_memory.messages = chain.memory.chat_memory.messages[:-2]
            text = response["text"]
            output_chars = len(text)
            if prompt_family:
                parsed = parse_family_output(prompt_family, text)
                parse_ok = parsed.is_valid
                parse_error = parsed.error
                reason = text
                if parsed.label in ("BORDER", "NOBORDER"):
                    scene_change = parsed.label == "BORDER"
                elif prompt_family in {"H", "I"} and parsed.is_valid:
                    inferred, infer_error = _infer_chunk_family_label(
                        prompt_family,
                        parsed.payload,
                        target_local_id=target_local_id if target_local_id is not None else 1,
                        score_threshold=args.score_threshold,
                    )
                    if inferred is not None and not infer_error:
                        scene_change = inferred
                        parse_ok = True
                        parse_error = ""
                    else:
                        scene_change = None
                        parse_ok = False
                        parse_error = infer_error or "chunk_inference_failed"
                else:
                    scene_change = None
            else:
                scene_change, reason = parse_response(text, args.prompt)
                parse_ok = scene_change is not None
                parse_error = "" if parse_ok else "parse_response_none"
                if scene_change is None:
                    loose = parse_response_loose(text)
                    if loose is not None:
                        scene_change = loose
                        parse_ok = True
                        parse_error = ""
            if scene_change is None:
                retry_count += 1
                first_line = text.split("\n")[0]
                log(f"  [retry {retry_count}] invalid response: {first_line[:80]}")

        if scene_change is None:
            scene_change = False
            reason = "FAILED_TO_CLASSIFY"
            parse_ok = False
            if not parse_error:
                parse_error = "failed_to_classify"

        pred_str = "BORDER" if scene_change else "NOBORDER"
        if true_label is None:
            log(f"{progress_bar(i + 1, max_sentences)} done pred={pred_str} "
                f"(elapsed {time.time() - sent_t0:.1f}s)")
            true_str = None
        else:
            true_str = true_label.value
            match = "OK" if pred_str == true_str else "MISMATCH"
            log(f"{progress_bar(i + 1, max_sentences)} done pred={pred_str} true={true_str} {match} "
                f"(elapsed {time.time() - sent_t0:.1f}s)")

        results["labels"].append(scene_change)
        results["reasons"].append(reason)
        results["compact_decisions"].append(_compact_decision(reason))
        results["ground_truth"].append(true_str)
        results["sentences"].append(sent_text)
        results["parse_ok"].append(parse_ok)
        results["parse_error"].append(parse_error)
        results["output_chars"].append(output_chars)
        results["latency_seconds"].append(round(time.time() - sent_t0, 4))

    elapsed = time.time() - t0

    has_gold = all(t in {"BORDER", "NOBORDER"} for t in results["ground_truth"])
    n_correct = 0
    n_borders_true = 0
    if has_gold:
        n_correct = sum(1 for p, t in zip(results["labels"], results["ground_truth"])
                        if (p and t == "BORDER") or (not p and t == "NOBORDER"))
        n_borders_true = sum(1 for t in results["ground_truth"] if t == "BORDER")
    n_borders_pred = sum(1 for p in results["labels"] if p)
    parse_failure_count = sum(1 for ok in results["parse_ok"] if not ok)
    parse_failure_rate = parse_failure_count / len(results["parse_ok"]) if results["parse_ok"] else 0.0
    avg_output_chars = (
        sum(float(x) for x in results["output_chars"]) / len(results["output_chars"])
        if results["output_chars"] else 0.0
    )
    avg_latency_seconds = (
        sum(float(x) for x in results["latency_seconds"]) / len(results["latency_seconds"])
        if results["latency_seconds"] else 0.0
    )

    input_file_name = xmi_file.name if args.input_mode == "xmi" else (txt_file.name if txt_file else "")
    summary: dict[str, Any] = {
        "input_mode": args.input_mode,
        "evaluation_mode": "with_gold" if has_gold else "inference_only",
        "model": model.name,
        "provider": "openrouter",
        "prompt_family": prompt_family,
        "prompt_mode": args.prompt,
        "reasoning": args.reasoning,
        "decode": {
            "temperature": args.temperature,
            "top_p": args.top_p,
            "top_k": args.top_k,
            "min_p": args.min_p,
            "seed": args.seed,
            "max_tokens": args.max_tokens,
            "stop": args.stop,
            "response_format": args.response_format,
            "response_format_effective": effective_response_format,
        },
        "file": input_file_name,
        "total_sentences_in_doc": total_sentences,
        "sentences_classified": len(results["labels"]),
        "predicted_borders": n_borders_pred,
        "parse_failure_count": parse_failure_count,
        "parse_failure_rate": round(parse_failure_rate, 4),
        "avg_output_chars": round(avg_output_chars, 2),
        "avg_latency_seconds": round(avg_latency_seconds, 3),
        "elapsed_seconds": round(elapsed, 1),
    }
    if has_gold:
        summary["accuracy"] = n_correct / len(results["labels"]) if results["labels"] else 0
        summary["true_borders"] = n_borders_true

    results_path = out_dir / "results.json"
    results_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    summary_path = out_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    review_schema_path = out_dir / "review_schema.json"
    review_schema_path.write_text(json.dumps(_review_schema(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    review_jsonl_path = out_dir / "review.jsonl"
    with review_jsonl_path.open("w", encoding="utf-8") as handle:
        for idx in range(len(results["labels"])):
            pred_bool = bool(results["labels"][idx])
            record = {
                "sentence_index": idx,
                "sentence_text_full": results["sentences"][idx],
                "prediction_label": "BORDER" if pred_bool else "NOBORDER",
                "prediction_bool": pred_bool,
                "ground_truth_label": results["ground_truth"][idx],
                "parse_ok": bool(results["parse_ok"][idx]),
                "parse_error": results["parse_error"][idx],
                "compact_decision": results["compact_decisions"][idx],
                "raw_model_response": results["reasons"][idx],
                "latency_seconds": float(results["latency_seconds"][idx]),
                "output_chars": int(results["output_chars"][idx]),
                "input_mode": args.input_mode,
                "prompt_mode": args.prompt,
                "prompt_family": prompt_family,
                "model": model.name,
                "source_file": input_file_name,
            }
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    log(f"Done in {elapsed:.1f}s")
    if has_gold:
        log(f"Accuracy: {summary['accuracy']:.2%} ({n_correct}/{len(results['labels'])})")
        log(f"True borders: {n_borders_true}, Predicted borders: {n_borders_pred}")
    else:
        log(f"Inference-only mode: predicted borders={n_borders_pred}/{len(results['labels'])}")
    log(
        f"Parse failures: {parse_failure_count}/{len(results['labels'])} "
        f"({parse_failure_rate:.1%}), avg chars={avg_output_chars:.1f}, "
        f"avg latency={avg_latency_seconds:.2f}s"
    )
    log(f"Results: {results_path}")
    log(f"Summary: {summary_path}")
    log(f"Review JSONL: {review_jsonl_path}")
    log(f"Review schema: {review_schema_path}")


if __name__ == "__main__":
    main()
