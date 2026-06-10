#!/usr/bin/env bash
# Build SFT data, upload to a private HF dataset, and submit a GPU Job (or run locally).
#
# One submission == one experiment. The job trains every (model x job) pair, runs
# in-job eval on each held-out split, and uploads adapters + metrics to the Hub.
#
# Data scope (see docs/planning/FINETUNING_EXPERIMENTS_PLAN.md §4):
#   DATA_SCOPE=pilot   — STSS-Test-2 folds only (debug / Pilot 0; default)
#   DATA_SCOPE=corpus  — paper-comparable train_full → stss_test_2 (requires full corpus)
#
# Prerequisites (one-time):
#   1. HF Pro account ($9/mo) — unlocks Jobs API and private dataset storage.
#   2. ``pip install huggingface_hub`` and ``hf auth login`` with a write token.
#   3. For cloud Jobs (optional): add prepaid credits at https://huggingface.co/settings/billing
#
# Default compute: LOCAL (free). Set COMPUTE=jobs for cloud GPUs (t4-small ≈ $0.40/hr).
#
# Usage examples:
#   # Pilot 0 / E0 smoke (STSS-Test-2 only, debug):
#   HF_USER=RuthonField DATA_SCOPE=pilot RUN_CONFIG=src/finetune/hf_jobs/configs/E0_smoke.json \
#     BUILD_MODE=skip bash src/finetune/hf_jobs/submit_job.sh
#
#   # Paper-comparable E1 (once full corpus is on disk):
#   HF_USER=RuthonField DATA_SCOPE=corpus RUN_CONFIG=src/finetune/hf_jobs/configs/E1_anchor.json \
#     BUILD_ARGS="--target_format cot_list --negative_mode paper10pct --context_mode tokens512" \
#     bash src/finetune/hf_jobs/submit_job.sh
#
#   # Cloud Job (prepaid credits):
#   HF_USER=RuthonField DATA_SCOPE=pilot COMPUTE=jobs FLAVOR=t4-small TIMEOUT=6h \
#     RUN_CONFIG=src/finetune/hf_jobs/configs/E0_smoke.json bash src/finetune/hf_jobs/submit_job.sh
set -euo pipefail

RESUME="${RESUME:-1}"
VERBOSE="${VERBOSE:-0}"
if [ "$VERBOSE" = "1" ]; then set -x; fi

_ts() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"

if [ -z "${HF_USER:-}" ]; then
  HF_USER="$(hf auth whoami 2>/dev/null | head -1 || true)"
fi
: "${HF_USER:?Set HF_USER or run hf auth login}"

DATASET_REPO="${DATASET_REPO:-${HF_USER}/scene-seg-sft}"
DATA_SCOPE="${DATA_SCOPE:-pilot}"          # pilot | corpus
BUILD_MODE="${BUILD_MODE:-}"               # auto from DATA_SCOPE if empty
BUILD_ARGS="${BUILD_ARGS:-}"
DATA_DIR="$ROOT/data/processed/finetune"
COMPUTE="${COMPUTE:-local}"                # local | jobs
FLAVOR="${FLAVOR:-t4-small}"
TIMEOUT="${TIMEOUT:-6h}"
DETACH="${DETACH:-1}"

case "$DATA_SCOPE" in
  pilot)
    BUILD_MODE="${BUILD_MODE:-folds}"
    JOBS="${JOBS:-fold_A}"
    BUILD_ARGS="${BUILD_ARGS:---target_format cot_list --negative_mode paper10pct}"
    echo "[scope] DATA_SCOPE=pilot — STSS-Test-2 folds only (debug; not paper-comparable)."
    ;;
  corpus)
    BUILD_MODE="${BUILD_MODE:-corpus}"
    JOBS="${JOBS:-train_full__to__stss_test_2}"
    BUILD_ARGS="${BUILD_ARGS:---train_split train_full --eval_split stss_test_2 --target_format cot_list --negative_mode paper10pct --context_mode tokens512}"
    CORPUS_DIR="${CORPUS_DIR:-$ROOT/upstream/scene-segmentation/data/full}"
    N_ZIPS="$(find "$CORPUS_DIR" -name '*.xmi.zip' 2>/dev/null | wc -l | tr -d ' ')"
    if [ "${N_ZIPS:-0}" -lt 10 ]; then
      echo "[scope] ERROR: DATA_SCOPE=corpus but only ${N_ZIPS:-0} XMI zips under $CORPUS_DIR."
      echo "        Place the full 41-text corpus there before E1+ (see FINETUNING_EXPERIMENTS_PLAN.md §4)."
      exit 1
    fi
    echo "[scope] DATA_SCOPE=corpus — paper-comparable (${N_ZIPS} zips found)."
    ;;
  *)
    echo "Unknown DATA_SCOPE=$DATA_SCOPE (use pilot|corpus)"; exit 1
    ;;
esac

MODELS="${MODELS:-unsloth/Llama-3.2-3B-Instruct}"

echo "[1/4] Building SFT dataset (scope=$DATA_SCOPE mode=$BUILD_MODE)..."
case "$BUILD_MODE" in
  folds)
    python "$ROOT/src/finetune/build_sft_dataset.py" --mode folds --fold both $BUILD_ARGS
    ;;
  corpus)
    python "$ROOT/src/finetune/build_sft_dataset.py" --mode corpus $BUILD_ARGS
    ;;
  skip)
    echo "      BUILD_MODE=skip; using existing $DATA_DIR"
    ;;
  *)
    echo "Unknown BUILD_MODE=$BUILD_MODE (use folds|corpus|skip)"; exit 1
    ;;
esac

echo "[2/4] Writing hf_run_config.json..."
CONFIG_PATH="$DATA_DIR/hf_run_config.json"
if [ -n "${RUN_CONFIG:-}" ]; then
  python - "$RUN_CONFIG" "$CONFIG_PATH" "$HF_USER" "$DATASET_REPO" "$DATA_SCOPE" "$DATA_DIR" <<'PY'
import json, re, sys
from pathlib import Path

src, dst, hf_user, data_repo, data_scope, data_dir = sys.argv[1:7]
cfg = json.load(open(src, encoding="utf-8"))
cfg.setdefault("hf_user", hf_user)
cfg.setdefault("data_repo", data_repo)
cfg.setdefault("data_scope", data_scope)
if data_scope == "pilot" and "debug" not in cfg:
    cfg["debug"] = True

if "max_seq_len" not in cfg:
    jobs = cfg.get("jobs") or []
    if jobs:
        meta_path = Path(data_dir) / jobs[0] / "meta.json"
        if meta_path.exists():
            meta = json.load(meta_path.open(encoding="utf-8"))
            if meta.get("max_seq_len_recommended"):
                cfg["max_seq_len"] = meta["max_seq_len_recommended"]
                print(f"Inferred max_seq_len={cfg['max_seq_len']} from {meta_path}")

json.dump(cfg, open(dst, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(f"Using RUN_CONFIG {src}: models={cfg.get('models')} jobs={cfg.get('jobs')} debug={cfg.get('debug')}")
PY
else
  python - "$CONFIG_PATH" "$HF_USER" "$DATASET_REPO" "$DATA_SCOPE" "$MODELS" "$JOBS" <<'PY'
import json, sys
dst, hf_user, data_repo, data_scope, models, jobs = sys.argv[1:7]
cfg = {
    "hf_user": hf_user,
    "data_repo": data_repo,
    "data_scope": data_scope,
    "debug": data_scope == "pilot",
    "models": [m.strip() for m in models.split(",") if m.strip()],
    "jobs": [j.strip() for j in jobs.split(",") if j.strip()],
}
json.dump(cfg, open(dst, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(f"Generated config: models={cfg['models']} jobs={cfg['jobs']}")
PY
fi

echo "[3/4] Uploading dataset -> $DATASET_REPO (private)..."
if ! hf repo info "$DATASET_REPO" --repo-type dataset >/dev/null 2>&1; then
  hf repo create "$DATASET_REPO" --repo-type dataset --private
fi
hf upload "$DATASET_REPO" "$DATA_DIR" . --repo-type dataset \
  --commit-message "update $(date -u +%FT%TZ)"

echo "[4/4] Launching compute (COMPUTE=$COMPUTE)..."
if [ "$COMPUTE" = "local" ]; then
  python - "$CONFIG_PATH" "$DATA_DIR" <<'PY'
import json, sys
path, data_dir = sys.argv[1:3]
cfg = json.load(open(path, encoding="utf-8"))
cfg["data_dir"] = data_dir
json.dump(cfg, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
PY
  export HF_RUN_CONFIG="$CONFIG_PATH"
  export HF_USER
  export RESUME
  echo "[$(_ts)] [4/4] Starting local train (RESUME=$RESUME)..."
  python "$HERE/train_job.py"
  echo "Done. Adapters + metrics under https://huggingface.co/$HF_USER"
elif [ "$COMPUTE" = "jobs" ]; then
  JOB_ARGS=(
    hf jobs uv run
    --flavor "$FLAVOR"
    --timeout "$TIMEOUT"
    --secrets HF_TOKEN
    -e "HF_USER=$HF_USER"
    -e "DATA_REPO=$DATASET_REPO"
  )
  if [ "$DETACH" = "1" ]; then
    JOB_ARGS+=(-d)
  fi
  JOB_ARGS+=(-e "RESUME=$RESUME")
  JOB_ARGS+=("$HERE/train_job.py")
  "${JOB_ARGS[@]}"
  echo "Job submitted. Track at: https://huggingface.co/jobs/$HF_USER"
  echo "Adapters + metrics will land under https://huggingface.co/$HF_USER"
else
  echo "Unknown COMPUTE=$COMPUTE (use local|jobs)"; exit 1
fi
