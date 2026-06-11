#!/usr/bin/env bash
# E4 negative-sampling sweep: hard mode + pct at 5/10/20/30/50%.
# One factor at a time; all other controls locked to E1 anchor defaults.
#
# Usage:
#   HF_USER=your-user bash scripts/sweeps/e4_negative_sweep.sh
#   DRY_RUN=1 bash scripts/sweeps/e4_negative_sweep.sh
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SUBMIT="$ROOT/src/finetune/hf_jobs/submit_job.sh"
HF_USER="${HF_USER:?Set HF_USER or run hf auth login}"
DATA_SCOPE="${DATA_SCOPE:-corpus}"
COMPUTE="${COMPUTE:-jobs}"
FLAVOR="${FLAVOR:-t4-small}"
TIMEOUT="${TIMEOUT:-8h}"
DRY_RUN="${DRY_RUN:-0}"

declare -a RUNS=(
  "E4_hard.json|--negative_mode hard --hard_window 3"
  "E4_pct05.json|--negative_mode pct --negative_pct 0.05"
  "E4_pct10.json|--negative_mode pct --negative_pct 0.10"
  "E4_pct20.json|--negative_mode pct --negative_pct 0.20"
  "E4_pct30.json|--negative_mode pct --negative_pct 0.30"
  "E4_pct50.json|--negative_mode pct --negative_pct 0.50"
)

echo "[$(date +%H:%M:%S)] E4 negative sweep start: user=$HF_USER scope=$DATA_SCOPE"

for entry in "${RUNS[@]}"; do
  CONFIG="${entry%%|*}"
  BUILD_ARGS="${entry#*|}"
  echo "[$(date +%H:%M:%S)] >>> $CONFIG BUILD_ARGS=\"$BUILD_ARGS\""
  if [ "$DRY_RUN" = "1" ]; then
    echo "    (dry run — skipping submit)"
    continue
  fi
  HF_USER="$HF_USER" DATA_SCOPE="$DATA_SCOPE" COMPUTE="$COMPUTE" FLAVOR="$FLAVOR" TIMEOUT="$TIMEOUT" \
    BUILD_ARGS="$BUILD_ARGS" \
    RUN_CONFIG="$ROOT/src/finetune/hf_jobs/configs/$CONFIG" \
    bash "$SUBMIT"
  echo "[$(date +%H:%M:%S)] <<< $CONFIG done"
done

echo "[$(date +%H:%M:%S)] E4 negative sweep finished."
