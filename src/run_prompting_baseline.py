"""Minimal prompting baseline runner for Phase 3.2.

Uses OpenRouter with qwen/qwen3-235b-a22b:free to classify scene boundaries
on a small subset of sentences from an XMI file.

Run from project root:
    OPENROUTER_API_KEY=sk-or-... python src/run_prompting_baseline.py
"""
import json
import argparse
import os
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "upstream" / "scene-segmentation"))

from wuenlp.impl.UIMANLPStructs import UIMADocument
from prompting.classify import (
    build_sentence_sample, get_chain, qwen3_plus, prompt_classify, Model
)
from utils.constants import Label, SCENE_TYPES, NONSCENE_TYPES


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

DATA_DIR = Path(__file__).resolve().parent.parent / "upstream" / "scene-segmentation" / "data" / "full" / "stss_test_2"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs" / "prompting" / "2026-04-05" / "baseline_qwen3"

MAX_SENTENCES = 20


def log(msg):
    """Timestamped, unbuffered terminal logging."""
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


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
    args = parser.parse_args()

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key or api_key == "Your OpenRouter API Key":
        log("ERROR: Set OPENROUTER_API_KEY environment variable")
        sys.exit(1)

    xmi_file = DATA_DIR / "Aus guter Familie.xmi.zip"
    if not xmi_file.exists():
        log(f"ERROR: File not found: {xmi_file}")
        sys.exit(1)

    model = qwen3_plus
    if args.model:
        model = Model(args.model, int(512 * 0.8), json=False, openai=False, openrouter=True)
    out_dir = args.output_dir or OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    log(f"Model: {model.name}")
    log(f"Output dir: {out_dir}")

    log(f"Loading document: {xmi_file.name}")
    load_t0 = time.time()
    doc = UIMADocument.from_xmi(xmi_file)
    log(f"Loaded document in {time.time() - load_t0:.1f}s")
    total_sentences = len(doc.sentences)
    max_sentences = max(1, min(args.max_sentences, total_sentences))
    log(f"Document has {total_sentences} sentences, classifying first {max_sentences}")

    chain = get_chain(model, prompt_classify)
    results = {"labels": [], "reasons": [], "ground_truth": [], "sentences": []}
    t0 = time.time()

    for i, sentence in enumerate(doc.sentences[:max_sentences]):
        sent_preview = sentence.text[:80].replace("\n", " ")
        log(f"  [{i+1}/{max_sentences}] start :: {sent_preview}")
        sample = build_sentence_sample(sentence, model)
        true_label = get_label_simple(sentence, coarse=True)

        scene_change = None
        retry_count = 0
        sent_t0 = time.time()
        while scene_change is None and retry_count < args.max_retries:
            try:
                response = chain(sample)
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
            lines = text.split("\n")
            if "True" in lines[0]:
                scene_change = True
                reason = text
            elif "False" in lines[0]:
                scene_change = False
                reason = text
            else:
                retry_count += 1
                log(f"  [retry {retry_count}] invalid response: {lines[0][:80]}")

        if scene_change is None:
            scene_change = False
            reason = "FAILED_TO_CLASSIFY"

        pred_str = "BORDER" if scene_change else "NOBORDER"
        true_str = true_label.value
        match = "OK" if pred_str == true_str else "MISMATCH"
        log(
            f"  [{i+1}/{max_sentences}] done pred={pred_str} true={true_str} {match} "
            f"(elapsed {time.time() - sent_t0:.1f}s)"
        )

        results["labels"].append(scene_change)
        results["reasons"].append(reason)
        results["ground_truth"].append(true_str)
        results["sentences"].append(sentence.text[:100])

    elapsed = time.time() - t0

    n_correct = sum(1 for p, t in zip(results["labels"], results["ground_truth"])
                    if (p and t == "BORDER") or (not p and t == "NOBORDER"))
    n_borders_true = sum(1 for t in results["ground_truth"] if t == "BORDER")
    n_borders_pred = sum(1 for p in results["labels"] if p)

    summary = {
        "model": model.name,
        "provider": "openrouter",
        "file": xmi_file.name,
        "total_sentences_in_doc": total_sentences,
        "sentences_classified": len(results["labels"]),
        "accuracy": n_correct / len(results["labels"]) if results["labels"] else 0,
        "true_borders": n_borders_true,
        "predicted_borders": n_borders_pred,
        "elapsed_seconds": round(elapsed, 1),
    }

    results_path = out_dir / "results.json"
    results_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    summary_path = out_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))

    log(f"Done in {elapsed:.1f}s")
    log(f"Accuracy: {summary['accuracy']:.2%} ({n_correct}/{len(results['labels'])})")
    log(f"True borders: {n_borders_true}, Predicted borders: {n_borders_pred}")
    log(f"Results: {results_path}")
    log(f"Summary: {summary_path}")


if __name__ == "__main__":
    main()
