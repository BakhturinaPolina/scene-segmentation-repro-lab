#!/usr/bin/env python3
"""Build leakage-safe SFT datasets for scene-boundary fine-tuning.

Sources
-------
- STSS-Test-2 XMI gold (Aus guter Familie, Effi Briest) via the pure-ElementTree
  parser in ``src/data/build_fewshot_from_stss.py`` (no GPU/wuenlp deps).
- Excel gold CSVs (Kleist, Gaensemagd) under ``data/processed/excel_prompting/``.

Leakage-safe leave-one-text-out folds (STSS-Test-2 is the paper's TEST set, so a
model is never trained and evaluated on the same novel):

- fold_A: train = Excel + Aus guter Familie ; eval = Effi Briest
- fold_B: train = Excel + Effi Briest      ; eval = Aus guter Familie

Output (per fold) under ``data/processed/finetune/<fold>/``:
- ``train.jsonl`` (NOBORDER downsampled to keep training balanced/small)
- ``eval.jsonl``  (held-out novel, full natural distribution)
- ``meta.json``   (counts, config, provenance)

Each JSONL row is TRL-SFT compatible chat format::

    {"messages": [{"role": "user", "content": <improved prompt>},
                   {"role": "assistant", "content": <CoT-List rationale + JSON label>}]}

The user turn is rendered from a precision-focused prompt template (default L,
the strict definition) so the fine-tuned model learns the SAME contract used at
inference. The assistant turn is a CoT-List-style rationale derived from gold
reason tags plus the final JSON label.

Run::

    python src/finetune/build_sft_dataset.py --fold both --context 4 --noborder_ratio 3
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

_FILE = Path(__file__).resolve()
_SRC_ROOT = _FILE.parents[1]
_PROJECT_ROOT = _FILE.parents[2]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from core.prompt_runtime import get_template_text, load_prompt_registry, render_prompt_for_family
from data.build_fewshot_from_stss import parse_xmi, unzip_xmis

REASON_TAGS = ("Zeit", "Raum", "Figuren", "Handlung")
REASON_LABELS = {
    "Zeit": "time",
    "Raum": "place",
    "Figuren": "character constellation",
    "Handlung": "action",
}

STSS_NOVELS = {
    "Aus guter Familie": "aus_guter_familie",
    "Effi Briest": "effi_briest",
}

FOLDS = {
    "fold_A": {"train_stss": ["Aus guter Familie"], "eval_stss": "Effi Briest"},
    "fold_B": {"train_stss": ["Effi Briest"], "eval_stss": "Aus guter Familie"},
}


@dataclass
class Example:
    source: str          # provenance (novel / excel file stem)
    index: int           # position within its document
    label: str           # BORDER / NOBORDER
    target_text: str
    left_context: List[str]
    right_context: List[str]
    reasons: List[str]   # gold reason tags (XMI only); empty otherwise


# ---------------------------------------------------------------------------
# Source loaders -> ordered per-document list of Example
# ---------------------------------------------------------------------------

def _context(texts: List[str], i: int, context: int) -> tuple[List[str], List[str]]:
    left = texts[max(0, i - context):i]
    right = texts[i + 1: i + 1 + context]
    return left, right


def examples_from_stss(xmi_path: Path, novel: str, context: int) -> List[Example]:
    _sofa, sentences, scenes = parse_xmi(xmi_path)
    texts = [s.text for s in sentences]
    # First sentence (by begin offset) inside each scene is a gold BORDER.
    border_idx_to_reasons: dict[int, List[str]] = {}
    for scene in scenes:
        for idx, sent in enumerate(sentences):
            if sent.begin >= scene.begin and sent.end <= scene.end:
                border_idx_to_reasons[idx] = scene.reasons
                break
    out: List[Example] = []
    for i, text in enumerate(texts):
        is_border = i in border_idx_to_reasons
        left, right = _context(texts, i, context)
        out.append(
            Example(
                source=novel,
                index=i,
                label="BORDER" if is_border else "NOBORDER",
                target_text=text,
                left_context=left,
                right_context=right,
                reasons=border_idx_to_reasons.get(i, []),
            )
        )
    return out


def examples_from_excel_gold(csv_path: Path, context: int) -> List[Example]:
    rows: List[dict] = []
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            text = str(row.get("sentence_text_full", "")).strip()
            if text:
                rows.append(row)
    texts = [str(r["sentence_text_full"]).strip() for r in rows]
    stem = csv_path.stem.replace("__gold_labels", "")
    out: List[Example] = []
    for i, row in enumerate(rows):
        label = "BORDER" if str(row.get("ground_truth_label", "")).strip().upper() == "BORDER" else "NOBORDER"
        left, right = _context(texts, i, context)
        out.append(
            Example(
                source=stem,
                index=i,
                label=label,
                target_text=texts[i],
                left_context=left,
                right_context=right,
                reasons=[],
            )
        )
    return out


# ---------------------------------------------------------------------------
# SFT formatting
# ---------------------------------------------------------------------------

def _sample_text(ex: Example) -> str:
    """Recreate the <sentence>-tagged sample string the renderer expects."""
    left = "\n".join(ex.left_context)
    right = "\n".join(ex.right_context)
    return f"{left}\n<sentence>{ex.target_text}</sentence>\n{right}".strip()


def build_user_turn(ex: Example, template_text: str, family: str) -> str:
    return render_prompt_for_family(family, template_text, _sample_text(ex))


def build_assistant_turn(ex: Example) -> str:
    """CoT-List-style rationale derived from gold, then the JSON label."""
    changed = set(ex.reasons)
    lines = ["Markers:"]
    for tag in REASON_TAGS:
        name = REASON_LABELS[tag]
        if ex.label == "BORDER":
            # When reason tags exist, mark only those as changed; otherwise mark
            # the generic case as a major change.
            state = "changed" if (not changed or tag in changed) else "unchanged"
        else:
            state = "unchanged"
        lines.append(f"- {name}: {state}")
    if ex.label == "BORDER":
        lines.append("Conclusion: a major discontinuity begins here, so this starts a new scene.")
        conf = 0.9
    else:
        lines.append("Conclusion: no major discontinuity; the situation continues.")
        conf = 0.9
    label_json = json.dumps({"label": ex.label, "confidence": conf})
    return "\n".join(lines) + "\n" + label_json


def to_messages_row(ex: Example, template_text: str, family: str) -> dict:
    return {
        "messages": [
            {"role": "user", "content": build_user_turn(ex, template_text, family)},
            {"role": "assistant", "content": build_assistant_turn(ex)},
        ],
        "label": ex.label,
        "source": ex.source,
        "index": ex.index,
    }


# ---------------------------------------------------------------------------
# Balancing
# ---------------------------------------------------------------------------

def downsample_noborder(examples: List[Example], ratio: int, seed: int) -> List[Example]:
    """Keep all BORDER, evenly subsample NOBORDER to ratio*n_border."""
    borders = [e for e in examples if e.label == "BORDER"]
    noborders = [e for e in examples if e.label == "NOBORDER"]
    if ratio <= 0 or len(noborders) <= ratio * len(borders):
        return sorted(borders + noborders, key=lambda e: (e.source, e.index))
    keep_n = ratio * len(borders)
    step = len(noborders) / keep_n
    selected = [noborders[int(i * step)] for i in range(keep_n)]
    random.Random(seed).shuffle(selected)  # only used to break ties; order re-sorted below
    return sorted(borders + selected, key=lambda e: (e.source, e.index))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def write_jsonl(rows: List[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--fold", choices=["fold_A", "fold_B", "both"], default="both")
    parser.add_argument("--family", default="L",
                        help="Prompt family used as the SFT instruction (default: L strict)")
    parser.add_argument("--context", type=int, default=4,
                        help="Sentences of context on each side (default: 4)")
    parser.add_argument("--noborder_ratio", type=int, default=3,
                        help="NOBORDER:BORDER ratio in TRAIN split (0 = keep all)")
    parser.add_argument("--seed", type=int, default=1337)
    parser.add_argument(
        "--xmi_zip_dir", type=Path,
        default=_PROJECT_ROOT / "upstream/scene-segmentation/data/full/stss_test_2",
    )
    parser.add_argument(
        "--excel_dir", type=Path,
        default=_PROJECT_ROOT / "data/processed/excel_prompting",
    )
    parser.add_argument(
        "--out_dir", type=Path,
        default=_PROJECT_ROOT / "data/processed/finetune",
    )
    parser.add_argument("--prompts_dir", type=Path, default=_SRC_ROOT / "prompts")
    args = parser.parse_args()

    registry = load_prompt_registry(args.prompts_dir)
    template_text = get_template_text(args.prompts_dir, args.family, registry)

    # Load Excel gold (training-only sources; no leakage with STSS).
    excel_examples: List[Example] = []
    excel_sources: List[str] = []
    for csv_path in sorted(args.excel_dir.glob("*/*__gold_labels.csv")):
        ex = examples_from_excel_gold(csv_path, args.context)
        excel_examples.extend(ex)
        excel_sources.append(csv_path.stem.replace("__gold_labels", ""))

    # Load STSS XMI gold into a temp dir.
    with tempfile.TemporaryDirectory() as tmp:
        xmi_paths = unzip_xmis(args.xmi_zip_dir, Path(tmp))
        stss_examples = {
            novel: examples_from_stss(path, novel, args.context)
            for novel, path in xmi_paths.items()
        }

    folds = list(FOLDS) if args.fold == "both" else [args.fold]
    for fold in folds:
        cfg = FOLDS[fold]
        train_examples = list(excel_examples)
        for novel in cfg["train_stss"]:
            if novel not in stss_examples:
                raise FileNotFoundError(f"Missing STSS XMI for training novel: {novel}")
            train_examples.extend(stss_examples[novel])
        eval_novel = cfg["eval_stss"]
        if eval_novel not in stss_examples:
            raise FileNotFoundError(f"Missing STSS XMI for eval novel: {eval_novel}")
        eval_examples = stss_examples[eval_novel]

        train_balanced = downsample_noborder(train_examples, args.noborder_ratio, args.seed)
        train_rows = [to_messages_row(e, template_text, args.family) for e in train_balanced]
        # Eval kept at full natural distribution to match the real metric.
        eval_rows = [to_messages_row(e, template_text, args.family) for e in eval_examples]

        fold_dir = args.out_dir / fold
        write_jsonl(train_rows, fold_dir / "train.jsonl")
        write_jsonl(eval_rows, fold_dir / "eval.jsonl")

        meta = {
            "fold": fold,
            "family": args.family,
            "context": args.context,
            "noborder_ratio": args.noborder_ratio,
            "seed": args.seed,
            "train_sources": excel_sources + cfg["train_stss"],
            "eval_source": eval_novel,
            "train_total": len(train_rows),
            "train_border": sum(1 for r in train_rows if r["label"] == "BORDER"),
            "train_noborder": sum(1 for r in train_rows if r["label"] == "NOBORDER"),
            "eval_total": len(eval_rows),
            "eval_border": sum(1 for r in eval_rows if r["label"] == "BORDER"),
            "eval_noborder": sum(1 for r in eval_rows if r["label"] == "NOBORDER"),
        }
        (fold_dir / "meta.json").write_text(
            json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(
            f"[{fold}] train={meta['train_total']} "
            f"(B={meta['train_border']}/NB={meta['train_noborder']}) "
            f"eval={meta['eval_total']} (B={meta['eval_border']}) -> {fold_dir}"
        )


if __name__ == "__main__":
    main()
