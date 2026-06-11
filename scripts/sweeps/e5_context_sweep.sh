#!/usr/bin/env bash
# E5 context-length sweep: token budgets 768, 1024, 1536, 2048 (512 is E1 default).
# One factor at a time; all other controls locked to E1 anchor defaults.
#
# Usage:
#   HF_USER=your-user bash scripts/sweeps/e5_context_sweep.sh
#   DRY_RUN=1 bash scripts/sweeps/e5_context_sweep.sh
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
  "E5_budget768.json|--context_mode tokens512 --token_budget 768"
  "E5_budget1024.json|--context_mode tokens512 --token_budget 1024"
  "E5_budget1536.json|--context_mode tokens512 --token_budget 1536"
  "E5_budget2048.json|--context_mode tokens512 --token_budget 2048"
)

echo "[$(date +%H:%M:%S)] E5 context sweep start: user=$HF_USER scope=$DATA_SCOPE"

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

echo "[$(date +%H:%M:%S)] E5 context sweep finished."
