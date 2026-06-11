#!/usr/bin/env bash
# Build SFT data, upload to a private HF dataset, and submit a GPU Job (or run locally if overridden).
#
# One submission == one experiment. The job trains every (model x job) pair, runs
# in-job eval on each held-out split, and uploads adapters + metrics to the Hub.
#
# Data scope (see docs/planning/FINETUNING_EXPERIMENTS_PLAN.md):
#   DATA_SCOPE=stss_test_2 — current stage: 2 novels only, LOO folds (debug; default)
#   DATA_SCOPE=pilot       — alias for stss_test_2
#   DATA_SCOPE=corpus      — paper-comparable train_full → stss_test_2 (requires full corpus)
#
# Prerequisites (one-time):
#   1. HF Pro account ($9/mo) — unlocks Jobs API and private dataset storage.
#   2. ``pip install huggingface_hub`` and ``hf auth login`` with a write token.
#   3. Add ~$35–45 prepaid credits at https://huggingface.co/settings/billing
#
# Default compute: HF Jobs (`COMPUTE=jobs`, `t4-small` ≈ $0.40/hr). Override with COMPUTE=local.
#
# Usage examples:
#   # STSS-Test-2 stage (2 novels, both folds):
#   HF_USER=RuthonField DATA_SCOPE=stss_test_2 RUN_CONFIG=src/finetune/hf_jobs/configs/stss_test_2/E0_full.json \
#     FLAVOR=t4-small TIMEOUT=8h bash src/finetune/hf_jobs/submit_job.sh
#
#   # STSS-Test-2 smoke (fold_A, eval_limit 200):
#   HF_USER=RuthonField DATA_SCOPE=stss_test_2 RUN_CONFIG=src/finetune/hf_jobs/configs/stss_test_2/E0_smoke.json \
#     FLAVOR=t4-small TIMEOUT=2h BUILD_MODE=skip bash src/finetune/hf_jobs/submit_job.sh
#
#   # Paper-comparable E1 (once full corpus is on disk):
#   HF_USER=RuthonField DATA_SCOPE=corpus RUN_CONFIG=src/finetune/hf_jobs/configs/E1_anchor.json \
#     FLAVOR=t4-small TIMEOUT=8h bash src/finetune/hf_jobs/submit_job.sh
#
#   # E10 validation (val split required at build):
#   HF_USER=RuthonField DATA_SCOPE=corpus \
#     BUILD_ARGS="--val_fraction 0.1" \
#     RUN_CONFIG=src/finetune/hf_jobs/configs/E10_validation.json \
#     FLAVOR=t4-small TIMEOUT=8h bash src/finetune/hf_jobs/submit_job.sh
#
#   # E3 target format (data-side factor — pass BUILD_ARGS):
#   HF_USER=RuthonField DATA_SCOPE=corpus \
#     BUILD_ARGS="--target_format json" \
#     RUN_CONFIG=src/finetune/hf_jobs/configs/E3_json.json \
#     FLAVOR=t4-small TIMEOUT=8h bash src/finetune/hf_jobs/submit_job.sh
#
#   # E8 stretch (8B, test_full eval):
#   HF_USER=RuthonField DATA_SCOPE=corpus \
#     BUILD_ARGS="--eval_split test_full" JOBS=train_full__to__test_full \
#     RUN_CONFIG=src/finetune/hf_jobs/configs/E8_8b_test_full.json \
#     COMPUTE=jobs FLAVOR=t4-medium TIMEOUT=12h bash src/finetune/hf_jobs/submit_job.sh
set -euo pipefail

RESUME="${RESUME:-1}"
VERBOSE="${VERBOSE:-0}"
if [ "$VERBOSE" = "1" ]; then set -x; fi

_ts() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"
PY="${PY:-$ROOT/.venv/bin/python}"
if [ ! -x "$PY" ]; then PY="${PY_FALLBACK:-python3}"; fi

if [ -z "${HF_USER:-}" ]; then
  HF_USER="$(hf auth whoami 2>/dev/null | head -1 || true)"
fi
: "${HF_USER:?Set HF_USER or run hf auth login}"

DATASET_REPO="${DATASET_REPO:-${HF_USER}/scene-seg-sft}"
DATA_SCOPE="${DATA_SCOPE:-stss_test_2}"   # stss_test_2 | pilot | corpus
BUILD_MODE="${BUILD_MODE:-}"               # auto from DATA_SCOPE if empty
BUILD_ARGS="${BUILD_ARGS:-}"
DATA_DIR="$ROOT/data/processed/finetune"
COMPUTE="${COMPUTE:-jobs}"                # jobs | local
FLAVOR="${FLAVOR:-t4-small}"
TIMEOUT="${TIMEOUT:-6h}"
DETACH="${DETACH:-1}"

case "$DATA_SCOPE" in
  stss_test_2|pilot)
    BUILD_MODE="${BUILD_MODE:-folds}"
    JOBS="${JOBS:-fold_A,fold_B}"
    BUILD_ARGS="${BUILD_ARGS:---fold both --stss_only --target_format cot_list --negative_mode paper10pct --context_mode tokens512}"
    STSS_DIR="${STSS_DIR:-$ROOT/upstream/scene-segmentation/data/full/stss_test_2}"
    N_STSS="$(find "$STSS_DIR" -name '*.xmi.zip' 2>/dev/null | wc -l | tr -d ' ')"
    if [ "${N_STSS:-0}" -lt 2 ]; then
      echo "[scope] ERROR: DATA_SCOPE=$DATA_SCOPE requires 2 XMI zips in $STSS_DIR (found ${N_STSS:-0})."
      echo "        Expected: Aus guter Familie.xmi.zip, Effi Briest.xmi.zip"
      exit 1
    fi
    echo "[scope] DATA_SCOPE=$DATA_SCOPE — STSS-Test-2 only (${N_STSS} zips); LOO folds; tag runs debug."
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
    echo "Unknown DATA_SCOPE=$DATA_SCOPE (use stss_test_2|pilot|corpus)"; exit 1
    ;;
esac

MODELS="${MODELS:-unsloth/Llama-3.2-3B-Instruct}"

echo "[1/4] Building SFT dataset (scope=$DATA_SCOPE mode=$BUILD_MODE)..."
case "$BUILD_MODE" in
  folds)
    "$PY" "$ROOT/src/finetune/build_sft_dataset.py" --mode folds --fold both $BUILD_ARGS
    ;;
  corpus)
    "$PY" "$ROOT/src/finetune/build_sft_dataset.py" --mode corpus $BUILD_ARGS
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
  "$PY" - "$RUN_CONFIG" "$CONFIG_PATH" "$HF_USER" "$DATASET_REPO" "$DATA_SCOPE" "$DATA_DIR" <<'PY'
import json, re, sys
from pathlib import Path

src, dst, hf_user, data_repo, data_scope, data_dir = sys.argv[1:7]
cfg = json.load(open(src, encoding="utf-8"))
cfg.setdefault("hf_user", hf_user)
cfg.setdefault("data_repo", data_repo)
cfg.setdefault("data_scope", data_scope)
if data_scope in ("stss_test_2", "pilot") and "debug" not in cfg:
    cfg["debug"] = True
if data_scope == "pilot":
    cfg.setdefault("data_scope", "stss_test_2")

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
  "$PY" - "$CONFIG_PATH" "$HF_USER" "$DATASET_REPO" "$DATA_SCOPE" "$MODELS" "$JOBS" <<'PY'
import json, sys
dst, hf_user, data_repo, data_scope, models, jobs = sys.argv[1:7]
cfg = {
    "hf_user": hf_user,
    "data_repo": data_repo,
    "data_scope": data_scope,
    "debug": data_scope in ("stss_test_2", "pilot"),
    "data_scope": "stss_test_2" if data_scope in ("stss_test_2", "pilot") else data_scope,
    "models": [m.strip() for m in models.split(",") if m.strip()],
    "jobs": [j.strip() for j in jobs.split(",") if j.strip()],
}
json.dump(cfg, open(dst, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(f"Generated config: models={cfg['models']} jobs={cfg['jobs']}")
PY
fi

echo "[3/4] Staging HF Jobs helper bundle + uploading dataset -> $DATASET_REPO (private)..."
BUNDLE_DIR="$DATA_DIR/_hf_job_bundle"
mkdir -p "$BUNDLE_DIR/finetune" "$BUNDLE_DIR/postprocess"
cp "$ROOT/src/finetune/__init__.py" "$BUNDLE_DIR/finetune/"
cp "$ROOT/src/finetune/run_log.py" "$BUNDLE_DIR/finetune/"
cp "$ROOT/src/postprocess/__init__.py" "$BUNDLE_DIR/postprocess/"
cp "$ROOT/src/postprocess/postprocess.py" "$BUNDLE_DIR/postprocess/"
hf repo create "$DATASET_REPO" --repo-type dataset --private --exist-ok
hf upload "$DATASET_REPO" "$DATA_DIR" . --repo-type dataset \
  --commit-message "update $(date -u +%FT%TZ)"

echo "[4/4] Launching compute (COMPUTE=$COMPUTE)..."
if [ "$COMPUTE" = "local" ]; then
  "$PY" - "$CONFIG_PATH" "$DATA_DIR" <<'PY'
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
  "$PY" "$HERE/train_job.py"
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
