#!/usr/bin/env bash
# Phase A: prompt-family sweep A..J on Nemotron Super 120B (single model).
# Locked controls match plan section "Fixed controls".
set -u  # do NOT set -e; if one family fails, continue with the rest.

DATE_TAG="2026-05-15-phaseA"
MODEL="nvidia/nemotron-3-super-120b-a12b:free"
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
LOG_DIR="logs/phaseA"
mkdir -p "$LOG_DIR"

echo "[$(date +%H:%M:%S)] Phase A sweep start: model=$MODEL date=$DATE_TAG"

for FAMILY in A B C D E F G H I J; do
  case "$FAMILY" in
    A|H) RF_ARGS="--response_format none" ;;
    I)   RF_ARGS="--response_format json_schema --schema_file $SCHEMA_ARR" ;;
    *)   RF_ARGS="--response_format json_schema --schema_file $SCHEMA_OBJ" ;;
  esac
  LOG="$LOG_DIR/family_${FAMILY}.log"
  echo "[$(date +%H:%M:%S)] >>> family=$FAMILY rf=[$RF_ARGS] log=$LOG"
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
  echo "[$(date +%H:%M:%S)] <<< family=$FAMILY exit=$STATUS"
done

echo "[$(date +%H:%M:%S)] Phase A sweep finished"
