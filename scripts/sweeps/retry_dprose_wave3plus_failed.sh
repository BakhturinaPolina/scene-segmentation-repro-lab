#!/usr/bin/env bash
# Retry parse-failed sentence keys across Wave 2 + Wave 3 books (optional; not required for 95% gate).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

DATE_TAG="$(date +%Y-%m-%d)"
LOG_DIR="logs/dprose"
LOG_FILE="${LOG_DIR}/retry_failed_${DATE_TAG}_wave3plus.log"

mkdir -p "$LOG_DIR"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

export PYTHONUNBUFFERED=1

# Books with remaining parse failures (19 books / ~37 keys after partial 2026-07-01 pass).
BOOKS="dprose_221,dprose_293,dprose_435,dprose_516,dprose_555,dprose_615,dprose_697,dprose_757,dprose_764,dprose_802,dprose_838,dprose_898,dprose_904,dprose_906,dprose_926,dprose_979,dprose_989,dprose_1019,dprose_1023"

CMD=(
  .venv/bin/python -u src/runners/run_dprose_batch_corpus.py
  --wave_manifest data/manifests/waves/wave_03_eur100.json
  --full_manifest data/manifests/dprose_full.json
  --books "$BOOKS"
  --retry_failed
  --resume
  --max_output_tokens 4096
  --max_cost_usd 200
  --output_root outputs/runs/dprose_batch/dprose-full-corpus
)

echo "Log file: $LOG_FILE"
echo "Command: ${CMD[*]}"
"${CMD[@]}" 2>&1 | tee -a "$LOG_FILE"
