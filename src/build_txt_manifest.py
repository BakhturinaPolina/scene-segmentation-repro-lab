"""Build a manifest for local TXT files in data/raw."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date
from pathlib import Path


def md5sum(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest(dataset: str, source: str, data_dir: Path) -> dict[str, object]:
    files = []
    for txt_path in sorted(data_dir.glob("*.txt")):
        files.append(
            {
                "name": txt_path.name,
                "size_bytes": txt_path.stat().st_size,
                "md5": md5sum(txt_path),
            }
        )
    return {
        "dataset": dataset,
        "source": source,
        "retrieved_at": date.today().isoformat(),
        "files": files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset",
        type=str,
        default="raw_txt",
        help="Manifest dataset identifier (default: raw_txt).",
    )
    parser.add_argument(
        "--source",
        type=str,
        default="local/raw_text",
        help="Data source description (default: local/raw_text).",
    )
    parser.add_argument(
        "--data_dir",
        type=Path,
        default=Path("data/raw"),
        help="Directory with source TXT files (default: data/raw).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/manifest_raw_txt.json"),
        help="Output manifest path (default: data/manifest_raw_txt.json).",
    )
    args = parser.parse_args()

    if not args.data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {args.data_dir}")

    manifest = build_manifest(args.dataset, args.source, args.data_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote manifest: {args.output}")
    print(f"Files listed: {len(manifest['files'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
