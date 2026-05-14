"""Unit tests for reproducibility runtime helpers."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.workflow_runtime import (
    command_string,
    output_dir_for,
    project_root,
    stss_test2_data_dir,
    write_repro_files,
)


class WorkflowRuntimeTests(unittest.TestCase):
    def test_project_root_from_src_file(self) -> None:
        fake_script = Path("/tmp/repo/src/my_script.py")
        self.assertEqual(project_root(fake_script), Path("/tmp/repo"))

    def test_stss_test2_data_dir(self) -> None:
        root = Path("/tmp/repo")
        expected = root / "upstream" / "scene-segmentation" / "data" / "full" / "stss_test_2"
        self.assertEqual(stss_test2_data_dir(root), expected)

    def test_output_dir_for(self) -> None:
        root = Path("/tmp/repo")
        out_dir = output_dir_for(root, "prompting", "2026-05-14", "baseline_qwen3")
        self.assertEqual(
            out_dir,
            Path("/tmp/repo/outputs/prompting/2026-05-14/baseline_qwen3"),
        )

    def test_write_repro_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir) / "outputs" / "prompting" / "demo"
            argv = ["python", "src/run_prompting.py", "--dry_run", "5"]
            config = {"dry_run": 5, "model": "openrouter/free"}
            write_repro_files(output_dir, argv, config)

            command_txt = (output_dir / "command.txt").read_text(encoding="utf-8")
            config_json = json.loads((output_dir / "config.json").read_text(encoding="utf-8"))

            self.assertIn("python", command_txt)
            self.assertIn("--dry_run", command_txt)
            self.assertEqual(config_json["dry_run"], 5)
            self.assertEqual(config_json["model"], "openrouter/free")

    def test_command_string_quotes_spaces(self) -> None:
        cmd = command_string(["python", "my script.py", "--name", "A B"])
        self.assertIn("'my script.py'", cmd)
        self.assertIn("'A B'", cmd)


if __name__ == "__main__":
    unittest.main()
