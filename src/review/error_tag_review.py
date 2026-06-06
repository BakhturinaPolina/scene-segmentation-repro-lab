"""Tag false positives and false negatives in stratified-runner review files.

Reads one or more ``review_<doc>.jsonl`` files (as emitted by
``src/runners/run_prompting_stratified.py``) and tags each FP/FN with one of the
§5.2 error categories:

    - near_correct_boundary  : FP or FN within ``--tolerance`` sentence
      positions of an opposite-side label in the SAMPLED set; treated as
      "early/late but near-correct boundary".
    - implicit_shift_fn      : FN with NO near predicted BORDER in the
      sampled set; the model failed to detect an implicit/subtle shift.
    - minor_shift_fp         : FP whose ``raw_model_response`` (or
      ``compact_decision``) cites at least one shift cue keyword
      (time / location / character / action). Read as "model saw a
      surface cue the gold thinks is not strong enough".
    - non_scene_confusion_fp : FP with no near gold BORDER and no shift
      cue keyword in the model rationale.

Outputs:
    - ``error_tags_<doc>.jsonl`` per input ``review_<doc>.jsonl``
      (one tagged record per FP or FN; TPs and TNs are omitted).
    - ``error_tags_summary.json`` aggregated counts per tag, per doc and
      across all docs.

Run from project root, pointing at the per-(model, family) output dir::

    python src/review/error_tag_review.py \
        --review_dir outputs/runs/prompting/2026-05-15-phaseC-baselineB-full/strat_nvidia_nemotron-3-super-120b-a12b_free_familyB_reasoning-low \
        --tolerance 3
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

# Bilingual cue keywords. EN/DE chosen to cover STSS-Test-2 (DE corpus) and
# any future EN runs. Words are matched case-insensitively as whole tokens.
SHIFT_CUE_KEYWORDS = {
    "time": [
        "time", "earlier", "later", "next day", "next morning", "afterward",
        "afterwards", "meanwhile", "subsequent",
        "zeit", "spaeter", "später", "danach", "morgens", "abends",
        "nachts", "tagsspaeter", "tags spaeter", "tags später",
        "naechsten tag", "nächsten tag", "danach",
    ],
    "location": [
        "location", "place", "scene shifts", "scene moves", "moved to",
        "elsewhere", "outside", "inside",
        "ort", "raum", "bewegt sich nach", "geht zu", "draussen",
        "draußen", "drinnen",
    ],
    "character": [
        "character", "new character", "introduces", "joined by",
        "figuren", "figur", "neue figur", "tritt auf", "kommt herein",
    ],
    "action": [
        "action", "new event", "begins to", "starts to",
        "handlung", "neues ereignis", "beginnt zu", "faengt an",
        "fängt an",
    ],
}


def detect_shift_cues(text: str) -> list[str]:
    """Return the list of cue categories whose keywords appear in ``text``."""
    if not text:
        return []
    lo = text.lower()
    cues = []
    for category, kws in SHIFT_CUE_KEYWORDS.items():
        for kw in kws:
            # Whole-word match for short tokens; substring for multiword phrases.
            if " " in kw:
                if kw in lo:
                    cues.append(category)
                    break
            else:
                if re.search(r"\b" + re.escape(kw) + r"\b", lo):
                    cues.append(category)
                    break
    return cues


def load_review(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def tag_doc(rows: list[dict], tolerance: int) -> tuple[list[dict], Counter]:
    """Return (tagged_records, tag_counter) for a single document.

    Records are sorted by ``sentence_index``. Near-neighbour checks operate on
    the SAMPLED set only (matches the runner's ``evaluate_sampled`` semantics).
    """
    rows_sorted = sorted(rows, key=lambda r: r.get("sentence_index", 0))
    indices = [r["sentence_index"] for r in rows_sorted]
    by_idx = {r["sentence_index"]: r for r in rows_sorted}

    pred_border = {r["sentence_index"] for r in rows_sorted if r.get("prediction_label") == "BORDER"}
    gold_border = {r["sentence_index"] for r in rows_sorted if r.get("ground_truth_label") == "BORDER"}

    def has_neighbour(target_idx: int, candidate_set: set[int]) -> bool:
        for idx in candidate_set:
            if idx == target_idx:
                continue
            # Neighbour over the SAMPLED set: count the number of sampled
            # positions between them, not raw sentence-index distance, since
            # stratified samples can be very sparse.
            try:
                pos_t = indices.index(target_idx)
                pos_i = indices.index(idx)
            except ValueError:
                continue
            if abs(pos_t - pos_i) <= tolerance:
                return True
        return False

    tagged = []
    counter: Counter = Counter()

    for r in rows_sorted:
        pred = r.get("prediction_label")
        gold = r.get("ground_truth_label")
        if pred == gold:
            continue  # TP and TN are not error-tagged.

        idx = r["sentence_index"]
        rationale = (r.get("raw_model_response") or "") + " \n" + (r.get("compact_decision") or "")

        if pred == "BORDER" and gold == "NOBORDER":
            kind = "FP"
            if has_neighbour(idx, gold_border):
                tag = "near_correct_boundary"
            else:
                cues = detect_shift_cues(rationale)
                if cues:
                    tag = "minor_shift_fp"
                else:
                    tag = "non_scene_confusion_fp"
        elif pred == "NOBORDER" and gold == "BORDER":
            kind = "FN"
            if has_neighbour(idx, pred_border):
                tag = "near_correct_boundary"
            else:
                tag = "implicit_shift_fn"
        else:
            # Predictions that are neither BORDER nor NOBORDER would have been
            # marked failed_to_classify by the runner (defaulting to NOBORDER).
            continue

        cues_present = detect_shift_cues(rationale)
        tagged.append({
            "sentence_index": idx,
            "kind": kind,
            "tag": tag,
            "shift_cues_in_rationale": cues_present,
            "prediction_label": pred,
            "ground_truth_label": gold,
            "compact_decision": r.get("compact_decision", ""),
            "sentence_text_preview": (r.get("sentence_text_full") or "")[:160].replace("\n", " "),
        })
        counter[tag] += 1
        counter[f"_{kind}_total"] += 1

    return tagged, counter


def aggregate(per_doc: dict[str, Counter]) -> dict:
    total: Counter = Counter()
    for c in per_doc.values():
        total.update(c)
    return {
        "per_doc": {k: dict(v) for k, v in per_doc.items()},
        "across_docs": dict(total),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--review_dir", type=Path, required=True,
                        help="Per-(model,family) output dir containing review_*.jsonl")
    parser.add_argument("--tolerance", type=int, default=3,
                        help="Sample-position window for near-neighbour check (default: 3)")
    args = parser.parse_args()

    review_files = sorted(args.review_dir.glob("review_*.jsonl"))
    if not review_files:
        raise SystemExit(f"No review_*.jsonl files in {args.review_dir}")

    per_doc: dict[str, Counter] = {}
    for rp in review_files:
        doc = rp.stem.replace("review_", "")
        rows = load_review(rp)
        if not rows:
            continue
        tagged, counter = tag_doc(rows, args.tolerance)
        out_path = args.review_dir / f"error_tags_{doc}.jsonl"
        with out_path.open("w", encoding="utf-8") as handle:
            for rec in tagged:
                handle.write(json.dumps(rec, ensure_ascii=False) + "\n")
        per_doc[doc] = counter
        print(f"  {doc}: tagged={len(tagged)}  counts={dict(counter)}")

    summary = aggregate(per_doc)
    summary_path = args.review_dir / "error_tags_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"Summary: {summary_path}")


if __name__ == "__main__":
    main()
