#!/usr/bin/env bash
# Stage 1 OFAT: model sweep on Excel corpus (Gänsemagd + Kleist).
# Varies model only; all other controls locked to Family B baseline.
#
# Resume: set RESUME=1 (default) to skip models whose summary.json has run_complete=true.
# Re-run the same DATE_TAG to continue interrupted models (per-sentence cache resumes automatically).
#
# Usage:
#   OPENROUTER_API_KEY=... bash scripts/sweeps/excel_ofat_stage1_models.sh
#   DATE_TAG=2026-06-14-excel-ofat-s1 RESUME=1 bash scripts/sweeps/excel_ofat_stage1_models.sh
set -u

DATE_TAG="${DATE_TAG:-2026-06-14-excel-ofat-s1}"
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

# Order: less congested free models first (smoke-tested / niche), heavily rate-limited
# free tiers last, then paid models (own quota, no shared :free pool).
MODELS=(
  "nvidia/nemotron-3-super-120b-a12b:free"
  "nvidia/nemotron-3-nano-30b-a3b:free"
  "poolside/laguna-xs.2:free"
  "poolside/laguna-m.1:free"
  "nex-agi/nex-n2-pro:free"
  "openai/gpt-oss-120b:free"
  "openrouter/owl-alpha"
  "nvidia/nemotron-3-ultra-550b-a55b:free"
  "meta-llama/llama-3.3-70b-instruct:free"
  "meta-llama/llama-3.1-8b-instruct"
  "openai/gpt-oss-20b"
  "openai/gpt-oss-120b"
  "qwen/qwen3.5-flash-02-23"
  "google/gemma-4-26b-a4b-it"
)

echo "[$(date +%H:%M:%S)] Excel OFAT Stage 1: ${#MODELS[@]} models, date=$DATE_TAG, resume=$RESUME"

for MODEL in "${MODELS[@]}"; do
  SAFE_M=$(echo "$MODEL" | tr '/:' '__')
  RUN_DIR="$OUT_ROOT/full_${SAFE_M}_familyB_reasoning-off"
  SUMMARY="$RUN_DIR/summary.json"
  LOG="$LOG_DIR/stage1_${SAFE_M}.log"

  if [ "$RESUME" = "1" ] && [ -f "$SUMMARY" ]; then
    if $PY -c "import json,sys; s=json.load(open('$SUMMARY')); sys.exit(0 if s.get('run_complete') else 1)"; then
      echo "[$(date +%H:%M:%S)] skip complete model=$MODEL"
      continue
    fi
    echo "[$(date +%H:%M:%S)] resume partial model=$MODEL (see $RUN_DIR/progress.json)"
  fi

  echo "[$(date +%H:%M:%S)] >>> model=$MODEL log=$LOG"
  $PY "$RUNNER" \
    --excel_manifest "$MANIFEST" \
    --model "$MODEL" \
    --prompt_family B \
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
    continue
  fi
done

echo "[$(date +%H:%M:%S)] Stage 1 finished. Aggregate with:"
echo "  $PY scripts/evaluation/summarize_excel_ofat.py --run_root $OUT_ROOT"
