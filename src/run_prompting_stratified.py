"""Stratified prompting evaluation on full corpus.

Classifies a stratified sample (all BORDERs + matched NOBORDERs) from each
novel in data/full/stss_test_2 using qwen/qwen3.6-plus via OpenRouter,
then computes precision/recall/F1 at tolerance 0, 1, and 3.

Supports resume: intermediate results are cached per-document so the run can
be interrupted and restarted without losing progress.

Run from project root:
    OPENROUTER_API_KEY=sk-or-... python src/run_prompting_stratified.py

Options:
    --max_per_class N   Max BORDER (and NOBORDER) sentences per novel (0 = all)
    --dry_run N         Classify only N sentences total then stop (for testing)
    --date YYYY-MM-DD   Override the output date folder (default: today)
    --prompt {no-cot,cot-list}  Prompt style (default: no-cot)
    --reasoning {on,off}        Model-level thinking (default: on)
"""
import argparse
import json
import os
import random
import re
import sys
import time
from datetime import date, datetime
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "upstream" / "scene-segmentation"))

from wuenlp.impl.UIMANLPStructs import UIMADocument, UIMAScene, UIMASentence
from prompting.classify import (
    build_sentence_sample, get_chain, Model, prompt_classify, prompt_classify_cot,
)
from utils.constants import Label
from prompt_runtime import (
    PROMPT_FAMILIES,
    build_openrouter_model_kwargs,
    get_template_text,
    load_prompt_registry,
    parse_family_output,
    render_prompt_for_family,
)

DEFAULT_MODEL = Model("qwen/qwen3.6-plus", int(512 * 0.8), json=False, openai=False, openrouter=True)

DATA_DIR = Path(__file__).resolve().parent.parent / "upstream" / "scene-segmentation" / "data" / "full" / "stss_test_2"
SEED = 1337


def log(msg):
    """Timestamped, unbuffered terminal logging."""
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


_ANSWER_YES_RE = re.compile(r"\bAnswer\s*:\s*Yes\b", re.IGNORECASE)
_ANSWER_NO_RE = re.compile(r"\bAnswer\s*:\s*No\b", re.IGNORECASE)
_NOT_START_RE = re.compile(
    r"\b(?:does\s+(?:\*{0,2})not(?:\*{0,2})|doesn't)\s+"
    r"(?:start|introduce|mark\b)", re.IGNORECASE)
_STARTS_RE = re.compile(
    r"\b(?:starts?|introduces?|marks?)\s+(?:a\s+new\s+scene|the\s+beginning)",
    re.IGNORECASE)


def parse_response(text, prompt_mode):
    """Return (scene_change: bool|None, reason: str) from model output."""
    if prompt_mode == "cot-list":
        if _ANSWER_NO_RE.search(text):
            return False, text
        if _ANSWER_YES_RE.search(text):
            return True, text
        if _NOT_START_RE.search(text):
            return False, text
        if _STARTS_RE.search(text):
            return True, text
    first_line = text.split("\n")[0]
    if "True" in first_line:
        return True, text
    if "False" in first_line:
        return False, text
    if first_line.strip().startswith("Yes"):
        return True, text
    if first_line.strip().startswith("No"):
        return False, text
    return None, text


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

    for count, (orig_idx, sentence, gold) in enumerate(sample):
        if count >= total:
            break
        key = str(orig_idx)
        if key in cache:
            log(f"  [{count+1}/{total}] idx={orig_idx} already cached, skipping")
            continue

        sent_preview = sentence.text[:80].replace("\n", " ")
        log(f"  [{count+1}/{total}] idx={orig_idx} start (gold={gold}) :: {sent_preview}")
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
        scene_change = None
        reason = ""
        parse_ok = False
        parse_error = ""
        output_chars = 0
        retry_count = 0
        sent_t0 = time.time()

        while scene_change is None and retry_count < 15:
            try:
                response = chain(text_sample)
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "rate" in err_str.lower():
                    wait = min(60, 5 * (2 ** retry_count))
                    log(f"  [rate limit] idx={orig_idx} retry={retry_count+1} waiting {wait}s")
                    time.sleep(wait)
                    retry_count += 1
                    continue
                else:
                    log(f"  [error] idx={orig_idx} retry={retry_count+1} {err_str[:120]}")
                    retry_count += 1
                    time.sleep(2)
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
                    scene_change = None
            else:
                scene_change, reason = parse_response(text, prompt_mode)
                parse_ok = scene_change is not None
                parse_error = "" if parse_ok else "parse_response_none"
            if scene_change is None:
                retry_count += 1
                first_line = text.split("\n")[0]
                log(f"  [retry {retry_count}] idx={orig_idx} invalid response: {first_line[:80]}")
                time.sleep(1)

        if scene_change is None:
            scene_change = False
            reason = "FAILED_TO_CLASSIFY"
            parse_ok = False
            if not parse_error:
                parse_error = "failed_to_classify"

        pred_str = "BORDER" if scene_change else "NOBORDER"
        match = "OK" if pred_str == gold else "MISS"
        log(
            f"  [{count+1}/{total}] idx={orig_idx} done "
            f"pred={pred_str} gold={gold} {match} "
            f"(elapsed {time.time() - sent_t0:.1f}s)"
        )

        cache[key] = {
            "pred": pred_str,
            "reason": reason,
            "gold": gold,
            "sentence": sentence.text[:200],
            "parse_ok": parse_ok,
            "parse_error": parse_error,
            "output_chars": output_chars,
            "latency_seconds": round(time.time() - sent_t0, 4),
            "chunk_target_local_id": target_local_id,
        }

        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
        log(f"  [{count+1}/{total}] checkpoint saved ({len(cache)} cached)")

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
                        help="OpenRouter model name (default: qwen/qwen3.6-plus)")
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
    output_dir = (Path(__file__).resolve().parent.parent
                  / "outputs" / "prompting" / run_date
                  / f"{mode_tag}_{model_slug}_{prompt_tag}_{reasoning_tag}")
    output_dir.mkdir(parents=True, exist_ok=True)
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
    log(f"Output: {output_dir}")

    xmi_files = sorted(DATA_DIR.glob("*.xmi.zip"))
    if not xmi_files:
        log(f"ERROR: No .xmi.zip files in {DATA_DIR}")
        sys.exit(1)

    all_doc_results = {}

    for xmi_path in xmi_files:
        stem = xmi_path.name.replace(".xmi.zip", "")
        log(f"{'='*60}")
        log(f"Document: {stem}")
        log(f"{'='*60}")
        log(f"Loading XMI: {xmi_path}")

        doc_t0 = time.time()
        doc = UIMADocument.from_xmi(xmi_path)
        log(f"Loaded XMI in {time.time() - doc_t0:.1f}s")
        sentences = list(doc.sentences)
        total_sents = len(sentences)

        full_gold = [get_label_simple(s, coarse=True).value for s in sentences]
        n_gold_borders = sum(1 for g in full_gold if g == "BORDER")

        if args.full_eval:
            sample = build_full_sample(doc)
        else:
            sample = build_stratified_sample(doc, args.seed, max_per_class=args.max_per_class)
        n_border_sampled = sum(1 for _, _, g in sample if g == "BORDER")
        n_noborder_sampled = sum(1 for _, _, g in sample if g == "NOBORDER")

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
                                score_threshold=args.score_threshold)

        sampled_indices = []
        sampled_preds = []
        sampled_golds = []
        reasons = []
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
            "file": xmi_path.name,
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
            "file": xmi_path.name,
            "original_indices": sampled_indices,
            "labels": [p == "BORDER" for p in sampled_preds],
            "predictions": sampled_preds,
            "ground_truth": sampled_golds,
            "reasons": reasons,
            "sentences": sent_texts,
            "parse_ok": parse_flags,
            "parse_error": parse_errors,
            "output_chars": output_chars_list,
            "latency_seconds": latencies,
            "metrics": metrics,
        }
        results_path.write_text(json.dumps(results_data, indent=2, ensure_ascii=False))

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
