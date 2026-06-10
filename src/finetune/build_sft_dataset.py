#!/usr/bin/env python3
"""Build leakage-safe SFT datasets for scene-boundary fine-tuning.

Two modes
=========

1. ``--mode folds`` (default, backward compatible)
   Leave-one-text-out folds over the locally available STSS-Test-2 novels plus
   the Excel gold texts. STSS-Test-2 is the paper's TEST set, so a model is never
   trained and evaluated on the same novel:

   - fold_A: train = Excel + Aus guter Familie ; eval = Effi Briest
   - fold_B: train = Excel + Effi Briest      ; eval = Aus guter Familie

2. ``--mode corpus`` (paper-comparable)
   Train on one named split and evaluate on another, using the full 41-text paper
   corpus. Splits and expected per-text counts come from
   ``data/manifests/finetune_splits.json`` (paper Table 5/6). XMI zips are
   discovered recursively under ``--corpus_dir`` and matched to split members by
   file stem (``<Text Name>.xmi.zip`` -> ``<Text Name>``).

   - default: train = train_full ; eval = stss_test_2 (paper's main comparison)

Output (per fold / split-pair) under ``data/processed/finetune/<tag>/``:
- ``train.jsonl`` (NOBORDER subsampled per ``--negative_mode``)
- ``eval.jsonl``  (held-out texts, full natural distribution)
- ``meta.json``   (counts, config, provenance)

A top-level ``verification.json`` is also written, comparing parsed per-text
sentence/border counts against the manifest's expected paper counts (closes the
"no reproducible data extraction proof for LLaMA labels" reproducibility gap).

Each JSONL row is TRL-SFT compatible chat format::

    {"messages": [{"role": "user", "content": <prompt>},
                   {"role": "assistant", "content": <rationale + JSON label>}]}

The user turn renders a precision-focused prompt template (default ``L`` strict)
so the fine-tuned model learns the SAME contract used at inference. The assistant
turn is one of three target formats (``--target_format``); all three end with a
``{"label": ..., "confidence": ...}`` JSON object so the eval parser can read the
label regardless of format.

Examples
--------
Folds mode (local smoke / leave-one-out)::

    python src/finetune/build_sft_dataset.py --mode folds --fold both

Corpus mode (paper-comparable, once the full corpus is on disk)::

    python src/finetune/build_sft_dataset.py --mode corpus \
        --train_split train_full --eval_split stss_test_2 \
        --target_format cot_list --negative_mode paper10pct
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import re
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

_FILE = Path(__file__).resolve()
_SRC_ROOT = _FILE.parents[1]
_PROJECT_ROOT = _FILE.parents[2]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from core.prompt_runtime import get_template_text, load_prompt_registry, render_prompt_for_family
from data.build_fewshot_from_stss import parse_xmi, unzip_xmis

# Gold reason tags -> the four CoT-List dimensions (paper appendix A.2).
REASON_TAGS = ("Zeit", "Raum", "Figuren", "Handlung")
REASON_LABELS = {
    "Zeit": "time",
    "Raum": "location",
    "Figuren": "character constellation",
    "Handlung": "narrative action",
}
# Order in which the four dimensions are listed in the CoT-List rationale.
COT_DIMENSIONS = [
    ("Handlung", "narrative action"),
    ("Raum", "location"),
    ("Zeit", "time"),
    ("Figuren", "the character constellation"),
]

STSS_NOVELS = {
    "Aus guter Familie": "aus_guter_familie",
    "Effi Briest": "effi_briest",
}

FOLDS = {
    "fold_A": {"train_stss": ["Aus guter Familie"], "eval_stss": "Effi Briest"},
    "fold_B": {"train_stss": ["Effi Briest"], "eval_stss": "Aus guter Familie"},
}

TARGET_FORMATS = ("cot_list", "json", "no_cot")
NEGATIVE_MODES = ("ratio", "paper10pct", "hard")
CONTEXT_MODES = ("sentences", "tokens512")


@dataclass
class Example:
    source: str          # provenance (text / novel / excel file stem)
    index: int           # position within its document
    label: str           # BORDER / NOBORDER
    target_text: str
    left_context: List[str]
    right_context: List[str]
    reasons: List[str]   # gold reason tags (XMI only); empty otherwise


# ---------------------------------------------------------------------------
# Context windowing
# ---------------------------------------------------------------------------

def _context_sentences(texts: List[str], i: int, context: int) -> Tuple[List[str], List[str]]:
    left = texts[max(0, i - context):i]
    right = texts[i + 1: i + 1 + context]
    return left, right


def _context_token_budget(texts: List[str], i: int, budget: int) -> Tuple[List[str], List[str]]:
    """Symmetric context expansion bounded by a whitespace-token budget.

    Approximates the paper's "512 tokens total, balanced by number of sentences"
    window without pulling in a model tokenizer (keeps this module dependency
    light). Expands one sentence at a time, alternating left/right, stopping a
    side once its next sentence would not fit.
    """
    remaining = max(0, budget - len(texts[i].split()))
    left_rev: List[str] = []
    right: List[str] = []
    li, ri = i - 1, i + 1
    left_open, right_open = li >= 0, ri < len(texts)
    take_left = True
    while remaining > 0 and (left_open or right_open):
        if take_left and left_open:
            tok = len(texts[li].split())
            if tok <= remaining:
                left_rev.append(texts[li])
                remaining -= tok
                li -= 1
                left_open = li >= 0
            else:
                left_open = False
        elif right_open:
            tok = len(texts[ri].split())
            if tok <= remaining:
                right.append(texts[ri])
                remaining -= tok
                ri += 1
                right_open = ri < len(texts)
            else:
                right_open = False
        # Alternate sides; if one side is closed, keep feeding the other.
        if left_open and right_open:
            take_left = not take_left
        else:
            take_left = left_open
    left_rev.reverse()
    return left_rev, right


def build_context(
    texts: List[str], i: int, context: int, context_mode: str, token_budget: int
) -> Tuple[List[str], List[str]]:
    if context_mode == "tokens512":
        return _context_token_budget(texts, i, token_budget)
    return _context_sentences(texts, i, context)


# ---------------------------------------------------------------------------
# Source loaders -> ordered per-document list of Example
# ---------------------------------------------------------------------------

def examples_from_stss(
    xmi_path: Path, novel: str, context: int, context_mode: str, token_budget: int
) -> List[Example]:
    _sofa, sentences, scenes = parse_xmi(xmi_path)
    texts = [s.text for s in sentences]
    # First sentence (by begin offset) inside each scene is a gold BORDER.
    border_idx_to_reasons: Dict[int, List[str]] = {}
    for scene in scenes:
        for idx, sent in enumerate(sentences):
            if sent.begin >= scene.begin and sent.end <= scene.end:
                border_idx_to_reasons[idx] = scene.reasons
                break
    out: List[Example] = []
    for i, text in enumerate(texts):
        is_border = i in border_idx_to_reasons
        left, right = build_context(texts, i, context, context_mode, token_budget)
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


def examples_from_excel_gold(
    csv_path: Path, context: int, context_mode: str, token_budget: int
) -> List[Example]:
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
        left, right = build_context(texts, i, context, context_mode, token_budget)
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
# Corpus discovery (corpus mode)
# ---------------------------------------------------------------------------

def discover_xmi_zips(corpus_dir: Path) -> Dict[str, Path]:
    """Map text-name stem -> zip path for every ``*.xmi.zip`` under corpus_dir."""
    found: Dict[str, Path] = {}
    for zip_path in sorted(corpus_dir.rglob("*.xmi.zip")):
        stem = zip_path.name[: -len(".xmi.zip")]
        found.setdefault(stem, zip_path)
    return found


def unzip_one(zip_path: Path, stem: str, tmp_dir: Path) -> Path:
    """Extract a single XMI zip and return the path to its .xmi file."""
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(tmp_dir)
    preferred = tmp_dir / f"{stem}.xmi"
    if preferred.exists():
        return preferred
    candidates = sorted(tmp_dir.glob("*.xmi"))
    if not candidates:
        raise FileNotFoundError(f"No .xmi found inside {zip_path}")
    return candidates[0]


def examples_for_split(
    split_name: str,
    members: List[str],
    available: Dict[str, Path],
    context: int,
    context_mode: str,
    token_budget: int,
) -> Tuple[List[Example], List[str]]:
    """Build examples for all available texts of a split. Returns (examples, missing)."""
    examples: List[Example] = []
    missing: List[str] = []
    for name in members:
        zip_path = available.get(name)
        if zip_path is None:
            missing.append(name)
            continue
        with tempfile.TemporaryDirectory() as tmp:
            xmi_path = unzip_one(zip_path, name, Path(tmp))
            examples.extend(
                examples_from_stss(xmi_path, name, context, context_mode, token_budget)
            )
    return examples, missing


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


def _label_json(label: str, confidence: float = 0.9) -> str:
    return json.dumps({"label": label, "confidence": confidence})


def _cot_list_rationale(ex: Example) -> str:
    changed = set(ex.reasons)
    is_border = ex.label == "BORDER"
    border_no_reasons = is_border and not changed
    bullets = ["a)", "b)", "c)", "d)"]
    lines: List[str] = []
    for marker, (tag, phrase) in zip(bullets, COT_DIMENSIONS):
        if not is_border:
            state = "no"
        elif border_no_reasons:
            state = "may be a"  # paper: "there may be a significant change"
        else:
            state = "a" if tag in changed else "no"
        if state == "may be a":
            lines.append(f"{marker} there may be a significant change in {phrase},")
        else:
            lines.append(f"{marker} there is {state} significant change in {phrase},")
    if is_border:
        lines.append("e) therefore, the sentence starts a new scene.")
    else:
        lines.append("e) therefore, the sentence does not start a new scene.")
    return "\n".join(lines)


def _no_cot_rationale(ex: Example) -> str:
    if ex.label == "BORDER":
        return ("True, because there is a significant change in narrative action, "
                "location, time or characters.")
    return ("False, because there is no significant change in narrative action, "
            "location, time or characters.")


def build_assistant_turn(ex: Example, target_format: str) -> str:
    if target_format == "json":
        return _label_json(ex.label)
    if target_format == "no_cot":
        return _no_cot_rationale(ex) + "\n" + _label_json(ex.label)
    # default: cot_list
    return _cot_list_rationale(ex) + "\n" + _label_json(ex.label)


def to_messages_row(ex: Example, template_text: str, family: str, target_format: str) -> dict:
    return {
        "messages": [
            {"role": "user", "content": build_user_turn(ex, template_text, family)},
            {"role": "assistant", "content": build_assistant_turn(ex, target_format)},
        ],
        "label": ex.label,
        "source": ex.source,
        "index": ex.index,
    }


# ---------------------------------------------------------------------------
# Negative selection
# ---------------------------------------------------------------------------

def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def load_fp_sentences(paths: List[Path]) -> Set[str]:
    """Best-effort: collect normalized sentence texts that a cached run predicted
    as BORDER while gold was NOBORDER (false positives), to up-weight as hard
    negatives. Tolerant to missing files / unexpected shapes."""
    fp: Set[str] = set()
    for path in paths:
        if not path.exists():
            print(f"[hard] fp_cache not found, skipping: {path}")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            print(f"[hard] could not parse fp_cache {path}: {exc}")
            continue
        entries = data.values() if isinstance(data, dict) else data
        if not isinstance(entries, (list, tuple)) and not hasattr(entries, "__iter__"):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            pred = str(entry.get("pred", "")).upper()
            gold = str(entry.get("gold", "")).upper()
            sent = entry.get("sentence")
            if pred == "BORDER" and gold == "NOBORDER" and sent:
                fp.add(_normalize_text(str(sent)))
    return fp


def _evenly_sample(items: List[Example], keep_n: int) -> List[Example]:
    if keep_n >= len(items):
        return list(items)
    step = len(items) / keep_n
    return [items[int(k * step)] for k in range(keep_n)]


def select_train_examples(
    examples: List[Example],
    mode: str,
    ratio: int,
    seed: int,
    hard_window: int,
    fp_sentences: Set[str],
) -> List[Example]:
    """Keep all BORDER; subsample NOBORDER according to ``mode``."""
    borders = [e for e in examples if e.label == "BORDER"]
    noborders = [e for e in examples if e.label == "NOBORDER"]
    if not noborders:
        return sorted(borders, key=lambda e: (e.source, e.index))

    if mode == "paper10pct":
        keep_n = max(1, round(0.10 * len(noborders)))
        selected = _evenly_sample(noborders, keep_n)

    elif mode == "hard":
        # Per-source border positions, to score adjacency hardness.
        border_pos: Dict[str, List[int]] = {}
        for e in borders:
            border_pos.setdefault(e.source, []).append(e.index)

        def distance_to_border(e: Example) -> int:
            positions = border_pos.get(e.source)
            if not positions:
                return 10 ** 9
            return min(abs(e.index - p) for p in positions)

        def hardness(e: Example) -> Tuple[int, int]:
            # Lower sorts first (harder): FP-matched, then closer to a border.
            is_fp = 0 if _normalize_text(e.target_text) in fp_sentences else 1
            return (is_fp, distance_to_border(e))

        keep_n = ratio * len(borders) if ratio > 0 else len(noborders)
        keep_n = min(keep_n, len(noborders))
        ranked = sorted(noborders, key=hardness)
        selected = ranked[:keep_n]
        n_fp = sum(1 for e in selected if _normalize_text(e.target_text) in fp_sentences)
        n_adj = sum(1 for e in selected if distance_to_border(e) <= hard_window)
        print(f"[hard] selected {len(selected)} negatives "
              f"(fp-matched={n_fp}, within {hard_window} of a border={n_adj})")

    else:  # ratio
        if ratio <= 0 or len(noborders) <= ratio * len(borders):
            selected = noborders
        else:
            selected = _evenly_sample(noborders, ratio * len(borders))

    random.Random(seed).shuffle(selected)  # break ties; re-sorted below
    return sorted(borders + selected, key=lambda e: (e.source, e.index))


# ---------------------------------------------------------------------------
# Verification against paper Table 5 counts
# ---------------------------------------------------------------------------

def verify_counts(
    per_text_examples: Dict[str, List[Example]],
    manifest: dict,
    sentence_tolerance: float,
) -> dict:
    expected = manifest.get("expected_counts", {})
    report: Dict[str, dict] = {}
    all_ok = True
    for name, exs in sorted(per_text_examples.items()):
        parsed_sent = len(exs)
        parsed_border = sum(1 for e in exs if e.label == "BORDER")
        exp = expected.get(name, {})
        exp_sent = exp.get("sentences")
        # Parser extracts scene-level borders only, so the verification target is
        # 'scenes'. 'non_scenes' is reported to keep the scenes-vs-segments gap visible.
        exp_scenes = exp.get("scenes")
        exp_non_scenes = exp.get("non_scenes")
        exp_segments = (
            None if exp_scenes is None or exp_non_scenes is None
            else exp_scenes + exp_non_scenes
        )
        sent_ok = (
            exp_sent is None
            or abs(parsed_sent - exp_sent) <= max(1, round(sentence_tolerance * exp_sent))
        )
        border_ok = exp_scenes is None or parsed_border == exp_scenes
        ok = sent_ok and border_ok
        all_ok = all_ok and ok
        report[name] = {
            "parsed_sentences": parsed_sent,
            "expected_sentences": exp_sent,
            "sentences_ok": sent_ok,
            "parsed_borders": parsed_border,
            "expected_scene_borders": exp_scenes,
            "expected_segment_borders": exp_segments,
            "borders_ok": border_ok,
            "ok": ok,
        }
    return {"all_ok": all_ok, "sentence_tolerance": sentence_tolerance, "texts": report}


# ---------------------------------------------------------------------------
# IO helpers
# ---------------------------------------------------------------------------

def write_jsonl(rows: List[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_pair(
    tag: str,
    train_examples: List[Example],
    eval_examples: List[Example],
    args,
    template_text: str,
    fp_sentences: Set[str],
    extra_meta: dict,
) -> dict:
    train_sel = select_train_examples(
        train_examples, args.negative_mode, args.noborder_ratio,
        args.seed, args.hard_window, fp_sentences,
    )
    train_rows = [to_messages_row(e, template_text, args.family, args.target_format) for e in train_sel]
    # Eval kept at full natural distribution to match the real metric.
    eval_rows = [to_messages_row(e, template_text, args.family, args.target_format) for e in eval_examples]

    pair_dir = args.out_dir / tag
    write_jsonl(train_rows, pair_dir / "train.jsonl")
    write_jsonl(eval_rows, pair_dir / "eval.jsonl")

    meta = {
        "tag": tag,
        "family": args.family,
        "target_format": args.target_format,
        "context": args.context,
        "context_mode": args.context_mode,
        "token_budget": args.token_budget,
        "negative_mode": args.negative_mode,
        "noborder_ratio": args.noborder_ratio,
        "hard_window": args.hard_window,
        "seed": args.seed,
        "train_total": len(train_rows),
        "train_border": sum(1 for r in train_rows if r["label"] == "BORDER"),
        "train_noborder": sum(1 for r in train_rows if r["label"] == "NOBORDER"),
        "eval_total": len(eval_rows),
        "eval_border": sum(1 for r in eval_rows if r["label"] == "BORDER"),
        "eval_noborder": sum(1 for r in eval_rows if r["label"] == "NOBORDER"),
        **extra_meta,
    }
    (pair_dir / "meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(
        f"[{tag}] train={meta['train_total']} "
        f"(B={meta['train_border']}/NB={meta['train_noborder']}) "
        f"eval={meta['eval_total']} (B={meta['eval_border']}) -> {pair_dir}"
    )
    return meta


# ---------------------------------------------------------------------------
# Mode runners
# ---------------------------------------------------------------------------

def run_folds_mode(args, template_text: str, fp_sentences: Set[str]) -> None:
    excel_examples: List[Example] = []
    excel_sources: List[str] = []
    for csv_path in sorted(args.excel_dir.glob("*/*__gold_labels.csv")):
        excel_examples.extend(
            examples_from_excel_gold(csv_path, args.context, args.context_mode, args.token_budget)
        )
        excel_sources.append(csv_path.stem.replace("__gold_labels", ""))

    with tempfile.TemporaryDirectory() as tmp:
        xmi_paths = unzip_xmis(args.xmi_zip_dir, Path(tmp))
        stss_examples = {
            novel: examples_from_stss(path, novel, args.context, args.context_mode, args.token_budget)
            for novel, path in xmi_paths.items()
        }

    per_text = dict(stss_examples)
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
        write_pair(
            fold, train_examples, stss_examples[eval_novel], args, template_text, fp_sentences,
            extra_meta={
                "mode": "folds",
                "data_scope": "stss_test_2_pilot",
                "debug_only": True,
                "manifest_ref": "data/manifests/stss_test_2.json",
                "train_sources": excel_sources + cfg["train_stss"],
                "eval_source": eval_novel,
            },
        )

    verification = verify_counts(per_text, args.manifest_data, args.sentence_tolerance)
    (args.out_dir / "verification.json").write_text(
        json.dumps(verification, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    _print_verification(verification)


def run_corpus_mode(args, template_text: str, fp_sentences: Set[str]) -> None:
    splits = args.manifest_data.get("splits", {})
    for split_key in (args.train_split, args.eval_split):
        if split_key not in splits:
            raise ValueError(
                f"Unknown split '{split_key}'. Available: {sorted(splits)}"
            )

    available = discover_xmi_zips(args.corpus_dir)
    print(f"[corpus] discovered {len(available)} XMI zips under {args.corpus_dir}")

    train_examples, train_missing = examples_for_split(
        args.train_split, splits[args.train_split], available,
        args.context, args.context_mode, args.token_budget,
    )
    eval_examples, eval_missing = examples_for_split(
        args.eval_split, splits[args.eval_split], available,
        args.context, args.context_mode, args.token_budget,
    )

    if train_missing:
        print(f"[corpus] WARNING: missing {len(train_missing)} train texts: {train_missing}")
    if eval_missing:
        print(f"[corpus] WARNING: missing {len(eval_missing)} eval texts: {eval_missing}")
    if not train_examples:
        raise FileNotFoundError(
            f"No XMI zips found for train split '{args.train_split}' under {args.corpus_dir}. "
            "Place the corpus zips there (same '<Text Name>.xmi.zip' format as STSS-Test-2)."
        )
    if not eval_examples:
        raise FileNotFoundError(
            f"No XMI zips found for eval split '{args.eval_split}' under {args.corpus_dir}."
        )

    tag = f"{args.train_split}__to__{args.eval_split}"
    write_pair(
        tag, train_examples, eval_examples, args, template_text, fp_sentences,
        extra_meta={
            "mode": "corpus",
            "data_scope": "full_corpus",
            "debug_only": False,
            "manifest_ref": "data/manifests/finetune_splits.json",
            "train_split": args.train_split,
            "eval_split": args.eval_split,
            "train_texts_present": sorted({e.source for e in train_examples}),
            "eval_texts_present": sorted({e.source for e in eval_examples}),
            "train_texts_missing": train_missing,
            "eval_texts_missing": eval_missing,
        },
    )

    # Verify every text we actually parsed. Count each source once even if the
    # train and eval splits overlap (e.g. a leakage smoke run).
    per_text: Dict[str, List[Example]] = {}
    for e in train_examples:
        per_text.setdefault(e.source, []).append(e)
    for e in eval_examples:
        if e.source not in per_text:
            per_text.setdefault(e.source, []).append(e)
    verification = verify_counts(per_text, args.manifest_data, args.sentence_tolerance)
    (args.out_dir / "verification.json").write_text(
        json.dumps(verification, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    _print_verification(verification)


def _print_verification(verification: dict) -> None:
    status = "OK" if verification["all_ok"] else "MISMATCH"
    print(f"[verify] {status} (tolerance {verification['sentence_tolerance']:.0%} on sentence counts)")
    for name, rep in verification["texts"].items():
        flag = "ok " if rep["ok"] else "BAD"
        print(
            f"[verify] {flag} {name}: sent {rep['parsed_sentences']}"
            f"/{rep['expected_sentences']} scene-borders {rep['parsed_borders']}"
            f"/{rep['expected_scene_borders']} (segments incl. non-scenes: "
            f"{rep['expected_segment_borders']})"
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--mode", choices=["folds", "corpus"], default="folds")

    # Shared formatting controls.
    parser.add_argument("--family", default="L",
                        help="Prompt family used as the SFT instruction (default: L strict)")
    parser.add_argument("--target_format", choices=TARGET_FORMATS, default="cot_list",
                        help="Assistant target style; all end with a JSON label (default: cot_list)")
    parser.add_argument("--context", type=int, default=4,
                        help="Sentences of context on each side (sentences mode; default: 4)")
    parser.add_argument("--context_mode", choices=CONTEXT_MODES, default="sentences")
    parser.add_argument("--token_budget", type=int, default=512,
                        help="Total whitespace-token budget for tokens512 context mode")
    parser.add_argument("--negative_mode", choices=NEGATIVE_MODES, default="ratio")
    parser.add_argument("--noborder_ratio", type=int, default=3,
                        help="NOBORDER:BORDER ratio in TRAIN for ratio/hard modes (0 = keep all)")
    parser.add_argument("--hard_window", type=int, default=3,
                        help="Adjacency window for hard-negative scoring (default: 3)")
    parser.add_argument("--fp_cache", type=Path, nargs="*", default=[],
                        help="Optional run cache JSON(s) to mine false-positive hard negatives")
    parser.add_argument("--seed", type=int, default=1337)

    # Folds mode sources.
    parser.add_argument("--fold", choices=["fold_A", "fold_B", "both"], default="both")
    parser.add_argument(
        "--xmi_zip_dir", type=Path,
        default=_PROJECT_ROOT / "upstream/scene-segmentation/data/full/stss_test_2",
    )
    parser.add_argument(
        "--excel_dir", type=Path,
        default=_PROJECT_ROOT / "data/processed/excel_prompting",
    )

    # Corpus mode sources.
    parser.add_argument(
        "--corpus_dir", type=Path,
        default=_PROJECT_ROOT / "upstream/scene-segmentation/data/full",
        help="Directory searched recursively for '*.xmi.zip' (corpus mode)",
    )
    parser.add_argument("--train_split", default="train_full")
    parser.add_argument("--eval_split", default="stss_test_2")

    # Shared outputs / manifest.
    parser.add_argument(
        "--out_dir", type=Path,
        default=_PROJECT_ROOT / "data/processed/finetune",
    )
    parser.add_argument("--prompts_dir", type=Path, default=_SRC_ROOT / "prompts")
    parser.add_argument(
        "--split_manifest", type=Path,
        default=_PROJECT_ROOT / "data/manifests/finetune_splits.json",
    )
    parser.add_argument("--sentence_tolerance", type=float, default=0.05,
                        help="Relative tolerance for sentence-count verification (default: 5%%)")
    args = parser.parse_args()

    registry = load_prompt_registry(args.prompts_dir)
    template_text = get_template_text(args.prompts_dir, args.family, registry)
    args.manifest_data = json.loads(args.split_manifest.read_text(encoding="utf-8"))
    fp_sentences = load_fp_sentences(list(args.fp_cache)) if args.negative_mode == "hard" else set()

    if args.mode == "folds":
        run_folds_mode(args, template_text, fp_sentences)
    else:
        run_corpus_mode(args, template_text, fp_sentences)


if __name__ == "__main__":
    main()
