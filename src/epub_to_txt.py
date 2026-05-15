#!/usr/bin/env python3
"""Convert an EPUB book into plain text."""

from __future__ import annotations

import argparse
import html
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


BLOCK_TAG_CLOSERS = re.compile(r"(?i)</(p|div|h[1-6]|li|tr|section|article|blockquote)>")
BR_TAGS = re.compile(r"(?i)<br\s*/?>")
STRIP_TAGS = re.compile(r"(?s)<[^>]+>")
STRIP_SCRIPTS = re.compile(r"(?is)<(script|style).*?>.*?</\1>")
MULTISPACE = re.compile(r"[ \t]+")
MULTINEWLINES = re.compile(r"\n{3,}")


def _extract_opf_path(epub_zip: zipfile.ZipFile) -> str:
    container_xml = epub_zip.read("META-INF/container.xml")
    root = ET.fromstring(container_xml)
    node = root.find(".//{*}rootfile")
    if node is None:
        raise ValueError("Could not locate OPF file in META-INF/container.xml.")
    opf_path = node.attrib.get("full-path")
    if not opf_path:
        raise ValueError("OPF path is missing in container.xml.")
    return opf_path


def _get_document_paths(epub_zip: zipfile.ZipFile) -> list[str]:
    try:
        opf_path = _extract_opf_path(epub_zip)
        opf_root = ET.fromstring(epub_zip.read(opf_path))
    except Exception:
        return sorted(
            name
            for name in epub_zip.namelist()
            if name.lower().endswith((".xhtml", ".html", ".htm"))
        )

    base_dir = str(Path(opf_path).parent)
    manifest: dict[str, str] = {}
    for item in opf_root.findall(".//{*}manifest/{*}item"):
        item_id = item.attrib.get("id")
        href = item.attrib.get("href")
        if not item_id or not href:
            continue
        media_type = item.attrib.get("media-type", "")
        if "xhtml" in media_type or "html" in media_type:
            manifest[item_id] = str((Path(base_dir) / href).as_posix())

    ordered_docs: list[str] = []
    for itemref in opf_root.findall(".//{*}spine/{*}itemref"):
        idref = itemref.attrib.get("idref")
        if not idref:
            continue
        href = manifest.get(idref)
        if href:
            ordered_docs.append(href)

    if ordered_docs:
        return ordered_docs

    return sorted(manifest.values())


def _html_to_text(content: str) -> str:
    text = STRIP_SCRIPTS.sub(" ", content)
    text = BR_TAGS.sub("\n", text)
    text = BLOCK_TAG_CLOSERS.sub("\n", text)
    text = STRIP_TAGS.sub(" ", text)
    text = html.unescape(text)

    lines = []
    for line in text.splitlines():
        clean_line = MULTISPACE.sub(" ", line).strip()
        if clean_line:
            lines.append(clean_line)
        else:
            lines.append("")

    joined = "\n".join(lines).strip()
    return MULTINEWLINES.sub("\n\n", joined)


def epub_to_txt(epub_path: Path, output_path: Path) -> None:
    with zipfile.ZipFile(epub_path, "r") as epub_zip:
        doc_paths = _get_document_paths(epub_zip)
        if not doc_paths:
            raise ValueError("No readable HTML/XHTML content found in EPUB.")

        chunks: list[str] = []
        for doc_path in doc_paths:
            try:
                raw = epub_zip.read(doc_path)
            except KeyError:
                continue
            content = raw.decode("utf-8", errors="ignore")
            chunk = _html_to_text(content)
            if chunk:
                chunks.append(chunk)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n\n".join(chunks).strip() + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parents[1]
    default_output_dir = project_root / "data" / "raw"

    parser = argparse.ArgumentParser(description="Convert EPUB to TXT.")
    parser.add_argument("epub", type=Path, help="Path to source .epub file.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=default_output_dir,
        help=f"Output directory (default: {default_output_dir}).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    epub_path = args.epub.expanduser().resolve()
    if not epub_path.exists():
        raise FileNotFoundError(f"EPUB file not found: {epub_path}")

    output_path = args.output_dir.expanduser().resolve() / f"{epub_path.stem}.txt"
    epub_to_txt(epub_path, output_path)
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
