"""Shared runtime helpers for reproducible research workflows."""

from __future__ import annotations

import json
import shlex
from pathlib import Path
from typing import Any, Sequence


def src_root(from_file: Path) -> Path:
    """Return the ``src/`` directory containing a script or module path."""
    resolved = from_file.resolve()
    for parent in (resolved.parent, *resolved.parents):
        if parent.name == "src":
            return parent
    raise ValueError(f"Could not locate src root from {from_file}")


def project_root(from_file: Path) -> Path:
    """Return repository root from a path under ``src/``."""
    return src_root(from_file).parent


def prompts_dir(from_file: Path) -> Path:
    """Return the default prompt templates directory."""
    return src_root(from_file) / "prompts"


def upstream_root(root: Path) -> Path:
    return root / "upstream" / "scene-segmentation"


def stss_test2_data_dir(root: Path) -> Path:
    return upstream_root(root) / "data" / "full" / "stss_test_2"


def output_dir_for(root: Path, track: str, run_date: str, run_slug: str) -> Path:
    """Return the standard output directory for a workflow track."""
    if track == "reproduction":
        return root / "outputs" / "reproduction" / run_date / run_slug
    return root / "outputs" / "runs" / track / run_date / run_slug


def prompting_run_root(root: Path, run_date: str) -> Path:
    """Return the date-level directory for prompting runs."""
    return root / "outputs" / "runs" / "prompting" / run_date


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
