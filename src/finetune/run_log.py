"""Shared logging, progress, and resumability helpers for the finetune pipeline."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Set, Tuple, TypeVar

T = TypeVar("T")

_LEVELS = {"debug": 10, "info": 20, "warning": 30, "error": 40}


def _level_num(level: str) -> int:
    return _LEVELS.get(level.lower(), 20)


def _min_level() -> int:
    return _level_num(os.environ.get("LOG_LEVEL", "info"))


def log(msg: str, *, level: str = "info") -> None:
    """Print a timestamped message with immediate flush."""
    if _level_num(level) < _min_level():
        return
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{ts}] [{level.upper()}] {msg}", flush=True)


def progress(iterable: Iterable[T], desc: str = "", **kwargs: Any) -> Iterator[T]:
    """tqdm wrapper defaulting to stdout with periodic refresh."""
    try:
        from tqdm import tqdm  # noqa: PLC0415
    except ImportError:
        log(f"tqdm not installed; running without progress bar ({desc})", level="warning")
        yield from iterable
        return

    defaults = {"desc": desc, "mininterval": 1.0, "file": sys.stdout, "dynamic_ncols": True}
    defaults.update(kwargs)
    yield from tqdm(iterable, **defaults)


def append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        handle.flush()


def load_completed_keys(path: Path, key_fields: Tuple[str, ...] = ("source", "index")) -> Set[str]:
    """Return set of 'field1:field2:...' keys already present in a JSONL cache."""
    if not path.exists():
        return set()
    keys: Set[str] = set()
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            parts = [str(row.get(f, "")) for f in key_fields]
            keys.add(":".join(parts))
    return keys


def row_key(row: dict, key_fields: Tuple[str, ...] = ("source", "index")) -> str:
    return ":".join(str(row.get(f, "")) for f in key_fields)


def upload_if_hub(
    path: Path,
    repo: str,
    token: str,
    *,
    path_in_repo: Optional[str] = None,
    repo_type: str = "model",
) -> bool:
    """Best-effort upload of a single file to the Hub."""
    if not path.exists() or not repo or not token:
        return False
    try:
        from huggingface_hub import upload_file  # noqa: PLC0415

        upload_file(
            path_or_fileobj=str(path),
            path_in_repo=path_in_repo or path.name,
            repo_id=repo,
            token=token,
            repo_type=repo_type,
        )
        log(f"Uploaded {path.name} -> {repo}")
        return True
    except Exception as exc:  # noqa: BLE001
        log(f"Could not upload {path} to {repo}: {exc}", level="warning")
        return False


class RunState:
    """Track completed (model, job) pairs for resumable multi-job runs."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.entries: List[Dict[str, Any]] = []
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    self.entries = data
            except Exception:  # noqa: BLE001
                self.entries = []

    def is_done(self, model: str, job: str) -> bool:
        for entry in self.entries:
            if entry.get("model") == model and entry.get("job") == job and entry.get("status") == "ok":
                return True
        return False

    def record(
        self,
        model: str,
        job: str,
        *,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> None:
        ts = datetime.now(timezone.utc).isoformat()
        self.entries.append(
            {
                "model": model,
                "job": job,
                "status": status,
                "timestamp": ts,
                "result": result,
                "error": error,
            }
        )
        self.flush()

    def flush(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(self.entries, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
