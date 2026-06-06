#!/usr/bin/env bash
# Phase C: deepen the headline combo (Nemotron-Super, family B) with one
# full-stratified baseline run, plus pilot-scope factor screening for E3/E4/E6.
# Single-factor-at-a-time; baseline = locked Phase A/B controls.
set -u

MODEL="nvidia/nemotron-3-super-120b-a12b:free"
FAMILY="B"
SCHEMA_OBJ="src/prompts/json_schema_label_reason.json"
PY=.venv-gpu/bin/python
RUNNER="src/runners/run_prompting_stratified.py"
LOG_DIR="logs/phaseC"
mkdir -p "$LOG_DIR"

# Locked Phase A/B controls
TEMP=0
TOP_P=1.0
SEED=1337
MAX_TOKENS=256
CHUNK_WIN=2
SCORE_TH=50
REASONING="low"

run_one () {
  local TAG="$1"; local DATE_TAG="$2"; shift; shift
  local LOG="$LOG_DIR/${TAG}.log"
  echo "[$(date +%H:%M:%S)] >>> $TAG date=$DATE_TAG log=$LOG extra=$*"
  $PY "$RUNNER" \
    --model "$MODEL" \
    --prompt_family "$FAMILY" \
    --reasoning "$REASONING" \
    --temperature $TEMP --top_p $TOP_P --seed $SEED --max_tokens $MAX_TOKENS \
    --response_format json_schema --schema_file $SCHEMA_OBJ \
    --chunk_window $CHUNK_WIN --score_threshold $SCORE_TH \
    --date "$DATE_TAG" \
    "$@" \
    > "$LOG" 2>&1
  local STATUS=$?
  echo "[$(date +%H:%M:%S)] <<< $TAG exit=$STATUS"
}

echo "[$(date +%H:%M:%S)] Phase C start: model=$MODEL family=$FAMILY"

# Headline: full-stratified baseline of the headline (model, family) combo.
# (Locked controls; varying factor: max_per_class 15 -> 0)
run_one "baseline_B_full" "2026-05-15-phaseC-baselineB-full" --max_per_class 0

# Factor pilots (max_per_class=15) — one factor at a time.
# E3 context window
run_one "E3_ctx1024" "2026-05-15-phaseC-E3-ctx1024" --max_per_class 15 --context_size 1024
run_one "E3_ctx2048" "2026-05-15-phaseC-E3-ctx2048" --max_per_class 15 --context_size 2048

# E4 temperature
run_one "E4_temp03" "2026-05-15-phaseC-E4-temp03" --max_per_class 15 --temperature 0.3
run_one "E4_temp10" "2026-05-15-phaseC-E4-temp10" --max_per_class 15 --temperature 1.0

# E6 reasoning (off only; "on" risks token-budget saturation per Phase B finding)
run_one "E6_reasoning_off" "2026-05-15-phaseC-E6-roff" --max_per_class 15 --reasoning off

echo "[$(date +%H:%M:%S)] Phase C finished"
