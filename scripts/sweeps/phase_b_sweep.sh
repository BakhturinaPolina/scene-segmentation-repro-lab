#!/usr/bin/env bash
# Phase B: kept families {B, E, D} on 3 NEW free models.
# Locked controls match Phase A so results are directly comparable to the carry-over
# Nemotron Super 120B numbers from outputs/runs/prompting/2026-05-15-phaseA/.
set -u

DATE_TAG="2026-05-15-phaseB"
MAX_PER_CLASS=15
REASONING="low"
TEMP=0
TOP_P=1.0
SEED=1337
MAX_TOKENS=256
CHUNK_WIN=2
SCORE_TH=50
SCHEMA_OBJ="src/prompts/json_schema_label_reason.json"
SCHEMA_ARR="src/prompts/json_schema_score_array.json"
PY=.venv-gpu/bin/python
RUNNER="src/runners/run_prompting_stratified.py"
LOG_DIR="logs/phaseB"
mkdir -p "$LOG_DIR"

MODELS=(
  "openai/gpt-oss-120b:free"
  "z-ai/glm-4.5-air:free"
  "google/gemma-4-31b-it:free"
)
FAMILIES=(B E D)

echo "[$(date +%H:%M:%S)] Phase B sweep start: families=${FAMILIES[*]} models=${#MODELS[@]} date=$DATE_TAG"

for MODEL in "${MODELS[@]}"; do
  for FAMILY in "${FAMILIES[@]}"; do
    case "$FAMILY" in
      A|H) RF_ARGS="--response_format none" ;;
      I)   RF_ARGS="--response_format json_schema --schema_file $SCHEMA_ARR" ;;
      *)   RF_ARGS="--response_format json_schema --schema_file $SCHEMA_OBJ" ;;
    esac
    SAFE_M=$(echo "$MODEL" | tr '/:' '__')
    LOG="$LOG_DIR/${SAFE_M}_family_${FAMILY}.log"
    echo "[$(date +%H:%M:%S)] >>> model=$MODEL family=$FAMILY log=$LOG"
    $PY "$RUNNER" \
      --model "$MODEL" \
      --prompt_family "$FAMILY" \
      --max_per_class $MAX_PER_CLASS \
      --reasoning "$REASONING" \
      --temperature $TEMP --top_p $TOP_P --seed $SEED --max_tokens $MAX_TOKENS \
      $RF_ARGS \
      --chunk_window $CHUNK_WIN --score_threshold $SCORE_TH \
      --date "$DATE_TAG" \
      > "$LOG" 2>&1
    STATUS=$?
    echo "[$(date +%H:%M:%S)] <<< model=$MODEL family=$FAMILY exit=$STATUS"
  done
done

echo "[$(date +%H:%M:%S)] Phase B sweep finished"
