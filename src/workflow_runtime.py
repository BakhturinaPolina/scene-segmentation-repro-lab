"""Shared runtime helpers for reproducible research workflows."""

from __future__ import annotations

import json
import shlex
from pathlib import Path
from typing import Any, Sequence


def project_root(from_file: Path) -> Path:
    """Return repository root from a script path inside src/."""
    return from_file.resolve().parent.parent


def upstream_root(root: Path) -> Path:
    return root / "upstream" / "scene-segmentation"


def stss_test2_data_dir(root: Path) -> Path:
    return upstream_root(root) / "data" / "full" / "stss_test_2"


def output_dir_for(root: Path, track: str, run_date: str, run_slug: str) -> Path:
    return root / "outputs" / track / run_date / run_slug


def command_string(argv: Sequence[str]) -> str:
    return " ".join(shlex.quote(arg) for arg in argv)


def write_repro_files(output_dir: Path, argv: Sequence[str], config: dict[str, Any]) -> None:
    """Write command/config files required for reproducibility."""
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "command.txt").write_text(command_string(argv) + "\n", encoding="utf-8")
    (output_dir / "config.json").write_text(
        json.dumps(config, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
