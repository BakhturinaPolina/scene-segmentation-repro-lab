#!/usr/bin/env bash
# Resume Excel OFAT improvement pipeline (steps 1–4).
# 1. Finish prompt-O sweep if needed
# 2–4. verify (skip if review/verify_Q_*.json exist), postprocess, context windows
set -u

PY="${PY:-.venv/bin/python}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

echo "[$(date +%H:%M:%S)] Step 1: prompt O sweep"
DATE_TAG=2026-06-14-excel-ofat-O RESUME=1 bash scripts/sweeps/excel_ofat_prompt_O_top2.sh

echo "[$(date +%H:%M:%S)] Steps 2–4: pipeline"
if [ ! -f review/verify_Q_nemotron.json ] || [ ! -f review/verify_Q_laguna_xs.json ]; then
  $PY scripts/evaluation/excel_ofat_improve_pipeline.py --step verify
fi
$PY scripts/evaluation/excel_ofat_improve_pipeline.py --step postprocess
$PY scripts/evaluation/excel_ofat_improve_pipeline.py --step context

echo "[$(date +%H:%M:%S)] Done. See review/excel_ofat_pipeline_candidates.json"
