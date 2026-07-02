#!/usr/bin/env bash
# Run a dProse prompting wave with logging.
#
# Optional upload cap (reduces home-network upload spikes for shared connections):
#   UPLOAD_RATE_KBPS=250 bash scripts/sweeps/run_dprose_wave.sh ...
# Uses trickle when installed; otherwise in-process throttling via --upload_rate_kbps.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

WAVE_MANIFEST="${1:-data/manifests/waves/wave_01_eur25.json}"
MAX_COST_USD="${2:-23}"
DRY_RUN="${DRY_RUN:-0}"
UPLOAD_RATE_KBPS="${UPLOAD_RATE_KBPS:-}"
DATE_TAG="$(date +%Y-%m-%d)"
WAVE_STEM="$(basename "${WAVE_MANIFEST}" .json)"
LOG_DIR="logs/dprose"
LOG_FILE="${LOG_DIR}/wave_${WAVE_STEM}_${DATE_TAG}.log"
RUN_NOTE="research_log/runs/${DATE_TAG}__prompting__experiment__dprose-full-${WAVE_STEM}.md"

mkdir -p "$LOG_DIR"

echo "Log file: $LOG_FILE"
echo "Research run note (create/update): $RUN_NOTE"
echo "Wave manifest: $WAVE_MANIFEST"
echo "Max cost USD: $MAX_COST_USD"
if [[ -n "$UPLOAD_RATE_KBPS" ]]; then
  echo "Upload cap: ${UPLOAD_RATE_KBPS} KB/s (~$(( UPLOAD_RATE_KBPS * 8 / 1000 )) Mbps)"
fi
echo "Started at: $(date -Iseconds)"

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

if [[ -n "$UPLOAD_RATE_KBPS" ]]; then
  CMD+=(--upload_rate_kbps "$UPLOAD_RATE_KBPS")
fi

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

export PYTHONUNBUFFERED=1

RUNNER=("${CMD[@]}")
if [[ -n "$UPLOAD_RATE_KBPS" ]] && command -v trickle >/dev/null 2>&1; then
  echo "Upload wrapper: trickle -u ${UPLOAD_RATE_KBPS}"
  RUNNER=(trickle -u "$UPLOAD_RATE_KBPS" "${CMD[@]}")
elif [[ -n "$UPLOAD_RATE_KBPS" ]]; then
  echo "Upload wrapper: in-process (--upload_rate_kbps; install trickle for LD_PRELOAD cap)"
fi

echo "Command: ${RUNNER[*]}"
"${RUNNER[@]}" 2>&1 | tee "$LOG_FILE"
