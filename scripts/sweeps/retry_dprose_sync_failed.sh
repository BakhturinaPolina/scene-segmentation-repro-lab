#!/usr/bin/env bash
# Sync API retry for remaining parse-failed dProse keys (non-batch).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

DATE_TAG="$(date +%Y-%m-%d)"
LOG_DIR="logs/dprose"
LOG_FILE="${LOG_DIR}/sync_retry_failed_${DATE_TAG}.log"
KEYS_FILE="data/manifests/dprose_sync_retry_keys.json"
RUN_NOTE="research_log/runs/${DATE_TAG}__prompting__retry__dprose-sync-failed.md"

mkdir -p "$LOG_DIR" data/manifests

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

export PYTHONUNBUFFERED=1

# Snapshot keys for reproducibility
.venv/bin/python - <<'PY' > "$KEYS_FILE"
import json
from pathlib import Path

keys = []
for br in Path("outputs/runs/dprose_batch/dprose-full-corpus/books").glob("*/book_review.json"):
    d = json.loads(br.read_text())
    keys.extend(d.get("failed_keys") or [])
keys = sorted(keys, key=lambda k: (int(k.split("_")[1].split(":")[0]), int(k.split(":")[1])))
print(json.dumps({"keys": keys, "count": len(keys)}, indent=2) + "\n")
PY

CMD=(
  .venv/bin/python -u src/runners/run_dprose_sync_retry.py
  --keys_file "$KEYS_FILE"
  --max_output_tokens 8192
  --thinking_budget 1024
  --sleep_seconds 1
  --output_root outputs/runs/dprose_batch/dprose-full-corpus
)

if [[ "${DRY_RUN:-0}" == "1" ]]; then
  CMD+=(--dry_run)
fi

echo "Log file: $LOG_FILE"
echo "Keys file: $KEYS_FILE"
echo "Research run note: $RUN_NOTE"
echo "Command: ${CMD[*]}"
"${CMD[@]}" 2>&1 | tee -a "$LOG_FILE"
