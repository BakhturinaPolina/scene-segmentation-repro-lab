"""Unit tests for STSS-Test-2 data manifest verification."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.verify_data_manifest import md5sum, verify_manifest


class DataManifestTests(unittest.TestCase):
    def test_verify_manifest_success(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            data_dir = root / "data"
            data_dir.mkdir(parents=True)
            file_path = data_dir / "sample.xmi.zip"
            file_path.write_bytes(b"abc123")
            manifest_path = root / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "dataset": "stss_test_2",
                        "files": [
                            {
                                "name": "sample.xmi.zip",
                                "size_bytes": 6,
                                "md5": md5sum(file_path),
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual(verify_manifest(manifest_path, data_dir), [])

    def test_verify_manifest_reports_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            data_dir = root / "data"
            data_dir.mkdir(parents=True)
            file_path = data_dir / "sample.xmi.zip"
            file_path.write_bytes(b"abc123")
            manifest_path = root / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "dataset": "stss_test_2",
                        "files": [
                            {
                                "name": "sample.xmi.zip",
                                "size_bytes": 999,
                                "md5": "deadbeef",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            errors = verify_manifest(manifest_path, data_dir)
            self.assertTrue(any("size mismatch" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
