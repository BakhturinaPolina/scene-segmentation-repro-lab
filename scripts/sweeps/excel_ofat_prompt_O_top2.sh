#!/usr/bin/env bash
# Stage 3-O: full_eval with German fairy few-shot prompt on top Q models.
set -u

DATE_TAG="${DATE_TAG:-2026-06-14-excel-ofat-O}"
PROMPT_FAMILY="${PROMPT_FAMILY:-O}"
RESUME="${RESUME:-1}"
TEMP=0
TOP_P=1.0
SEED=1337
MAX_TOKENS=256
CONTEXT=409
PY="${PY:-.venv/bin/python}"
RUNNER="src/runners/run_prompting_stratified.py"
MANIFEST="data/manifests/excel_prompting.json"
LOG_DIR="logs/excel_ofat"
OUT_ROOT="outputs/runs/prompting/$DATE_TAG"
mkdir -p "$LOG_DIR"

MODELS=(
  "nvidia/nemotron-3-super-120b-a12b:free"
  "poolside/laguna-xs.2:free"
)

echo "[$(date +%H:%M:%S)] Prompt family $PROMPT_FAMILY: ${#MODELS[@]} models, date=$DATE_TAG"

for MODEL in "${MODELS[@]}"; do
  SAFE_M=$(echo "$MODEL" | tr '/:' '__')
  RUN_DIR="$OUT_ROOT/full_${SAFE_M}_family${PROMPT_FAMILY}_reasoning-off"
  SUMMARY="$RUN_DIR/summary.json"
  LOG="$LOG_DIR/prompt_${PROMPT_FAMILY}_${SAFE_M}.log"

  if [ "$RESUME" = "1" ] && [ -f "$SUMMARY" ]; then
    if $PY -c "import json,sys; s=json.load(open('$SUMMARY')); sys.exit(0 if s.get('run_complete') else 1)"; then
      echo "[$(date +%H:%M:%S)] skip complete model=$MODEL"
      continue
    fi
    echo "[$(date +%H:%M:%S)] resume partial model=$MODEL"
  fi

  echo "[$(date +%H:%M:%S)] >>> model=$MODEL family=$PROMPT_FAMILY"
  $PY "$RUNNER" \
    --excel_manifest "$MANIFEST" \
    --model "$MODEL" \
    --prompt_family "$PROMPT_FAMILY" \
    --full_eval \
    --apply_model_profile \
    --reasoning off \
    --temperature $TEMP --top_p $TOP_P --seed $SEED --max_tokens $MAX_TOKENS \
    --context_size $CONTEXT \
    --context_mode tokens \
    --date "$DATE_TAG" \
    --request_delay 0.5 \
    --rate_limit_cooldown 180 \
    >> "$LOG" 2>&1
  STATUS=$?
  echo "[$(date +%H:%M:%S)] <<< model=$MODEL exit=$STATUS"
  if [ "$STATUS" -eq 2 ]; then
    echo "[$(date +%H:%M:%S)] guardrail abort — see $RUN_DIR/guardrail_failure.json"
  fi
done

echo "[$(date +%H:%M:%S)] Prompt O sweep done."
