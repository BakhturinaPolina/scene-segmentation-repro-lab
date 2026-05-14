"""Scene review renderer — human-readable Markdown output.

Reads annotated XMI files (ground truth scenes + model system scenes) and
prompting JSON results, then writes Markdown files to an output directory for
easy human review.

Usage
-----
# All three modes in one shot (recommended):
source .venv/bin/activate
python src/render_review.py \
    --mode all \
    --xmi_dir outputs/ssc/2026-04-05/baseline_bert/stss_test_2 \
    --standoff_dir upstream/scene-segmentation/data/standoff/stss_test_2 \
    --results_json outputs/prompting/2026-04-05/baseline_qwen3/results.json \
    --out_dir outputs/review

# With English translation (outputs to outputs/review/en/):
python src/render_review.py --mode all ... --translate

# Individual modes:
python src/render_review.py --mode ground_truth \
    --xmi_dir ... --standoff_dir ... --out_dir ...
python src/render_review.py --mode ssc \
    --xmi_dir ... --out_dir ...
python src/render_review.py --mode prompting \
    --results_json ... --out_dir ...

Options
-------
--snippet_chars INT   Characters shown at scene start (default 300). 0 = full text.
--tail_chars INT      Characters shown at scene end (default 100). 0 = skip tail.
--translate          Translate German text to English via Google Translate (free).
                     Writes to <out_dir>/en/ instead of <out_dir>/.
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path


# ---------------------------------------------------------------------------
# Translation helper
# ---------------------------------------------------------------------------

class _Translator:
    """Thin wrapper around GoogleTranslator with retry and chunking.

    Google Translate accepts up to 5000 chars per request. We split on
    paragraph boundaries to stay under the limit and preserve structure.
    """

    MAX_CHARS = 4800  # stay safely under 5000

    def __init__(self, source: str = "de", target: str = "en"):
        from deep_translator import GoogleTranslator  # noqa: PLC0415
        self._cls = GoogleTranslator
        self._source = source
        self._target = target

    def translate(self, text: str) -> str:
        if not text or not text.strip():
            return text
        # Split into chunks at paragraph/sentence boundaries
        if len(text) <= self.MAX_CHARS:
            return self._call(text)
        chunks = self._split(text)
        parts = []
        for chunk in chunks:
            parts.append(self._call(chunk))
            time.sleep(0.1)  # gentle pacing
        return " ".join(parts)

    def _call(self, text: str) -> str:
        for attempt in range(3):
            try:
                return self._cls(source=self._source, target=self._target).translate(text) or text
            except Exception:
                time.sleep(1.5 * (attempt + 1))
        return text  # fall back to original on persistent failure

    def _split(self, text: str) -> list[str]:
        """Split text into chunks ≤ MAX_CHARS, preferring paragraph breaks."""
        paragraphs = text.split("\n\n")
        chunks: list[str] = []
        current = ""
        for para in paragraphs:
            candidate = (current + "\n\n" + para).lstrip("\n")
            if len(candidate) <= self.MAX_CHARS:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                # If single paragraph is still too long, split by sentence
                if len(para) <= self.MAX_CHARS:
                    current = para
                else:
                    for i in range(0, len(para), self.MAX_CHARS):
                        chunks.append(para[i:i + self.MAX_CHARS])
                    current = ""
        if current:
            chunks.append(current)
        return chunks or [text]


# Singleton — None when --translate is not requested
_translator: _Translator | None = None


def _t(text: str) -> str:
    """Translate text if a translator is active, otherwise return as-is."""
    if _translator is None or not text:
        return text
    return _translator.translate(text)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _slug(name: str) -> str:
    """Turn a file stem into a safe filename part."""
    return re.sub(r"[^A-Za-z0-9_\-]", "_", name)


def _blockquote(text: str) -> str:
    """Wrap multi-line text as a Markdown blockquote."""
    return "\n".join("> " + line for line in text.splitlines())


def _scene_label(text: str) -> str:
    """Normalise German scene-type strings to short English labels."""
    t = text.lower()
    if "nicht" in t or "nonscene" in t:
        return "Nonscene"
    return "Scene"


def _load_standoff(path: Path) -> list[dict]:
    """Load standoff JSON and return list of scene dicts."""
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    return data.get("scenes", [])


def _border_set_from_scenes(scenes, doc_text: str) -> set[int]:
    """Return the set of character offsets where scenes begin."""
    return {s.begin for s in scenes}


# ---------------------------------------------------------------------------
# Mode 1: Ground truth reader
# ---------------------------------------------------------------------------

def render_ground_truth(
    xmi_path: Path,
    standoff_dir: Path,
    out_dir: Path,
    snippet_chars: int,
    tail_chars: int,
) -> Path:
    from wuenlp.impl.UIMANLPStructs import UIMADocument

    stem = xmi_path.name.replace(".xmi.zip", "").replace(".xmi", "")
    slug = _slug(stem)

    doc = UIMADocument.from_xmi(xmi_path)
    text = doc.text
    gold_scenes = list(doc.scenes)

    # Build standoff lookup keyed by begin offset for reason_for_change
    standoff_path = standoff_dir / f"{stem}.json"
    reason_by_begin: dict[int, list[str]] = {}
    if standoff_path.exists():
        for entry in _load_standoff(standoff_path):
            begin = entry.get("start", entry.get("begin"))
            r = entry.get("reason_for_change")
            if r:
                reason_by_begin[begin] = [x.strip(",").strip() for x in r]

    lines = [
        f"# Ground Truth — {stem}",
        f"",
        f"- **Total text length:** {len(text):,} chars",
        f"- **Total scenes:** {len(gold_scenes)}",
        f"- **Source:** `{xmi_path}`",
        f"",
        "---",
        "",
    ]

    n_scenes = len(gold_scenes)
    for i, sc in enumerate(gold_scenes, 1):
        label = _scene_label(sc.scene_type)
        reasons = reason_by_begin.get(sc.begin, [])
        reason_str = _t(", ".join(reasons)) if reasons else "—"
        span_len = sc.end - sc.begin
        scene_text = text[sc.begin:sc.end]

        lines.append(f"## Scene {i} — {sc.scene_type}  [chars {sc.begin}–{sc.end}, {span_len:,} chars]")
        lines.append("")

        if i > 1:
            lines.append(f"**Reason for change:** {reason_str}")
            lines.append("")

        if snippet_chars == 0:
            lines.append(_blockquote(_t(scene_text)))
        else:
            head = _t(scene_text[:snippet_chars])
            lines.append(_blockquote(head))
            if span_len > snippet_chars + tail_chars and tail_chars > 0:
                lines.append(f"> …[{span_len:,} chars total]…")
                tail = _t(scene_text[-tail_chars:])
                lines.append(_blockquote(tail))
            elif span_len > snippet_chars:
                lines.append(f"> …[{span_len - snippet_chars:,} more chars]")

        if _translator and i % 20 == 0:
            print(f"    translated {i}/{n_scenes} scenes…")

        lines.append("")
        lines.append("---")
        lines.append("")

    out_path = out_dir / f"{slug}__ground_truth.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Wrote {out_path}  ({len(gold_scenes)} scenes)")
    return out_path


# ---------------------------------------------------------------------------
# Mode 2: SSC vs gold diff
# ---------------------------------------------------------------------------

def render_ssc_vs_gold(
    xmi_path: Path,
    out_dir: Path,
    snippet_chars: int,
) -> Path:
    from wuenlp.impl.UIMANLPStructs import UIMADocument, UIMASentence

    stem = xmi_path.name.replace(".xmi.zip", "").replace(".xmi", "")
    slug = _slug(stem)

    doc = UIMADocument.from_xmi(xmi_path)
    text = doc.text
    gold_scenes = list(doc.scenes)
    sys_scenes = list(doc.system_scenes)

    # Build border sets: sentence index → BORDER or NOBORDER
    # A sentence is a BORDER if it's the first sentence of a scene.
    sentences = list(doc.sentences)
    sent_begins = [s.begin for s in sentences]

    def first_sent_of_scene(scenes_list) -> set[int]:
        """Return set of sentence-begin offsets that open a scene."""
        borders: set[int] = set()
        for sc in scenes_list:
            # Find the first sentence whose begin >= scene begin
            for s in sentences:
                if s.begin >= sc.begin:
                    borders.add(s.begin)
                    break
        return borders

    gold_borders = first_sent_of_scene(gold_scenes)
    pred_borders = first_sent_of_scene(sys_scenes)

    # Summary counts
    tp = sum(1 for s in sentences if s.begin in gold_borders and s.begin in pred_borders)
    fp = sum(1 for s in sentences if s.begin not in gold_borders and s.begin in pred_borders)
    fn = sum(1 for s in sentences if s.begin in gold_borders and s.begin not in pred_borders)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    lines = [
        f"# SSC vs Ground Truth — {stem}",
        "",
        f"- **Model:** SSC (bert-base-german-cased, 1 epoch, frozen embeddings)",
        f"- **Source XMI:** `{xmi_path}`",
        f"- **Sentences:** {len(sentences):,}",
        f"- **Gold scenes:** {len(gold_scenes)}  |  Gold borders: {len(gold_borders)}",
        f"- **Predicted scenes:** {len(sys_scenes)}  |  Predicted borders: {len(pred_borders)}",
        "",
        f"| TP | FP | FN | Precision | Recall | F1 |",
        f"|---|---|---|---|---|---|",
        f"| {tp} | {fp} | {fn} | {precision:.3f} | {recall:.3f} | {f1:.3f} |",
        "",
        "---",
        "",
        "## Scene boundary comparison",
        "",
        "Only sentences that are gold BORDER or predicted BORDER are shown (to keep the file readable).",
        "All others are NOBORDER/NOBORDER matches (omitted).",
        "",
        f"| # | Sentence text (first {snippet_chars} chars) | Gold | Predicted |",
        f"|---|---|---|---|",
    ]

    border_rows = []
    for i, s in enumerate(sentences):
        g = "**BORDER**" if s.begin in gold_borders else "NOBORDER"
        p = "**BORDER**" if s.begin in pred_borders else "NOBORDER"
        if s.begin in gold_borders or s.begin in pred_borders:
            raw_text = s.text[:snippet_chars] if s.text else ""
            sent_text = _t(raw_text).replace("|", "\\|").replace("\n", " ")
            match = "" if (g == p) else " ⚠"
            border_rows.append(f"| {i} | {sent_text} | {g} | {p}{match} |")

    if border_rows:
        lines.extend(border_rows)
    else:
        lines.append("| — | No borders detected by either model or gold | — | — |")

    lines += [
        "",
        "---",
        "",
        "## Gold scenes (with opening sentence)",
        "",
    ]

    for i, sc in enumerate(gold_scenes, 1):
        first_sent = next((s for s in sentences if s.begin >= sc.begin), None)
        raw_first = (first_sent.text[:snippet_chars] if first_sent and first_sent.text else "—")
        first_text = _t(raw_first).replace("\n", " ")
        lines.append(f"**{i}.** `{sc.scene_type}` [{sc.begin}–{sc.end}]  ")
        lines.append(f"→ {first_text}")
        lines.append("")

    out_path = out_dir / f"{slug}__ssc_vs_gold.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Wrote {out_path}  (F1={f1:.3f}, {len(sentences)} sentences, {len(gold_scenes)} gold scenes)")
    return out_path


# ---------------------------------------------------------------------------
# Mode 3: Prompting review
# ---------------------------------------------------------------------------

def render_prompting(results_json: Path, out_dir: Path) -> Path:
    with open(results_json, encoding="utf-8") as fh:
        data = json.load(fh)

    labels = data.get("labels", [])
    reasons = data.get("reasons", [])
    ground_truth = data.get("ground_truth", [])
    sentences = data.get("sentences", [])
    metrics = data.get("metrics")
    original_indices = data.get("original_indices")
    is_stratified = original_indices is not None

    n = len(labels)
    n_correct = sum(
        1 for p, g in zip(labels, ground_truth)
        if (p and g == "BORDER") or (not p and g == "NOBORDER")
    )
    n_pred_border = sum(1 for p in labels if (p is True or p == "BORDER"))
    n_gold_border = sum(1 for g in ground_truth if g == "BORDER")

    doc_name = data.get("file", "")
    model_name = data.get("model", "nvidia/nemotron-3-super-120b-a12b:free")

    lines = [
        f"# Prompting Review — {model_name} (OpenRouter)",
        "",
        f"- **Results file:** `{results_json}`",
        f"- **Document:** {doc_name}" if doc_name else "",
        f"- **Sentences classified:** {n}"
        + (f"  (stratified sample)" if is_stratified else ""),
        f"- **Gold borders in sample:** {n_gold_border}",
        f"- **Predicted borders:** {n_pred_border}",
        f"- **Accuracy:** {n_correct}/{n} = {n_correct/n:.1%}" if n else "- **Accuracy:** —",
    ]
    lines = [l for l in lines if l != ""]

    if metrics:
        lines += [
            "",
            "### Metrics (Precision / Recall / F1)",
            "",
            "| Tolerance | Precision | Recall | F1 | TP | FP | FN |",
            "|-----------|-----------|--------|-----|----|----|-----|",
        ]
        for tol_key in sorted(metrics.keys()):
            m = metrics[tol_key]
            tol_label = tol_key.replace("tol_", "")
            lines.append(
                f"| {tol_label} "
                f"| {m['precision']:.3f} "
                f"| {m['recall']:.3f} "
                f"| {m['f1']:.3f} "
                f"| {m['tp']} "
                f"| {m['fp']} "
                f"| {m['fn']} |"
            )

    lines += ["", "---", ""]

    for i, (label, reason, gt, sent) in enumerate(
        zip(labels, reasons, ground_truth, sentences), 1
    ):
        pred_str = "BORDER" if (label is True or label == "BORDER") else "NOBORDER"
        gt_str = gt if isinstance(gt, str) else ("BORDER" if gt else "NOBORDER")
        match_mark = "✓" if pred_str == gt_str else "✗"
        idx_info = f" (idx {original_indices[i-1]})" if is_stratified else ""
        header = f"### Sentence {i}{idx_info}  [{gt_str} → pred: {pred_str} {match_mark}]"
        lines.append(header)
        lines.append("")
        sent_display = _t(sent) if sent else sent
        lines.append(f"**Text (first 200 chars):** {sent_display}")
        lines.append("")
        lines.append("**Model reasoning:**")
        lines.append("")
        lines.append(_blockquote(reason.strip()))
        lines.append("")
        lines.append("---")
        lines.append("")

    stem = results_json.stem.replace("results_", "").replace("results", "")
    parent_slug = _slug(results_json.parent.name)
    slug = _slug(stem) if stem else parent_slug
    out_path = out_dir / f"prompting__{parent_slug}__{slug}.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    acc_str = f", accuracy {n_correct/n:.1%}" if n else ""
    print(f"  Wrote {out_path}  ({n} sentences{acc_str})")
    return out_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Render human-readable Markdown review files from experiment outputs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--mode",
        choices=["ground_truth", "ssc", "prompting", "all"],
        default="all",
        help="Which review(s) to render (default: all).",
    )
    parser.add_argument(
        "--xmi_dir",
        type=Path,
        default=None,
        help="Directory containing annotated .xmi.zip files (needed for ground_truth and ssc modes).",
    )
    parser.add_argument(
        "--standoff_dir",
        type=Path,
        default=None,
        help="Directory containing standoff .json files (needed for ground_truth mode).",
    )
    parser.add_argument(
        "--results_json",
        type=Path,
        nargs="+",
        default=None,
        help="Path(s) to prompting results JSON file(s) (needed for prompting mode). "
             "Accepts multiple files for stratified per-document results.",
    )
    parser.add_argument(
        "--out_dir",
        type=Path,
        default=Path("outputs/review"),
        help="Output directory for Markdown files (default: outputs/review).",
    )
    parser.add_argument(
        "--snippet_chars",
        type=int,
        default=300,
        help="Characters to show at the start of each scene (0 = full text, default: 300).",
    )
    parser.add_argument(
        "--tail_chars",
        type=int,
        default=100,
        help="Characters to show at the end of each scene (0 = skip, default: 100).",
    )
    parser.add_argument(
        "--translate",
        action="store_true",
        default=False,
        help=(
            "Translate German text to English via Google Translate. "
            "Output is written to <out_dir>/en/ instead of <out_dir>/."
        ),
    )
    args = parser.parse_args()

    # Enable translation if requested
    global _translator
    if args.translate:
        print("Translation mode: de → en  (Google Translate, free)")
        _translator = _Translator(source="de", target="en")
        args.out_dir = args.out_dir / "en"

    args.out_dir.mkdir(parents=True, exist_ok=True)

    modes = {"ground_truth", "ssc", "prompting"} if args.mode == "all" else {args.mode}

    if "ground_truth" in modes or "ssc" in modes:
        if args.xmi_dir is None:
            parser.error("--xmi_dir is required for modes ground_truth and ssc")
        xmi_files = sorted(args.xmi_dir.glob("*.xmi.zip")) + sorted(args.xmi_dir.glob("*.xmi"))
        if not xmi_files:
            print(f"No .xmi.zip or .xmi files found in {args.xmi_dir}", file=sys.stderr)
            sys.exit(1)

    if "ground_truth" in modes:
        if args.standoff_dir is None:
            parser.error("--standoff_dir is required for mode ground_truth")
        print("=== Ground truth ===")
        for xmi_path in xmi_files:
            render_ground_truth(
                xmi_path,
                args.standoff_dir,
                args.out_dir,
                args.snippet_chars,
                args.tail_chars,
            )

    if "ssc" in modes:
        print("=== SSC vs gold ===")
        for xmi_path in xmi_files:
            render_ssc_vs_gold(xmi_path, args.out_dir, snippet_chars=120)

    if "prompting" in modes:
        if args.results_json is None:
            parser.error("--results_json is required for mode prompting")
        print("=== Prompting ===")
        for rj in args.results_json:
            render_prompting(rj, args.out_dir)

    print(f"\nDone. Review files in: {args.out_dir}/")


if __name__ == "__main__":
    main()
