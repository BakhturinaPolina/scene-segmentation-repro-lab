---
note_type: run
run_id: run_20260405_ssc_baseline_bert
title: "SSC baseline: bert-base-german-cased on stss_test_2 (1 epoch)"
date: 2026-04-05
track: ssc
run_type: baseline
status: success
goal: "Run minimal SSC training and evaluation to verify the pipeline end-to-end"
entrypoint: "python -m ssc.main"
command: >
  python -m ssc.main
  --model_name bert-base-german-cased
  --tokenizer_name bert-base-german-cased
  --context_size 512 --stride full --label_set Coarse
  --train_files data/full/stss_test_2
  --test_files data/full/stss_test_2
  --train_batch_size 1 --eval_batch_size 1
  --num_train_epochs 1
  --output_dir ../../outputs/ssc/2026-04-05/baseline_bert
  --random_seed 42
  --lstm_num_layers 0 --lstm_hidden_size 0
working_directory: "upstream/scene-segmentation"
git_commit: "8649e50"
environment: ".venv-gpu"
os: "Linux 6.17.0-111019-tuxedo"
hardware: "Intel + NVIDIA GeForce RTX 2070 Max-Q (8 GB)"
gpu: "NVIDIA GeForce RTX 2070 with Max-Q Design"
cuda_notes: "CUDA 12.0, torch 2.10.0+cu128, transformers 4.52.4"
api_provider: ""
api_model: ""
api_cost_estimate: ""
dataset_assets:
  - "data/full/stss_test_2 (Aus guter Familie.xmi.zip, Effi Briest.xmi.zip)"
label_schema: "Coarse (BORDER / NOBORDER)"
prompt_version: ""
model_name: "bert-base-german-cased"
varying_factor: "none"
fixed_conditions:
  - "context_size=512, stride=full, frozen embeddings, no LSTM, no MLP"
  - "batch_size=1 (model forward uses squeeze, incompatible with batch>1)"
random_seed: "42"
output_dir: "outputs/ssc/2026-04-05/baseline_bert"
artifacts_expected:
  - "model.safetensors"
  - "results.json"
  - "train.log"
artifacts_produced:
  - "model.safetensors (425 MB)"
  - "stss_test_2/results.json"
  - "train.log"
  - "config.json"
  - "checkpoint-500, checkpoint-541"
main_metric_name: "average_f1"
main_metric_value: "0.0089"
precision: "1.0"
recall: "0.0045"
f1: "0.0089"
iou: ""
runtime: "3401s (~57 min total: 922s train + 506s eval + annotation)"
failure_category: ""
related_experiment: ""
related_issue: "issue_ssc_collator_batch_size, issue_eval_strategy_rename"
decision_relevance: true
notion_targets:
  roadmap: "Phase 3.1"
  runs: true
  experiments: ""
  artifacts: true
  issues: true
  decisions: true
---

## Objective

Validate the SSC training and evaluation pipeline runs end-to-end on the GPU environment with the available test data. This is not expected to produce a strong model; it's a smoke baseline.

## What was held constant

- bert-base-german-cased embeddings (frozen)
- No LSTM layers, no MLP override
- Coarse label set (BORDER / NOBORDER)
- context_size=512, stride=full

## What changed

Several upstream code patches were required:
1. `evaluation_strategy` renamed to `eval_strategy` for transformers 4.52.4
2. `accelerate` upgraded to fix `unwrap_model(keep_torch_compile=...)` TypeError
3. Custom `SSCDataCollator` added to pad variable-length fields (labels, sep_token_indices, sentence_indices)
4. batch_size reduced to 1 because the model's `.squeeze()` forward is incompatible with batch > 1

## Outcome

- **Training**: loss=0.386, completed 541 steps in 922s
- **Eval during training**: accuracy=0.959, F1=0.0, precision=0.0, recall=0.0 (model predicts all NOBORDER)
- **Pipeline evaluation (tolerance=3)**: avg F1=0.0089, precision=1.0, recall=0.0045
  - Aus guter Familie: F1=0.0091
  - Effi Briest: F1=0.0088

## Interpretation

The extremely low F1 is expected: 1 epoch with frozen embeddings on heavily imbalanced data (96% NOBORDER). The model barely learns to predict borders. The important outcome is that the full pipeline (train → eval → annotate → score) runs without errors.

## Next step

Run with more epochs, unfrozen embeddings, or proper train/test splits to get meaningful results. Consider the batch_size=1 limitation for future work.
