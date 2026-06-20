#!/usr/bin/env python3
"""Prepare dProse sentence-level CSVs for prompting / Gemini Batch API.

Outputs per source file into data/processed/dprose/<slug>/:
- <slug>__for_prompting.txt           (one sentence per line)
- <slug>__for_prompting.jsonl         (sentence_index + text + source metadata)

Also writes a manifest:
- data/manifests/dprose_pilot.json (default)
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

DEFAULT_RAW_DIR = Path("data/raw/dprose")
DEFAULT_PILOT_FILES = [
    "dprose_100.csv",
    "dprose_806.csv",
    "dprose_2158.csv",
]


def slugify_filename(name: str) -> str:
    base = Path(name).stem.strip().lower()
    out = []
    for ch in base:
        if ch.isalnum():
            out.append(ch)
        else:
            out.append("_")
    slug = "".join(out)
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug.strip("_")


def md5sum(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if text.lower() == "nan":
        return ""
    return text


def infer_sentence_id_column(columns: list[str]) -> str | None:
    lowered = {c.lower(): c for c in columns}
    for preferred in ("sentence_id", "satz_id", "sent_nr", "sentence_nr", "sent_id"):
        if preferred in lowered:
            return lowered[preferred]
    for c in columns:
        lc = c.lower()
        if ("satz" in lc or "sent" in lc) and "id" in lc:
            return c
    return None


def infer_text_column(columns: list[str]) -> str:
    lowered = {c.lower(): c for c in columns}
    for preferred in ("sentence", "sent_text", "sentence_text", "text"):
        if preferred in lowered:
            return lowered[preferred]
    for c in columns:
        lc = c.lower()
        if "text" in lc and "rating" not in lc:
            return c
    raise ValueError(f"Could not infer sentence text column from: {columns}")


def coerce_int(value: Any, fallback: int) -> int:
    try:
        return int(float(str(value).strip()))
    except Exception:
        return fallback


def derive_prompting_rows(df: pd.DataFrame, source_name: str) -> list[dict[str, Any]]:
    columns = [str(c) for c in df.columns]
    sentence_id_col = infer_sentence_id_column(columns)
    text_col = infer_text_column(columns)

    records: list[dict[str, Any]] = []
    for i, row in df.iterrows():
        text = clean_text(row.get(text_col))
        if not text:
            continue
        sentence_idx = coerce_int(row.get(sentence_id_col), fallback=i) if sentence_id_col else i
        records.append(
            {
                "sentence_index": sentence_idx,
                "sentence_text_full": text,
                "source_file": source_name,
            }
        )
    return records


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--files",
        nargs="+",
        default=DEFAULT_PILOT_FILES,
        help="dProse CSV filenames under --raw_dir (default: pilot trio).",
    )
    parser.add_argument(
        "--raw_dir",
        type=Path,
        default=DEFAULT_RAW_DIR,
        help="Directory containing dProse CSV exports.",
    )
    parser.add_argument(
        "--out_dir",
        type=Path,
        default=Path("data/processed/dprose"),
        help="Output folder for processed inputs.",
    )
    parser.add_argument(
        "--manifest_out",
        type=Path,
        default=Path("data/manifests/dprose_pilot.json"),
        help="Manifest JSON output path.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    raw_dir = args.raw_dir.expanduser()
    out_dir = args.out_dir.expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_files: list[dict[str, Any]] = []
    profile_rows: list[dict[str, Any]] = []
    total_sentences = 0

    for csv_name in args.files:
        csv_path = (raw_dir / csv_name).resolve()
        if not csv_path.exists():
            raise FileNotFoundError(f"dProse CSV not found: {csv_path}")

        slug = slugify_filename(csv_path.name)
        target_dir = out_dir / slug
        target_dir.mkdir(parents=True, exist_ok=True)

        df = pd.read_csv(csv_path)
        df.columns = [str(c).strip() for c in df.columns]

        txt_out = target_dir / f"{slug}__for_prompting.txt"
        jsonl_out = target_dir / f"{slug}__for_prompting.jsonl"

        prompting_rows = derive_prompting_rows(df, source_name=csv_path.name)
        txt_out.write_text(
            "\n".join(row["sentence_text_full"] for row in prompting_rows) + "\n",
            encoding="utf-8",
        )
        write_jsonl(jsonl_out, prompting_rows)

        total_sentences += len(prompting_rows)
        manifest_files.append(
            {
                "source_file": csv_path.name,
                "slug": slug,
                "name": str(txt_out.relative_to(Path("data"))),
                "jsonl": str(jsonl_out.relative_to(Path("data"))),
                "size_bytes": txt_out.stat().st_size,
                "sentence_count": len(prompting_rows),
                "md5": md5sum(txt_out),
            }
        )
        profile_rows.append(
            {
                "csv_file": str(csv_path),
                "rows_raw": int(len(df)),
                "rows_used": int(len(prompting_rows)),
                "txt_out": str(txt_out),
                "jsonl_out": str(jsonl_out),
            }
        )
        print(f"Processed: {csv_path.name} -> {target_dir} ({len(prompting_rows)} sentences)")

    manifest = {
        "dataset": "dprose_pilot",
        "source": "local/dprose_sentence_level",
        "retrieved_at": date.today().isoformat(),
        "total_sentences": total_sentences,
        "files": manifest_files,
    }
    args.manifest_out.parent.mkdir(parents=True, exist_ok=True)
    args.manifest_out.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    profile_out = out_dir / "processing_report.json"
    profile_out.write_text(
        json.dumps({"workbooks": profile_rows, "total_sentences": total_sentences}, indent=2)
        + "\n",
        encoding="utf-8",
    )

    print(f"Total sentences: {total_sentences}")
    print(f"Wrote manifest: {args.manifest_out}")
    print(f"Wrote processing report: {profile_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
