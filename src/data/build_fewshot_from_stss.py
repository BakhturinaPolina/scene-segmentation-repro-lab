"""Extract few-shot example candidates from the stss_test_2 annotated corpus.

Input: the two zipped XMI files under
``upstream/scene-segmentation/data/full/stss_test_2/`` (Effi Briest,
Aus guter Familie) and the matching standoff JSON files.

Output: a JSON file with candidate BORDER and NOBORDER examples, each carrying
6 sentences of left context, the target sentence, 6 sentences of right
context, the gold label, the source novel, the scene index, and the
reason-for-change tags. The output is intended for human curation before
inlining into prompt templates D and E.

Run:
    python src/data/build_fewshot_from_stss.py \\
        --out data/interim/fewshot_candidates_stss_test_2.json

The script is read-only with respect to the upstream data and unzips XMIs
into a temporary directory.
"""

from __future__ import annotations

import argparse
import json
import re
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

WUENLP_NS = "{http:///de/uniwue/wuenlp.ecore}"
CAS_NS = "{http:///uima/cas.ecore}"
XMI_ID = "{http://www.omg.org/XMI}id"

REASON_TAGS = ("Zeit", "Figuren", "Raum", "Handlung")
SCENE_LEVEL_TYPE = "Szene Ebene 1"


@dataclass
class Sentence:
    begin: int
    end: int
    text: str


@dataclass
class Scene:
    begin: int
    end: int
    scene_index: int | None
    reasons: list[str]


@dataclass
class Candidate:
    novel: str
    label: str  # "BORDER" or "NOBORDER"
    scene_index: int | None
    reasons: list[str]
    target_offset: int
    target_text: str
    left_context: list[str]
    right_context: list[str]


def _whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def parse_xmi(xmi_path: Path) -> tuple[str, list[Sentence], list[Scene]]:
    tree = ET.parse(xmi_path)
    root = tree.getroot()

    sofa = next(root.iter(f"{CAS_NS}Sofa"))
    sofa_string = sofa.attrib.get("sofaString", "")

    sentences: list[Sentence] = []
    for el in root.iter(f"{WUENLP_NS}Sentence"):
        begin = int(el.attrib["begin"])
        end = int(el.attrib["end"])
        text = _whitespace(sofa_string[begin:end])
        if text:
            sentences.append(Sentence(begin=begin, end=end, text=text))
    sentences.sort(key=lambda s: s.begin)

    scenes: list[Scene] = []
    for el in root.iter(f"{WUENLP_NS}Scene"):
        if el.attrib.get("SceneType") != SCENE_LEVEL_TYPE:
            continue
        begin = int(el.attrib["begin"])
        end = int(el.attrib["end"])
        features_raw = el.attrib.get("AdditionalFeatures", "")
        scene_index: int | None = None
        reasons: list[str] = []
        if features_raw:
            try:
                payload = json.loads(features_raw)
                grund = payload.get("features", {}).get("Grund_für_Wechsel", "")
                for token in (t.strip().rstrip(",") for t in grund.split(",")):
                    if not token:
                        continue
                    if token.isdigit():
                        scene_index = int(token)
                    elif token in REASON_TAGS:
                        reasons.append(token)
            except json.JSONDecodeError:
                pass
        scenes.append(
            Scene(begin=begin, end=end, scene_index=scene_index, reasons=reasons)
        )
    scenes.sort(key=lambda s: s.begin)
    return sofa_string, sentences, scenes


def first_sentence_in_scene(sentences: list[Sentence], scene: Scene) -> int | None:
    """Return index in `sentences` of the first sentence whose begin >= scene.begin."""
    for idx, sent in enumerate(sentences):
        if sent.begin >= scene.begin and sent.end <= scene.end:
            return idx
    return None


def mid_scene_sentence_index(
    sentences: list[Sentence], scene: Scene, first_idx: int
) -> int | None:
    """Return index of a sentence safely inside the scene (not first, not last)."""
    indices = [
        i
        for i, s in enumerate(sentences)
        if s.begin >= scene.begin and s.end <= scene.end and i != first_idx
    ]
    if len(indices) < 3:
        return None
    return indices[len(indices) // 2]


def build_candidate(
    novel: str,
    sentences: list[Sentence],
    target_idx: int,
    label: str,
    scene: Scene,
    context: int,
) -> Candidate:
    left = [s.text for s in sentences[max(0, target_idx - context):target_idx]]
    right = [s.text for s in sentences[target_idx + 1: target_idx + 1 + context]]
    return Candidate(
        novel=novel,
        label=label,
        scene_index=scene.scene_index,
        reasons=scene.reasons,
        target_offset=sentences[target_idx].begin,
        target_text=sentences[target_idx].text,
        left_context=left,
        right_context=right,
    )


def candidates_for_novel(
    novel: str,
    xmi_path: Path,
    context: int = 6,
) -> list[Candidate]:
    _sofa, sentences, scenes = parse_xmi(xmi_path)
    out: list[Candidate] = []
    for scene in scenes:
        first_idx = first_sentence_in_scene(sentences, scene)
        if first_idx is None:
            continue
        # Require enough left context to be a useful few-shot example.
        if first_idx < context:
            continue
        out.append(
            build_candidate(novel, sentences, first_idx, "BORDER", scene, context)
        )
        mid_idx = mid_scene_sentence_index(sentences, scene, first_idx)
        if mid_idx is not None and mid_idx + context < len(sentences):
            out.append(
                build_candidate(
                    novel, sentences, mid_idx, "NOBORDER", scene, context
                )
            )
    return out


def unzip_xmis(zip_dir: Path, tmp_dir: Path) -> dict[str, Path]:
    out: dict[str, Path] = {}
    for zip_path in sorted(zip_dir.glob("*.xmi.zip")):
        novel = zip_path.name.replace(".xmi.zip", "")
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(tmp_dir)
        out[novel] = tmp_dir / f"{novel}.xmi"
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--xmi_zip_dir",
        type=Path,
        default=Path("upstream/scene-segmentation/data/full/stss_test_2"),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("data/interim/fewshot_candidates_stss_test_2.json"),
    )
    parser.add_argument("--context", type=int, default=6)
    args = parser.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        xmi_paths = unzip_xmis(args.xmi_zip_dir, tmp_dir)
        all_candidates: list[Candidate] = []
        for novel, path in xmi_paths.items():
            all_candidates.extend(
                candidates_for_novel(novel, path, context=args.context)
            )

    payload = {
        "dataset": "stss_test_2",
        "context_sentences_each_side": args.context,
        "n_candidates": len(all_candidates),
        "candidates": [asdict(c) for c in all_candidates],
    }
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(all_candidates)} candidates to {args.out}")


if __name__ == "__main__":
    main()
