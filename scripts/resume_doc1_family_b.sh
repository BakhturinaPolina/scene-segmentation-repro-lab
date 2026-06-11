#!/usr/bin/env bash
# Resume 2026-06-06 family-B full eval on doc 1 only (Aus guter Familie).
# Safe to re-run after daily OpenRouter quota reset; skips cached sentences.
#
# Quota plan (single job, 2000 free calls/day):
#   night 1 → ~3623/5025
#   night 2 → 5025/5025 (doc 1 done; does not start Effi Briest)
set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [ -z "${OPENROUTER_API_KEY:-}" ]; then
  echo "ERROR: OPENROUTER_API_KEY not set"
  exit 1
fi

DATE_TAG="${DATE_TAG:-2026-06-06}"
DOC="${DOC:-Aus guter Familie}"
MODEL="${MODEL:-nvidia/nemotron-3-super-120b-a12b:free}"
PY="${PY:-.venv/bin/python}"
LOG="${LOG:-outputs/runs/prompting/${DATE_TAG}/nemotron-super-120b-reasoning-off.log}"

mkdir -p "$(dirname "$LOG")"

echo "[$(date +%H:%M:%S)] resume doc1 family B: date=$DATE_TAG doc=$DOC log=$LOG"

exec "$PY" src/runners/run_prompting_stratified.py \
  --full_eval \
  --prompt_family B \
  --model "$MODEL" \
  --reasoning off \
  --temperature 0.0 \
  --date "$DATE_TAG" \
  --documents "$DOC" \
  >> "$LOG" 2>&1
