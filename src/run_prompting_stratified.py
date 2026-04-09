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
"""
import argparse
import json
import os
import random
import sys
import time
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "upstream" / "scene-segmentation"))

from wuenlp.impl.UIMANLPStructs import UIMADocument, UIMAScene, UIMASentence
from prompting.classify import build_sentence_sample, get_chain, Model, prompt_classify
from utils.constants import Label

DEFAULT_MODEL = Model("qwen/qwen3.6-plus", int(512 * 0.8), json=False, openai=False, openrouter=True)

DATA_DIR = Path(__file__).resolve().parent.parent / "upstream" / "scene-segmentation" / "data" / "full" / "stss_test_2"
SEED = 1337


def log(msg):
    """Timestamped, unbuffered terminal logging."""
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


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

def classify_sample(sample, doc, chain, model, cache_path, dry_run=0):
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

    for count, (orig_idx, sentence, gold) in enumerate(sample):
        if count >= total:
            break
        key = str(orig_idx)
        if key in cache:
            log(f"  [{count+1}/{total}] idx={orig_idx} already cached, skipping")
            continue

        sent_preview = sentence.text[:80].replace("\n", " ")
        log(f"  [{count+1}/{total}] idx={orig_idx} start (gold={gold}) :: {sent_preview}")
        text_sample = build_sentence_sample(sentence, model)
        scene_change = None
        reason = ""
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
            first_line = text.split("\n")[0]
            if "True" in first_line:
                scene_change = True
                reason = text
            elif "False" in first_line:
                scene_change = False
                reason = text
            else:
                retry_count += 1
                log(f"  [retry {retry_count}] idx={orig_idx} invalid response: {first_line[:80]}")
                time.sleep(1)

        if scene_change is None:
            scene_change = False
            reason = "FAILED_TO_CLASSIFY"

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
    args = parser.parse_args()

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key or api_key == "Your OpenRouter API Key":
        log("ERROR: Set OPENROUTER_API_KEY environment variable")
        sys.exit(1)

    model = DEFAULT_MODEL
    if args.model:
        model = Model(args.model, int(512 * 0.8), json=False, openai=False, openrouter=True)

    run_date = args.date or date.today().isoformat()
    model_slug = model.name.replace("/", "_").replace(":", "_")
    output_dir = (Path(__file__).resolve().parent.parent
                  / "outputs" / "prompting" / run_date / f"stratified_{model_slug}")
    output_dir.mkdir(parents=True, exist_ok=True)
    log(f"Model: {model.name}")
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

        sample = build_stratified_sample(doc, SEED, max_per_class=args.max_per_class)
        n_border_sampled = sum(1 for _, _, g in sample if g == "BORDER")
        n_noborder_sampled = sum(1 for _, _, g in sample if g == "NOBORDER")

        log(f"  Total sentences: {total_sents}")
        log(f"  Gold borders: {n_gold_borders}")
        log(f"  Sampled: {len(sample)} ({n_border_sampled} BORDER + {n_noborder_sampled} NOBORDER)")

        cache_path = output_dir / f"cache_{stem.replace(' ', '_')}.json"
        chain = get_chain(model, prompt_classify)
        cache = classify_sample(sample, doc, chain, model, cache_path, dry_run=args.dry_run)

        sampled_indices = []
        sampled_preds = []
        sampled_golds = []
        reasons = []
        sent_texts = []

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

        n_classified = len(sampled_indices)
        n_correct = sum(1 for p, g in zip(sampled_preds, sampled_golds) if p == g)

        metrics = {}
        for tol in (0, 1, 3):
            metrics[f"tol_{tol}"] = evaluate_sampled(
                sampled_indices, sampled_preds, full_gold, tol)

        doc_result = {
            "file": xmi_path.name,
            "total_sentences": total_sents,
            "gold_borders": n_gold_borders,
            "sampled": n_classified,
            "sampled_borders": sum(1 for g in sampled_golds if g == "BORDER"),
            "sampled_noborders": sum(1 for g in sampled_golds if g == "NOBORDER"),
            "accuracy": round(n_correct / n_classified, 4) if n_classified else 0,
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
            "metrics": metrics,
        }
        results_path.write_text(json.dumps(results_data, indent=2, ensure_ascii=False))

        log(f"  Results for {stem}:")
        log(f"    Classified: {n_classified}, Accuracy: {doc_result['accuracy']:.1%}")
        for tol_key, m in metrics.items():
            log(
                f"    {tol_key}: P={m['precision']:.3f} R={m['recall']:.3f} F1={m['f1']:.3f}"
                f"  (TP={m['tp']} FP={m['fp']} FN={m['fn']})"
            )

    # Aggregate summary
    summary = {
        "model": model.name,
        "provider": "openrouter",
        "seed": SEED,
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
