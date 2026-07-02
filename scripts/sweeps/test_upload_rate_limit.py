#!/usr/bin/env python3
"""Smoke-test RateLimitedFile throughput (no API calls)."""

from __future__ import annotations

import sys
import tempfile
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.runners.dprose_batch_core import RateLimitedFile

KBPS = 250
SIZE_BYTES = 1024 * 1024  # 1 MiB
TOLERANCE = 0.20  # allow 20% timing slack


def main() -> int:
    data = b"x" * SIZE_BYTES
    with tempfile.NamedTemporaryFile(delete=False) as handle:
        handle.write(data)
        path = handle.name

    start = time.monotonic()
    with RateLimitedFile(path, kbps=KBPS) as limited:
        total = 0
        while True:
            chunk = limited.read(65536)
            if not chunk:
                break
            total += len(chunk)
    elapsed = time.monotonic() - start

    expected = SIZE_BYTES / (KBPS * 1024)
    ratio = elapsed / expected
    print(f"Read {total} bytes at {KBPS} KB/s cap")
    print(f"Elapsed: {elapsed:.2f}s  expected: ~{expected:.2f}s  ratio: {ratio:.2f}")

    Path(path).unlink(missing_ok=True)

    if total != SIZE_BYTES:
        print("FAIL: incomplete read", file=sys.stderr)
        return 1
    if ratio < (1.0 - TOLERANCE):
        print("FAIL: faster than cap (throttle not applied?)", file=sys.stderr)
        return 1
    if ratio > (1.0 + TOLERANCE):
        print("FAIL: much slower than cap", file=sys.stderr)
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
