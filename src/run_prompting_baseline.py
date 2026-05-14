"""Minimal prompting baseline runner for Phase 3.2.

Uses OpenRouter with nvidia/nemotron-3-super-120b-a12b:free to classify scene
boundaries on a small subset of sentences from an XMI file.

Run from project root:
    OPENROUTER_API_KEY=sk-or-... python src/run_prompting_baseline.py

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
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "upstream" / "scene-segmentation"))

from wuenlp.impl.UIMANLPStructs import UIMADocument
from prompting.classify import (
    build_sentence_sample, get_chain, nemotron, prompt_classify, prompt_classify_cot, Model
)
from utils.constants import Label, SCENE_TYPES, NONSCENE_TYPES
from prompt_runtime import (
    PROMPT_FAMILIES,
    build_openrouter_model_kwargs,
    get_template_text,
    load_prompt_registry,
    parse_family_output,
    render_prompt_for_family,
)
from workflow_runtime import output_dir_for, project_root, stss_test2_data_dir, write_repro_files


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
                        default=Path(__file__).resolve().parent / "prompts",
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
    args = parser.parse_args()

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key or api_key == "Your OpenRouter API Key":
        log("ERROR: Set OPENROUTER_API_KEY environment variable")
        sys.exit(1)

    xmi_file = DATA_DIR / "Aus guter Familie.xmi.zip"
    if not xmi_file.exists():
        log(f"ERROR: File not found: {xmi_file}")
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
        if prompt_family in {"H", "I"}:
            log("ERROR: Families H/I are chunk-level and not supported in sentence-wise baseline runner yet.")
            sys.exit(1)
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

    run_date = datetime.now().date().isoformat()
    out_dir = args.output_dir or output_dir_for(ROOT_DIR, "prompting", run_date, "baseline_qwen3")
    out_dir.mkdir(parents=True, exist_ok=True)
    run_config = {
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
        "schema_file": str(args.schema_file) if args.schema_file else None,
        "output_dir": str(out_dir),
        "data_file": str(DATA_DIR / "Aus guter Familie.xmi.zip"),
    }
    write_repro_files(out_dir, sys.argv, run_config)
    log(f"Model: {model.name}")
    log(f"Context size: {model.context_size} tokens")
    log(f"Prompt: {args.prompt}")
    if prompt_family:
        log(f"Prompt family: {prompt_family}")
    log(f"Reasoning: {args.reasoning}")
    log(f"Decode: temp={args.temperature}, top_p={args.top_p}, max_tokens={args.max_tokens}")
    log(f"Output dir: {out_dir}")

    log(f"Loading document: {xmi_file.name}")
    load_t0 = time.time()
    doc = UIMADocument.from_xmi(xmi_file)
    log(f"Loaded document in {time.time() - load_t0:.1f}s")
    total_sentences = len(doc.sentences)
    max_sentences = max(1, min(args.max_sentences, total_sentences))
    log(f"Document has {total_sentences} sentences, classifying first {max_sentences}")

    chain = get_chain(model, prompt_text, extra_model_kwargs=model_kwargs)
    results = {
        "labels": [],
        "reasons": [],
        "ground_truth": [],
        "sentences": [],
        "parse_ok": [],
        "parse_error": [],
        "output_chars": [],
        "latency_seconds": [],
    }
    t0 = time.time()

    for i, sentence in enumerate(doc.sentences[:max_sentences]):
        sent_preview = sentence.text[:80].replace("\n", " ")
        log(f"{progress_bar(i + 1, max_sentences)} start :: {sent_preview}")
        base_sample = build_sentence_sample(sentence, model)
        if prompt_family:
            sample = render_prompt_for_family(
                prompt_family,
                template_text,
                base_sample,
                few_shot_examples=few_shot_examples,
            )
        else:
            sample = base_sample
        true_label = get_label_simple(sentence, coarse=True)

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
                active_sample = sample + _STRICT_SUFFIX
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
        true_str = true_label.value
        match = "OK" if pred_str == true_str else "MISMATCH"
        log(f"{progress_bar(i + 1, max_sentences)} done pred={pred_str} true={true_str} {match} "
            f"(elapsed {time.time() - sent_t0:.1f}s)")

        results["labels"].append(scene_change)
        results["reasons"].append(reason)
        results["ground_truth"].append(true_str)
        results["sentences"].append(sentence.text[:100])
        results["parse_ok"].append(parse_ok)
        results["parse_error"].append(parse_error)
        results["output_chars"].append(output_chars)
        results["latency_seconds"].append(round(time.time() - sent_t0, 4))

    elapsed = time.time() - t0

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

    summary = {
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
        },
        "file": xmi_file.name,
        "total_sentences_in_doc": total_sentences,
        "sentences_classified": len(results["labels"]),
        "accuracy": n_correct / len(results["labels"]) if results["labels"] else 0,
        "true_borders": n_borders_true,
        "predicted_borders": n_borders_pred,
        "parse_failure_count": parse_failure_count,
        "parse_failure_rate": round(parse_failure_rate, 4),
        "avg_output_chars": round(avg_output_chars, 2),
        "avg_latency_seconds": round(avg_latency_seconds, 3),
        "elapsed_seconds": round(elapsed, 1),
    }

    results_path = out_dir / "results.json"
    results_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    summary_path = out_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))

    log(f"Done in {elapsed:.1f}s")
    log(f"Accuracy: {summary['accuracy']:.2%} ({n_correct}/{len(results['labels'])})")
    log(
        f"Parse failures: {parse_failure_count}/{len(results['labels'])} "
        f"({parse_failure_rate:.1%}), avg chars={avg_output_chars:.1f}, "
        f"avg latency={avg_latency_seconds:.2f}s"
    )
    log(f"True borders: {n_borders_true}, Predicted borders: {n_borders_pred}")
    log(f"Results: {results_path}")
    log(f"Summary: {summary_path}")


if __name__ == "__main__":
    main()
