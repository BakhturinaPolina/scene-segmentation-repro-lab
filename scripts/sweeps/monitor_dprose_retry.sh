#!/usr/bin/env bash
# Append retry progress snapshots to the retry log (for runs not launched via tee).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

LOG_FILE="${1:-logs/dprose/retry_failed_$(date +%Y-%m-%d).log}"
PID="${2:-}"
INTERVAL="${3:-120}"

monitor_once() {
  .venv/bin/python - <<'PY'
import json
from pathlib import Path
from datetime import datetime, timezone

books_dir = Path("outputs/runs/dprose_batch/dprose-full-corpus/books")
retry_slugs = []
for br in books_dir.glob("*/book_review.json"):
    d = json.loads(br.read_text())
    if d["failed_keys"]:
        retry_slugs.append(br.parent.name)
retry_slugs.sort(key=lambda s: int(s.split("_")[1]))

total_keys = sum(
    len(json.loads((books_dir / s / "book_review.json").read_text())["failed_keys"])
    for s in retry_slugs
)

in_flight = []
for slug in retry_slugs:
    jm = books_dir / slug / "job_meta.json"
    pred = books_dir / slug / "predictions.jsonl"
    if jm.exists() and jm.stat().st_mtime > pred.stat().st_mtime if pred.exists() else True:
        d = json.loads(jm.read_text())
        in_flight.append(f"{slug}({d.get('request_count', '?')} reqs @ {d.get('submitted_at', '?')[:19]})")

ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
print(f"[monitor {ts}] failed_keys={total_keys} books_remaining={len(retry_slugs)} in_flight={len(in_flight)}")
if in_flight:
    print(f"  polling: {', '.join(in_flight[:5])}{'...' if len(in_flight) > 5 else ''}")
PY
}

while true; do
  if [[ -n "$PID" ]] && ! kill -0 "$PID" 2>/dev/null; then
    {
      echo ""
      echo "=== MONITOR: PID $PID exited $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
      monitor_once
    } >> "$LOG_FILE"
    exit 0
  fi
  {
    echo ""
    monitor_once
  } >> "$LOG_FILE"
  sleep "$INTERVAL"
done
