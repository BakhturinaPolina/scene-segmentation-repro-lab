#!/usr/bin/env python3
"""Prepare sentence-level Excel sources for prompting config B.

Outputs per workbook into data/processed/excel_prompting/<slug>/:
- <slug>__sheet1.csv                  (raw CSV export)
- <slug>__for_prompting.txt           (one sentence per line)
- <slug>__for_prompting.jsonl         (sentence_index + text + source metadata)
- <slug>__gold_labels.csv             (BORDER/NOBORDER derived from scene IDs)

Also writes a manifest (same top-level shape as data/manifest_stss_test_2.json):
- data/processed/manifest_excel_prompting.json
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


DEFAULT_EXCEL_FILES = [
    Path("data/raw/Gaensemagd_sentence level.xlsx"),
    Path("data/raw/Kleist_sentence level.xlsx"),
]


def slugify_filename(name: str) -> str:
    base = name.replace(".xlsx", "").strip().lower()
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


def infer_scene_column(columns: list[str]) -> str:
    lowered = {c.lower(): c for c in columns}
    if "scene_id" in lowered:
        return lowered["scene_id"]
    if "scene" in lowered:
        return lowered["scene"]
    for c in columns:
        lc = c.lower()
        if "scene" in lc and "id" in lc:
            return c
    raise ValueError(f"Could not infer scene column from: {columns}")


def infer_sentence_id_column(columns: list[str]) -> str:
    lowered = {c.lower(): c for c in columns}
    for preferred in ("satz_id", "sent_nr", "sentence_nr", "sent_id"):
        if preferred in lowered:
            return lowered[preferred]
    for c in columns:
        lc = c.lower()
        if ("satz" in lc or "sent" in lc) and "id" in lc:
            return c
        if lc.endswith("_nr") or lc == "nr":
            return c
    raise ValueError(f"Could not infer sentence index column from: {columns}")


def infer_text_column(columns: list[str]) -> str:
    lowered = {c.lower(): c for c in columns}
    for preferred in ("sent_text", "sentence_text", "text"):
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


def derive_gold_rows(df: pd.DataFrame, source_name: str) -> list[dict[str, Any]]:
    columns = [str(c) for c in df.columns]
    scene_col = infer_scene_column(columns)
    sentence_id_col = infer_sentence_id_column(columns)
    text_col = infer_text_column(columns)

    records: list[dict[str, Any]] = []
    prev_scene = None
    for i, row in df.iterrows():
        text = clean_text(row.get(text_col))
        if not text:
            continue

        scene_raw = clean_text(row.get(scene_col))
        if not scene_raw:
            continue

        sentence_idx = coerce_int(row.get(sentence_id_col), fallback=i)
        is_border = prev_scene is None or scene_raw != prev_scene
        prev_scene = scene_raw

        records.append(
            {
                "sentence_index": sentence_idx,
                "sentence_text_full": text,
                "ground_truth_label": "BORDER" if is_border else "NOBORDER",
                "source_file": source_name,
                "scene_id_raw": scene_raw,
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
        "--excel_files",
        nargs="+",
        default=[str(p) for p in DEFAULT_EXCEL_FILES],
        help="Sentence-level Excel files to process.",
    )
    parser.add_argument(
        "--sheet_name",
        type=str,
        default="Sheet1",
        help="Sheet name to export (default: Sheet1).",
    )
    parser.add_argument(
        "--out_dir",
        type=Path,
        default=Path("data/processed/excel_prompting"),
        help="Output folder for processed inputs.",
    )
    parser.add_argument(
        "--manifest_out",
        type=Path,
        default=Path("data/processed/manifest_excel_prompting.json"),
        help="Manifest JSON output path.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = args.out_dir.expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_files: list[dict[str, Any]] = []
    profile_rows: list[dict[str, Any]] = []

    for excel_raw in args.excel_files:
        excel_path = Path(excel_raw).expanduser().resolve()
        if not excel_path.exists():
            raise FileNotFoundError(f"Excel not found: {excel_path}")

        slug = slugify_filename(excel_path.name)
        target_dir = out_dir / slug
        target_dir.mkdir(parents=True, exist_ok=True)

        df = pd.read_excel(excel_path, sheet_name=args.sheet_name)
        df.columns = [str(c).strip() for c in df.columns]

        csv_out = target_dir / f"{slug}__sheet1.csv"
        txt_out = target_dir / f"{slug}__for_prompting.txt"
        jsonl_out = target_dir / f"{slug}__for_prompting.jsonl"
        gold_out = target_dir / f"{slug}__gold_labels.csv"

        df.to_csv(csv_out, index=False, encoding="utf-8")
        gold_rows = derive_gold_rows(df, source_name=excel_path.name)

        txt_lines = [row["sentence_text_full"] for row in gold_rows]
        txt_out.write_text("\n".join(txt_lines) + "\n", encoding="utf-8")

        prompting_rows = [
            {
                "sentence_index": row["sentence_index"],
                "sentence_text_full": row["sentence_text_full"],
                "source_file": row["source_file"],
            }
            for row in gold_rows
        ]
        write_jsonl(jsonl_out, prompting_rows)

        with gold_out.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "sentence_index",
                    "sentence_text_full",
                    "ground_truth_label",
                    "source_file",
                    "scene_id_raw",
                ],
            )
            writer.writeheader()
            writer.writerows(gold_rows)

        manifest_files.append(
            {
                "name": str(txt_out.relative_to(Path("data"))),
                "size_bytes": txt_out.stat().st_size,
                "md5": md5sum(txt_out),
            }
        )
        profile_rows.append(
            {
                "excel_file": str(excel_path),
                "sheet": args.sheet_name,
                "rows_raw": int(len(df)),
                "rows_used": int(len(gold_rows)),
                "csv_out": str(csv_out),
                "txt_out": str(txt_out),
                "jsonl_out": str(jsonl_out),
                "gold_out": str(gold_out),
            }
        )
        print(f"Processed: {excel_path.name} -> {target_dir}")

    manifest = {
        "dataset": "excel_prompting_inputs",
        "source": "local/excel_sentence_level",
        "retrieved_at": date.today().isoformat(),
        "files": manifest_files,
    }
    args.manifest_out.parent.mkdir(parents=True, exist_ok=True)
    args.manifest_out.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    profile_out = out_dir / "processing_report.json"
    profile_out.write_text(
        json.dumps({"workbooks": profile_rows}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote manifest: {args.manifest_out}")
    print(f"Wrote processing report: {profile_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
