#!/usr/bin/env python3
"""Kaggle GPU kernel: QLoRA fine-tune small models for scene-boundary detection.

Runs on a Kaggle Notebook (T4 16GB) with internet ENABLED. Trains one or more
base models on one or more leave-one-text-out folds using Unsloth 4-bit QLoRA +
TRL ``SFTTrainer``, then pushes each LoRA adapter to the Hugging Face Hub
(Kaggle outputs are ephemeral).

Configuration is read, in priority order, from:
  1. ``kaggle_run_config.json`` in the working dir (bundled next to this script), then
  2. environment variables, then
  3. the defaults below.

Expected config keys (all optional)::

    {
      "models": ["unsloth/Llama-3.2-3B-Instruct",
                  "unsloth/Qwen2.5-3B-Instruct",
                  "unsloth/gemma-2-2b-it"],
      "folds": ["fold_A", "fold_B"],
      "data_dir": "/kaggle/input/scene-seg-sft",   # contains <fold>/train.jsonl
      "hf_user": "your-hf-username",
      "hf_token": "",            # prefer Kaggle Secret HF_TOKEN over inlining
      "max_seq_len": 1024,
      "epochs": 1,
      "lr": 2e-4,
      "lora_r": 16,
      "lora_alpha": 16,
      "batch_size": 2,
      "grad_accum": 4,
      "seed": 1337
    }

Adapters are pushed to ``{hf_user}/scene-seg-{model_short}-{fold}``.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Dict

DEFAULTS: Dict[str, Any] = {
    "models": [
        "unsloth/Llama-3.2-3B-Instruct",
        "unsloth/Qwen2.5-3B-Instruct",
        "unsloth/gemma-2-2b-it",
    ],
    "folds": ["fold_A", "fold_B"],
    "data_dir": "/kaggle/input/scene-seg-sft",
    "hf_user": "",
    "hf_token": "",
    "max_seq_len": 1024,
    "epochs": 1,
    "lr": 2e-4,
    "lora_r": 16,
    "lora_alpha": 16,
    "batch_size": 2,
    "grad_accum": 4,
    "seed": 1337,
}


def load_config() -> Dict[str, Any]:
    cfg = dict(DEFAULTS)
    cfg_path = Path("kaggle_run_config.json")
    if cfg_path.exists():
        cfg.update(json.loads(cfg_path.read_text(encoding="utf-8")))
    # Env overrides (scalars / comma lists).
    if os.environ.get("SCENE_SEG_MODELS"):
        cfg["models"] = [m.strip() for m in os.environ["SCENE_SEG_MODELS"].split(",") if m.strip()]
    if os.environ.get("SCENE_SEG_FOLDS"):
        cfg["folds"] = [f.strip() for f in os.environ["SCENE_SEG_FOLDS"].split(",") if f.strip()]
    for key in ("data_dir", "hf_user", "hf_token"):
        if os.environ.get(key.upper()):
            cfg[key] = os.environ[key.upper()]
    return cfg


def resolve_hf_token(cfg: Dict[str, Any]) -> str:
    if cfg.get("hf_token"):
        return cfg["hf_token"]
    if os.environ.get("HF_TOKEN"):
        return os.environ["HF_TOKEN"]
    try:  # Kaggle Secrets
        from kaggle_secrets import UserSecretsClient  # type: ignore

        return UserSecretsClient().get_secret("HF_TOKEN")
    except Exception:  # noqa: BLE001
        return ""


def model_short_name(model_id: str) -> str:
    base = model_id.split("/")[-1].lower()
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    return base


def train_one(model_id: str, fold: str, cfg: Dict[str, Any], hf_token: str) -> str:
    from datasets import load_dataset
    from trl import SFTConfig, SFTTrainer
    from unsloth import FastLanguageModel
    from unsloth.chat_templates import get_chat_template

    train_path = Path(cfg["data_dir"]) / fold / "train.jsonl"
    if not train_path.exists():
        raise FileNotFoundError(f"Missing training file: {train_path}")

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_id,
        max_seq_length=cfg["max_seq_len"],
        load_in_4bit=True,
        dtype=None,
    )
    model = FastLanguageModel.get_peft_model(
        model,
        r=cfg["lora_r"],
        lora_alpha=cfg["lora_alpha"],
        lora_dropout=0.0,
        bias="none",
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ],
        use_gradient_checkpointing="unsloth",
        random_state=cfg["seed"],
    )

    # Apply each model's own chat template to the messages field.
    template_name = {
        "llama": "llama-3.1",
        "qwen": "qwen-2.5",
        "gemma": "gemma",
    }
    chosen = next((v for k, v in template_name.items() if k in model_id.lower()), "chatml")
    tokenizer = get_chat_template(tokenizer, chat_template=chosen)

    def formatting(example: Dict[str, Any]) -> Dict[str, str]:
        text = tokenizer.apply_chat_template(
            example["messages"], tokenize=False, add_generation_prompt=False
        )
        return {"text": text}

    dataset = load_dataset("json", data_files=str(train_path), split="train")
    dataset = dataset.map(formatting, remove_columns=dataset.column_names)

    out_dir = f"out-{model_short_name(model_id)}-{fold}"
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        args=SFTConfig(
            dataset_text_field="text",
            max_seq_length=cfg["max_seq_len"],
            per_device_train_batch_size=cfg["batch_size"],
            gradient_accumulation_steps=cfg["grad_accum"],
            num_train_epochs=cfg["epochs"],
            learning_rate=cfg["lr"],
            warmup_ratio=0.05,
            logging_steps=10,
            optim="adamw_8bit",
            weight_decay=0.01,
            lr_scheduler_type="cosine",
            seed=cfg["seed"],
            output_dir=out_dir,
            report_to="none",
        ),
    )
    trainer.train()

    repo = f"{cfg['hf_user']}/scene-seg-{model_short_name(model_id)}-{fold}"
    if cfg["hf_user"] and hf_token:
        model.push_to_hub(repo, token=hf_token)
        tokenizer.push_to_hub(repo, token=hf_token)
        print(f"Pushed adapter -> https://huggingface.co/{repo}")
    else:
        model.save_pretrained(out_dir)
        tokenizer.save_pretrained(out_dir)
        print(f"hf_user/token missing; saved adapter locally to {out_dir}")
    return repo


def main() -> None:
    cfg = load_config()
    hf_token = resolve_hf_token(cfg)
    print(f"Config: models={cfg['models']} folds={cfg['folds']} data_dir={cfg['data_dir']}")
    results = []
    for model_id in cfg["models"]:
        for fold in cfg["folds"]:
            print(f"\n=== Training {model_id} on {fold} ===")
            repo = train_one(model_id, fold, cfg, hf_token)
            results.append({"model": model_id, "fold": fold, "repo": repo})
    Path("train_results.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )
    print("\nDone:", json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
