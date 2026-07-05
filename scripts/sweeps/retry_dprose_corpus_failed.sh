#!/usr/bin/env bash
# Corpus-wide retry of parse-failed sentence keys (optional; not required for 95% gate).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

DATE_TAG="$(date +%Y-%m-%d)"
LOG_DIR="logs/dprose"
LOG_FILE="${LOG_DIR}/retry_failed_${DATE_TAG}.log"
RUN_NOTE="research_log/runs/${DATE_TAG}__prompting__retry__dprose-corpus-failed.md"

mkdir -p "$LOG_DIR"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

export PYTHONUNBUFFERED=1

BOOKS="$(
  .venv/bin/python - <<'PY'
import json
from pathlib import Path

slugs = []
for br in Path("outputs/runs/dprose_batch/dprose-full-corpus/books").glob("*/book_review.json"):
    d = json.loads(br.read_text())
    if d["failed_keys"]:
        slugs.append(br.parent.name)
print(",".join(sorted(slugs, key=lambda s: int(s.split("_")[1]))))
PY
)"

if [[ -z "$BOOKS" ]]; then
  echo "No books with failed keys; nothing to retry."
  exit 0
fi

CMD=(
  .venv/bin/python -u src/runners/run_dprose_batch_corpus.py
  --wave_manifest data/manifests/dprose_full.json
  --full_manifest data/manifests/dprose_full.json
  --books "$BOOKS"
  --retry_failed
  --resume
  --max_output_tokens 4096
  --max_cost_usd 600
  --output_root outputs/runs/dprose_batch/dprose-full-corpus
)

if [[ "${DRY_RUN:-0}" == "1" ]]; then
  CMD+=(--dry_run)
fi

echo "Log file: $LOG_FILE"
echo "Research run note: $RUN_NOTE"
echo "Command: ${CMD[*]}"
"${CMD[@]}" 2>&1 | tee -a "$LOG_FILE"
