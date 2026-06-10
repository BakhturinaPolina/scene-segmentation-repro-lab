#!/usr/bin/env bash
# Push the QLoRA train+eval kernel to Kaggle and run it on a free T4 GPU.
#
# One push == one experiment. The kernel trains every (model x job) pair, runs
# in-kernel eval on each job's held-out split, and uploads metrics to the HF Hub.
#
# Prerequisites (one-time):
#   1. pip install kaggle  (and put your API token at ~/.kaggle/kaggle.json)
#   2. Set KAGGLE_USERNAME to your Kaggle username.
#   3. Add an HF write token as a Kaggle Notebook secret named HF_TOKEN
#      (Add-ons -> Secrets) so adapters + metrics can be pushed to the HF Hub.
#
# Build is non-destructive: committed kernel-metadata.json stays a template; a
# temporary build dir with substituted values is what gets pushed.
#
# Usage examples:
#   # Folds mode (uses locally available STSS-Test-2 + Excel):
#   KAGGLE_USERNAME=me HF_USER=mehf BUILD_MODE=folds bash src/finetune/kaggle/push_kernel.sh
#
#   # Corpus mode (paper-comparable; needs the full corpus on disk):
#   KAGGLE_USERNAME=me HF_USER=mehf BUILD_MODE=corpus \
#     JOBS=train_full__to__stss_test_2 \
#     MODELS=unsloth/Llama-3.2-3B-Instruct \
#     BUILD_ARGS="--train_split train_full --eval_split stss_test_2 --target_format cot_list --negative_mode paper10pct" \
#     bash src/finetune/kaggle/push_kernel.sh
#
#   # Provide a ready-made per-experiment config (overrides MODELS/JOBS plumbing):
#   KAGGLE_USERNAME=me RUN_CONFIG=experiments/E1.json bash src/finetune/kaggle/push_kernel.sh
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"
: "${KAGGLE_USERNAME:?Set KAGGLE_USERNAME to your Kaggle username}"
HF_USER="${HF_USER:-$KAGGLE_USERNAME}"

BUILD_MODE="${BUILD_MODE:-folds}"          # folds | corpus | skip
BUILD_ARGS="${BUILD_ARGS:-}"               # extra flags for build_sft_dataset.py
DATA_DIR="$ROOT/data/processed/finetune"

# Default job + model lists depend on build mode.
if [ "$BUILD_MODE" = "corpus" ]; then
  JOBS="${JOBS:-train_full__to__stss_test_2}"
else
  JOBS="${JOBS:-fold_A,fold_B}"
fi
MODELS="${MODELS:-unsloth/Llama-3.2-3B-Instruct,unsloth/Qwen2.5-3B-Instruct,unsloth/gemma-2-2b-it}"

echo "[1/5] Building SFT dataset (mode=$BUILD_MODE)..."
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

echo "[2/5] Uploading $DATA_DIR as Kaggle dataset 'scene-seg-sft'..."
cat > "$DATA_DIR/dataset-metadata.json" <<JSON
{
  "title": "scene-seg-sft",
  "id": "${KAGGLE_USERNAME}/scene-seg-sft",
  "licenses": [{"name": "CC0-1.0"}]
}
JSON
if kaggle datasets status "${KAGGLE_USERNAME}/scene-seg-sft" >/dev/null 2>&1; then
  kaggle datasets version -p "$DATA_DIR" -m "update $(date -u +%FT%TZ)" --dir-mode zip
else
  kaggle datasets create -p "$DATA_DIR" --dir-mode zip
fi

echo "[3/5] Preparing temporary kernel build dir..."
BUILD_DIR="$(mktemp -d)"
trap 'rm -rf "$BUILD_DIR"' EXIT
cp "$HERE/train_kernel.py" "$BUILD_DIR/train_kernel.py"

echo "[4/5] Writing kaggle_run_config.json + kernel-metadata.json..."
if [ -n "${RUN_CONFIG:-}" ]; then
  # Use the provided config, but ensure hf_user + data_dir are set.
  python - "$RUN_CONFIG" "$BUILD_DIR/kaggle_run_config.json" "$HF_USER" <<'PY'
import json, sys
src, dst, hf_user = sys.argv[1], sys.argv[2], sys.argv[3]
cfg = json.load(open(src, encoding="utf-8"))
cfg.setdefault("hf_user", hf_user)
cfg.setdefault("data_dir", "/kaggle/input/scene-seg-sft")
json.dump(cfg, open(dst, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(f"Using RUN_CONFIG {src}: models={cfg.get('models')} jobs={cfg.get('jobs')}")
PY
else
  python - "$BUILD_DIR/kaggle_run_config.json" "$HF_USER" "$MODELS" "$JOBS" <<'PY'
import json, sys
dst, hf_user, models, jobs = sys.argv[1:5]
cfg = {
    "hf_user": hf_user,
    "data_dir": "/kaggle/input/scene-seg-sft",
    "models": [m.strip() for m in models.split(",") if m.strip()],
    "jobs": [j.strip() for j in jobs.split(",") if j.strip()],
}
json.dump(cfg, open(dst, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(f"Generated config: models={cfg['models']} jobs={cfg['jobs']}")
PY
fi

sed "s/KAGGLE_USERNAME/${KAGGLE_USERNAME}/g" "$HERE/kernel-metadata.json" > "$BUILD_DIR/kernel-metadata.json"

echo "[5/5] Pushing kernel..."
kaggle kernels push -p "$BUILD_DIR"
echo "Done. Track the run at: https://www.kaggle.com/${KAGGLE_USERNAME}/scene-seg-qlora-train"
echo "Adapters + metrics_<model>_<job>.json will appear under https://huggingface.co/${HF_USER}"
