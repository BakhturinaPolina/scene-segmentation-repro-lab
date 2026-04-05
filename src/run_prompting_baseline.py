"""Minimal prompting baseline runner for Phase 3.2.

Uses OpenRouter with qwen/qwen3-235b-a22b:free to classify scene boundaries
on a small subset of sentences from an XMI file.

Run from project root:
    OPENROUTER_API_KEY=sk-or-... python src/run_prompting_baseline.py
"""
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "upstream" / "scene-segmentation"))

from wuenlp.impl.UIMANLPStructs import UIMADocument
from prompting.classify import (
    build_sentence_sample, get_chain, qwen3_plus, prompt_classify
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


def main():
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key or api_key == "Your OpenRouter API Key":
        print("ERROR: Set OPENROUTER_API_KEY environment variable")
        sys.exit(1)

    xmi_file = DATA_DIR / "Aus guter Familie.xmi.zip"
    if not xmi_file.exists():
        print(f"ERROR: File not found: {xmi_file}")
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Loading document: {xmi_file.name}")
    doc = UIMADocument.from_xmi(xmi_file)
    total_sentences = len(doc.sentences)
    print(f"Document has {total_sentences} sentences, classifying first {MAX_SENTENCES}")

    chain = get_chain(qwen3_plus, prompt_classify)
    results = {"labels": [], "reasons": [], "ground_truth": [], "sentences": []}
    t0 = time.time()

    for i, sentence in enumerate(doc.sentences[:MAX_SENTENCES]):
        sample = build_sentence_sample(sentence, qwen3_plus)
        true_label = get_label_simple(sentence, coarse=True)

        scene_change = None
        retry_count = 0
        while scene_change is None and retry_count < 10:
            try:
                response = chain(sample)
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "rate" in err_str.lower():
                    wait = min(30, 5 * (retry_count + 1))
                    print(f"  [rate limit] waiting {wait}s...")
                    time.sleep(wait)
                    retry_count += 1
                    continue
                else:
                    print(f"  [error] {err_str[:120]}")
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
                print(f"  [retry {retry_count}] invalid response: {lines[0][:80]}")

        if scene_change is None:
            scene_change = False
            reason = "FAILED_TO_CLASSIFY"

        pred_str = "BORDER" if scene_change else "NOBORDER"
        true_str = true_label.value
        match = "OK" if pred_str == true_str else "MISMATCH"
        print(f"  [{i+1}/{MAX_SENTENCES}] pred={pred_str} true={true_str} {match}")

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
        "model": "qwen/qwen3.6-plus:free",
        "provider": "openrouter",
        "file": xmi_file.name,
        "total_sentences_in_doc": total_sentences,
        "sentences_classified": len(results["labels"]),
        "accuracy": n_correct / len(results["labels"]) if results["labels"] else 0,
        "true_borders": n_borders_true,
        "predicted_borders": n_borders_pred,
        "elapsed_seconds": round(elapsed, 1),
    }

    results_path = OUTPUT_DIR / "results.json"
    results_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    summary_path = OUTPUT_DIR / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))

    print(f"\nDone in {elapsed:.1f}s")
    print(f"Accuracy: {summary['accuracy']:.2%} ({n_correct}/{len(results['labels'])})")
    print(f"True borders: {n_borders_true}, Predicted borders: {n_borders_pred}")
    print(f"Results: {results_path}")
    print(f"Summary: {summary_path}")


if __name__ == "__main__":
    main()
