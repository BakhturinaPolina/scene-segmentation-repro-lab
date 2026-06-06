"""Verify local STSS-Test-2 files against a pinned manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


def md5sum(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_manifest(manifest_path: Path, data_dir: Path) -> list[str]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    files = manifest.get("files", [])
    if not isinstance(files, list):
        return ["Manifest field 'files' must be a list."]

    for entry in files:
        if not isinstance(entry, dict):
            errors.append("Manifest contains non-object file entry.")
            continue
        name = entry.get("name")
        expected_size = entry.get("size_bytes")
        expected_md5 = entry.get("md5")
        if not isinstance(name, str):
            errors.append("Manifest file entry is missing string 'name'.")
            continue
        if not isinstance(expected_size, int):
            errors.append(f"{name}: missing integer 'size_bytes'.")
            continue
        if not isinstance(expected_md5, str):
            errors.append(f"{name}: missing string 'md5'.")
            continue

        path = data_dir / name
        if not path.exists():
            errors.append(f"{name}: missing file at {path}.")
            continue

        actual_size = path.stat().st_size
        if actual_size != expected_size:
            errors.append(
                f"{name}: size mismatch (expected {expected_size}, got {actual_size})."
            )
            continue

        actual_md5 = md5sum(path)
        if actual_md5 != expected_md5:
            errors.append(
                f"{name}: md5 mismatch (expected {expected_md5}, got {actual_md5})."
            )

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("data/manifests/stss_test_2.json"),
        help="Path to dataset manifest JSON.",
    )
    parser.add_argument(
        "--data_dir",
        type=Path,
        default=Path("upstream/scene-segmentation/data/full/stss_test_2"),
        help="Directory containing local STSS-Test-2 XMI files.",
    )
    args = parser.parse_args(argv)

    errors = verify_manifest(args.manifest, args.data_dir)
    if errors:
        print("STSS-Test-2 manifest verification: FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("STSS-Test-2 manifest verification: OK")
    print(f"- manifest: {args.manifest}")
    print(f"- data_dir: {args.data_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
