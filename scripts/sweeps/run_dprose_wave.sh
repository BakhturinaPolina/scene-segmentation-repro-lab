#!/usr/bin/env bash
# Run a dProse prompting wave with logging.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

WAVE_MANIFEST="${1:-data/manifests/waves/wave_01_eur25.json}"
MAX_COST_USD="${2:-23}"
DRY_RUN="${DRY_RUN:-0}"
DATE_TAG="$(date +%Y-%m-%d)"
LOG_DIR="logs/dprose"
LOG_FILE="${LOG_DIR}/wave_$(basename "${WAVE_MANIFEST}" .json)_${DATE_TAG}.log"
RUN_NOTE="research_log/runs/${DATE_TAG}__prompting__experiment__dprose-full-wave01.md"

mkdir -p "$LOG_DIR"

echo "Log file: $LOG_FILE"
echo "Research run note (create/update): $RUN_NOTE"
echo "Wave manifest: $WAVE_MANIFEST"
echo "Max cost USD: $MAX_COST_USD"

CMD=(
  .venv/bin/python -u src/runners/run_dprose_batch_corpus.py
  --wave_manifest "$WAVE_MANIFEST"
  --full_manifest data/manifests/dprose_full.json
  --output_root outputs/runs/dprose_batch/dprose-full-corpus
  --max_cost_usd "$MAX_COST_USD"
  --seed_pilot
  --resume
)

if [[ "$DRY_RUN" == "1" ]]; then
  CMD+=(--dry_run)
fi

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

export PYTHONUNBUFFERED=1
echo "Command: ${CMD[*]}"
"${CMD[@]}" 2>&1 | tee "$LOG_FILE"
