#!/usr/bin/env bash
# Push the QLoRA training kernel to Kaggle and run it on a free T4 GPU.
#
# Prerequisites (one-time):
#   1. pip install kaggle  (and put your API token at ~/.kaggle/kaggle.json)
#   2. Set KAGGLE_USERNAME to your Kaggle username.
#   3. Add an HF write token as a Kaggle Notebook secret named HF_TOKEN
#      (Add-ons -> Secrets) so adapters can be pushed to the HF Hub.
#
# Steps performed:
#   a. Build the SFT dataset locally (if not already present).
#   b. Upload data/processed/finetune as a Kaggle dataset "scene-seg-sft".
#   c. Substitute KAGGLE_USERNAME into kernel-metadata.json.
#   d. Push the kernel (kaggle kernels push), which queues a GPU run.
#
# Usage:
#   KAGGLE_USERNAME=yourname HF_USER=yourhfname bash src/finetune/kaggle/push_kernel.sh
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"
: "${KAGGLE_USERNAME:?Set KAGGLE_USERNAME to your Kaggle username}"
HF_USER="${HF_USER:-$KAGGLE_USERNAME}"

DATA_DIR="$ROOT/data/processed/finetune"
KERNEL_DIR="$HERE"

echo "[1/4] Ensuring SFT dataset exists..."
if [ ! -f "$DATA_DIR/fold_A/train.jsonl" ]; then
  python "$ROOT/src/finetune/build_sft_dataset.py" --fold both
fi

echo "[2/4] Preparing Kaggle dataset metadata..."
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

echo "[3/4] Writing kaggle_run_config.json + kernel-metadata.json (user=${KAGGLE_USERNAME})..."
cat > "$KERNEL_DIR/kaggle_run_config.json" <<JSON
{
  "hf_user": "${HF_USER}",
  "data_dir": "/kaggle/input/scene-seg-sft",
  "models": ["unsloth/Llama-3.2-3B-Instruct", "unsloth/Qwen2.5-3B-Instruct", "unsloth/gemma-2-2b-it"],
  "folds": ["fold_A", "fold_B"]
}
JSON
sed "s/KAGGLE_USERNAME/${KAGGLE_USERNAME}/g" "$KERNEL_DIR/kernel-metadata.json" > "$KERNEL_DIR/kernel-metadata.local.json"
mv "$KERNEL_DIR/kernel-metadata.local.json" "$KERNEL_DIR/kernel-metadata.json"

echo "[4/4] Pushing kernel..."
kaggle kernels push -p "$KERNEL_DIR"
echo "Done. Track the run at: https://www.kaggle.com/${KAGGLE_USERNAME}/scene-seg-qlora-train"
