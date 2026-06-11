#!/usr/bin/env bash
# F3 precision prompt sweep: control B vs precision variants K (negatives),
# L (strict definition), M (FP-pattern guard). One factor at a time; all other
# controls locked to the Step-2 protocol in
# research_log/experiments/experiment__improvement__f3-precision-campaign.md.
#
# Pilot scope by default (--max_per_class 15). Promote winners to a full run by
# setting MAX_PER_CLASS=0 and FULL_EVAL=1.
#
# Usage:
#   OPENROUTER_API_KEY=... bash scripts/sweeps/precision_prompt_sweep.sh
#   MAX_PER_CLASS=0 FULL_EVAL=1 bash scripts/sweeps/precision_prompt_sweep.sh
set -u  # do NOT set -e; if one family fails, continue with the rest.

DATE_TAG="${DATE_TAG:-$(date +%F)-precision}"
MODEL="${MODEL:-nvidia/nemotron-3-super-120b-a12b:free}"
MAX_PER_CLASS="${MAX_PER_CLASS:-15}"
FULL_EVAL="${FULL_EVAL:-0}"
REASONING="${REASONING:-off}"
TEMP=0
TOP_P=1.0
SEED=1337
MAX_TOKENS=256
CONTEXT=409
PY="${PY:-.venv/bin/python}"
RUNNER="src/runners/run_prompting_stratified.py"
LOG_DIR="logs/precision"
mkdir -p "$LOG_DIR"

EVAL_ARGS=""
if [ "$FULL_EVAL" = "1" ]; then
  EVAL_ARGS="--full_eval"
else
  EVAL_ARGS="--max_per_class $MAX_PER_CLASS"
fi

echo "[$(date +%H:%M:%S)] precision sweep start: model=$MODEL date=$DATE_TAG eval=[$EVAL_ARGS]"

for FAMILY in B K L M; do
  LOG="$LOG_DIR/family_${FAMILY}.log"
  echo "[$(date +%H:%M:%S)] >>> family=$FAMILY log=$LOG"
  $PY "$RUNNER" \
    --model "$MODEL" \
    --prompt_family "$FAMILY" \
    $EVAL_ARGS \
    --reasoning "$REASONING" \
    --context_size $CONTEXT \
    --temperature $TEMP --top_p $TOP_P --seed $SEED --max_tokens $MAX_TOKENS \
    --response_format json_object \
    --date "$DATE_TAG" \
    > "$LOG" 2>&1
  echo "[$(date +%H:%M:%S)] <<< family=$FAMILY exit=$?"
done

echo "[$(date +%H:%M:%S)] precision sweep finished. Logs in $LOG_DIR/"
