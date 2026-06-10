# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "unsloth",
#     "datasets",
#     "trl==0.22.2",
#     "huggingface_hub[hf_transfer]",
#     "transformers==4.57.3",
# ]
# ///
"""HF Jobs / local GPU: QLoRA fine-tune + optional eval for scene-boundary detection.

Runs on Hugging Face Jobs (``hf jobs uv run``) or locally on a CUDA GPU. For each
(base model, job) pair it:

  1. Trains an Unsloth 4-bit QLoRA adapter with TRL ``SFTTrainer``.
  2. Pushes the adapter to the Hugging Face Hub (Jobs environments are ephemeral).
  3. Optionally evaluates on the job's held-out ``eval.jsonl`` with batched greedy
     generation, scoring relaxed F1 at tolerances 0/1/3 (macro-averaged per text).
  4. Writes ``metrics_<model>_<job>.json`` and uploads it next to the adapter.

Data layout: a Hub dataset (default ``{hf_user}/scene-seg-sft``) or a local directory
with one subdirectory per job (``train.jsonl`` + ``eval.jsonl``), plus an optional
``hf_run_config.json`` at the dataset root.

Configuration priority:
  1. ``hf_run_config.json`` in the working directory
  2. ``HF_RUN_CONFIG`` env var (path to JSON)
  3. environment variables (``SCENE_SEG_MODELS``, ``SCENE_SEG_JOBS``, …)
  4. defaults below

Adapters: ``{hf_user}/scene-seg-{model_short}-{job}``.

Local (free on your GPU)::

    python src/finetune/hf_jobs/train_job.py

HF Jobs (prepaid credits; cheapest: ``--flavor t4-small``)::

    hf jobs uv run --flavor t4-small --timeout 6h --secrets HF_TOKEN \\
      src/finetune/hf_jobs/train_job.py
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

DEFAULTS: Dict[str, Any] = {
    "models": [
        "unsloth/Llama-3.2-3B-Instruct",
    ],
    "jobs": ["fold_A"],
    "folds": [],
    "data_dir": "",
    "data_repo": "",
    "hf_user": "",
    "hf_token": "",
    "family": "L",
    "max_seq_len": 1024,
    "epochs": 1,
    "lr": 2e-4,
    "lora_r": 16,
    "lora_alpha": 16,
    "batch_size": 2,
    "grad_accum": 4,
    "seed": 1337,
    "eval_after_train": True,
    "eval_limit": 0,
    "eval_batch_size": 16,
    "eval_max_new_tokens": 96,
    "tolerances": [0, 1, 3],
    "postprocess": ["none", "min_scene_len_3", "confidence_threshold_plus_min_scene_len_3"],
    "confidence_threshold": 0.85,
    "max_runtime_seconds": 21600,
    # Run metadata (mirrors plan doc / research_log tags).
    "run_phase": "",
    "data_scope": "",
    "debug": False,
}


def load_config() -> Dict[str, Any]:
    cfg = dict(DEFAULTS)
    cfg_path = Path(os.environ.get("HF_RUN_CONFIG", "hf_run_config.json"))
    if cfg_path.exists():
        cfg.update(json.loads(cfg_path.read_text(encoding="utf-8")))
    if os.environ.get("SCENE_SEG_MODELS"):
        cfg["models"] = [m.strip() for m in os.environ["SCENE_SEG_MODELS"].split(",") if m.strip()]
    if os.environ.get("SCENE_SEG_JOBS"):
        cfg["jobs"] = [j.strip() for j in os.environ["SCENE_SEG_JOBS"].split(",") if j.strip()]
    elif os.environ.get("SCENE_SEG_FOLDS"):
        cfg["jobs"] = [f.strip() for f in os.environ["SCENE_SEG_FOLDS"].split(",") if f.strip()]
    for key in ("data_dir", "data_repo", "hf_user", "hf_token"):
        if os.environ.get(key.upper()):
            cfg[key] = os.environ[key.upper()]
    if os.environ.get("DATA_REPO") and not cfg.get("data_repo"):
        cfg["data_repo"] = os.environ["DATA_REPO"]
    if not cfg.get("jobs") and cfg.get("folds"):
        cfg["jobs"] = list(cfg["folds"])
    if not cfg.get("hf_user") and os.environ.get("HF_USER"):
        cfg["hf_user"] = os.environ["HF_USER"]
    return cfg


def resolve_hf_token(cfg: Dict[str, Any]) -> str:
    if cfg.get("hf_token"):
        return cfg["hf_token"]
    return os.environ.get("HF_TOKEN", "")


def resolve_data_dir(cfg: Dict[str, Any], hf_token: str) -> Path:
    if cfg.get("data_dir"):
        path = Path(cfg["data_dir"])
        if path.exists():
            return path
    data_repo = cfg.get("data_repo") or (
        f"{cfg['hf_user']}/scene-seg-sft" if cfg.get("hf_user") else ""
    )
    if not data_repo:
        raise FileNotFoundError(
            "Set data_dir to a local path or data_repo / hf_user for Hub download."
        )
    from huggingface_hub import snapshot_download  # noqa: PLC0415

    root = snapshot_download(
        repo_id=data_repo,
        repo_type="dataset",
        token=hf_token or None,
    )
    print(f"Downloaded dataset {data_repo} -> {root}")
    return Path(root)


def model_short_name(model_id: str) -> str:
    base = model_id.split("/")[-1].lower()
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    return base


def _extract_json_object(text: str) -> Optional[dict]:
    if not text:
        return None
    start = text.find("{")
    if start < 0:
        return None
    depth = 0
    for i in range(start, len(text)):
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                try:
                    obj = json.loads(text[start : i + 1])
                    return obj if isinstance(obj, dict) else None
                except Exception:  # noqa: BLE001
                    start = text.find("{", i + 1)
                    if start < 0:
                        return None
                    return _extract_json_object(text[start:])
    return None


def parse_label_confidence(text: str) -> Tuple[str, Optional[float]]:
    obj = _extract_json_object(text or "")
    label = None
    conf: Optional[float] = None
    if obj is not None:
        raw = str(obj.get("label", "")).strip().upper()
        if raw in {"BORDER", "TRUE", "YES"}:
            label = "BORDER"
        elif raw in {"NOBORDER", "NO_BORDER", "FALSE", "NO"}:
            label = "NOBORDER"
        try:
            conf = float(obj["confidence"]) if obj.get("confidence") is not None else None
        except Exception:  # noqa: BLE001
            conf = None
    if label is None:
        upper = (text or "").upper()
        if re.search(r"\bNOBORDER\b", upper):
            label = "NOBORDER"
        elif re.search(r"\bBORDER\b", upper):
            label = "BORDER"
        else:
            label = "NOBORDER"
    return label, conf


def apply_min_scene_len(labels: Sequence[str], min_gap: int) -> List[str]:
    out = list(labels)
    last = -10**9
    for i, lab in enumerate(out):
        if lab != "BORDER":
            continue
        if i - last < min_gap:
            out[i] = "NOBORDER"
        else:
            last = i
    return out


def apply_confidence_threshold(
    labels: Sequence[str], confidences: Sequence[Optional[float]], thr: float
) -> List[str]:
    out = list(labels)
    for i, lab in enumerate(out):
        if lab == "BORDER" and confidences[i] is not None and confidences[i] < thr:
            out[i] = "NOBORDER"
    return out


def apply_scenario(
    labels: Sequence[str],
    scenario: str,
    confidences: Optional[Sequence[Optional[float]]] = None,
    thr: float = 0.85,
) -> List[str]:
    if scenario in {"none", "baseline"}:
        return list(labels)
    if scenario == "min_scene_len_3":
        return apply_min_scene_len(labels, 3)
    if scenario == "min_scene_len_5":
        return apply_min_scene_len(labels, 5)
    if scenario == "confidence_threshold":
        return apply_confidence_threshold(labels, confidences or [None] * len(labels), thr)
    if scenario == "confidence_threshold_plus_min_scene_len_3":
        step = apply_confidence_threshold(labels, confidences or [None] * len(labels), thr)
        return apply_min_scene_len(step, 3)
    raise ValueError(f"Unsupported scenario: {scenario}")


def score_one_text(
    preds: Sequence[str], golds: Sequence[str], tolerance: int
) -> Dict[str, float]:
    n = len(golds)
    tp = fp = fn = 0
    for idx in range(n):
        if golds[idx] != "BORDER":
            continue
        lo, hi = max(0, idx - tolerance), min(n, idx + tolerance + 1)
        if any(preds[j] == "BORDER" for j in range(lo, hi)):
            tp += 1
        else:
            fn += 1
    for idx in range(n):
        if preds[idx] != "BORDER":
            continue
        lo, hi = max(0, idx - tolerance), min(n, idx + tolerance + 1)
        if not any(golds[j] == "BORDER" for j in range(lo, hi)):
            fp += 1
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {"tp": tp, "fp": fp, "fn": fn, "precision": precision, "recall": recall, "f1": f1}


def evaluate_macro(
    by_source: Dict[str, Dict[int, Tuple[str, str, Optional[float]]]],
    tolerance: int,
    scenario: str,
    thr: float,
) -> Dict[str, Any]:
    per_text: Dict[str, Dict[str, float]] = {}
    agg_tp = agg_fp = agg_fn = 0
    f1s: List[float] = []
    for source, items in by_source.items():
        size = max(items) + 1
        golds = ["NOBORDER"] * size
        preds = ["NOBORDER"] * size
        confs: List[Optional[float]] = [None] * size
        for idx, (pred, gold, conf) in items.items():
            golds[idx] = gold
            preds[idx] = pred
            confs[idx] = conf
        preds = apply_scenario(preds, scenario, confs, thr)
        m = score_one_text(preds, golds, tolerance)
        per_text[source] = {k: round(v, 4) for k, v in m.items()}
        agg_tp += m["tp"]
        agg_fp += m["fp"]
        agg_fn += m["fn"]
        f1s.append(m["f1"])
    micro_p = agg_tp / (agg_tp + agg_fp) if (agg_tp + agg_fp) else 0.0
    micro_r = agg_tp / (agg_tp + agg_fn) if (agg_tp + agg_fn) else 0.0
    micro_f1 = 2 * micro_p * micro_r / (micro_p + micro_r) if (micro_p + micro_r) else 0.0
    return {
        "macro_f1": round(sum(f1s) / len(f1s), 4) if f1s else 0.0,
        "micro_precision": round(micro_p, 4),
        "micro_recall": round(micro_r, 4),
        "micro_f1": round(micro_f1, 4),
        "per_text": per_text,
    }


def _chat_template_for(model_id: str):
    return {
        "llama": "llama-3.1",
        "qwen": "qwen-2.5",
        "gemma": "gemma",
    }


def read_jsonl(path: Path) -> List[dict]:
    rows: List[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def evaluate_adapter(
    model, tokenizer, eval_rows: List[dict], cfg: Dict[str, Any]
) -> Dict[str, Any]:
    import torch  # noqa: PLC0415
    from unsloth import FastLanguageModel  # noqa: PLC0415

    FastLanguageModel.for_inference(model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"

    limit = int(cfg["eval_limit"])
    if limit > 0:
        eval_rows = eval_rows[:limit]
    bs = int(cfg["eval_batch_size"])
    max_new = int(cfg["eval_max_new_tokens"])

    by_source: Dict[str, Dict[int, Tuple[str, str, Optional[float]]]] = {}
    device = next(model.parameters()).device

    for start in range(0, len(eval_rows), bs):
        batch = eval_rows[start : start + bs]
        prompts = [
            tokenizer.apply_chat_template(
                [{"role": "user", "content": r["messages"][0]["content"]}],
                tokenize=False,
                add_generation_prompt=True,
            )
            for r in batch
        ]
        inputs = tokenizer(
            prompts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=cfg["max_seq_len"],
        ).to(device)
        with torch.no_grad():
            gen = model.generate(
                **inputs,
                max_new_tokens=max_new,
                do_sample=False,
                pad_token_id=tokenizer.pad_token_id,
            )
        gen = gen[:, inputs["input_ids"].shape[1] :]
        texts = tokenizer.batch_decode(gen, skip_special_tokens=True)
        for row, text in zip(batch, texts):
            label, conf = parse_label_confidence(text)
            source = str(row.get("source", "doc"))
            idx = int(row.get("index", 0))
            gold = str(row["label"]).upper()
            by_source.setdefault(source, {})[idx] = (label, gold, conf)

    thr = float(cfg["confidence_threshold"])
    metrics: Dict[str, Any] = {"scenarios": {}}
    for scenario in cfg["postprocess"]:
        metrics["scenarios"][scenario] = {
            f"tol_{t}": evaluate_macro(by_source, t, scenario, thr)
            for t in cfg["tolerances"]
        }
    metrics["n_eval_rows"] = sum(len(v) for v in by_source.values())
    metrics["n_texts"] = len(by_source)
    metrics["n_gold_border"] = sum(
        1 for items in by_source.values() for (_, g, _) in items.values() if g == "BORDER"
    )
    return metrics


def train_one(
    model_id: str, job: str, cfg: Dict[str, Any], hf_token: str, data_root: Path
) -> Dict[str, Any]:
    import unsloth  # noqa: F401, PLC0415 — must precede trl/transformers
    from datasets import load_dataset  # noqa: PLC0415
    from trl import SFTConfig, SFTTrainer  # noqa: PLC0415
    from unsloth import FastLanguageModel  # noqa: PLC0415
    from unsloth.chat_templates import get_chat_template  # noqa: PLC0415

    job_dir = data_root / job
    train_path = job_dir / "train.jsonl"
    eval_path = job_dir / "eval.jsonl"
    meta_path = job_dir / "meta.json"
    job_meta: Dict[str, Any] = {}
    if meta_path.exists():
        job_meta = json.loads(meta_path.read_text(encoding="utf-8"))
    if not train_path.exists():
        raise FileNotFoundError(f"Missing training file: {train_path}")

    if job_meta.get("debug_only") or cfg.get("debug"):
        print(
            "WARNING: debug/pilot run — metrics are for pipeline validation only; "
            "do not report as model performance."
        )

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
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
        use_gradient_checkpointing="unsloth",
        random_state=cfg["seed"],
    )

    chosen = next(
        (v for k, v in _chat_template_for(model_id).items() if k in model_id.lower()),
        "chatml",
    )
    tokenizer = get_chat_template(tokenizer, chat_template=chosen)

    def formatting(example: Dict[str, Any]) -> Dict[str, str]:
        text = tokenizer.apply_chat_template(
            example["messages"], tokenize=False, add_generation_prompt=False
        )
        return {"text": text}

    raw = load_dataset("json", data_files=str(train_path), split="train")
    dataset = raw.map(formatting, remove_columns=raw.column_names)

    short = model_short_name(model_id)
    out_dir = f"out-{short}-{job}"
    trainer = SFTTrainer(
        model=model,
        processing_class=tokenizer,
        train_dataset=dataset,
        args=SFTConfig(
            dataset_text_field="text",
            max_length=cfg["max_seq_len"],
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

    repo = f"{cfg['hf_user']}/scene-seg-{short}-{job}"
    if cfg["hf_user"] and hf_token:
        model.push_to_hub(repo, token=hf_token)
        tokenizer.push_to_hub(repo, token=hf_token)
        print(f"Pushed adapter -> https://huggingface.co/{repo}")
    else:
        model.save_pretrained(out_dir)
        tokenizer.save_pretrained(out_dir)
        print(f"hf_user/token missing; saved adapter locally to {out_dir}")

    result: Dict[str, Any] = {"model": model_id, "job": job, "repo": repo}

    if cfg["eval_after_train"] and eval_path.exists():
        print(f"=== Evaluating {short} on {job} (eval split) ===")
        eval_rows = read_jsonl(eval_path)
        metrics = evaluate_adapter(model, tokenizer, eval_rows, cfg)
        metrics.update(
            {
                "model": model_id,
                "job": job,
                "family": cfg["family"],
                "run_phase": cfg.get("run_phase") or job_meta.get("run_phase", ""),
                "data_scope": cfg.get("data_scope") or job_meta.get("data_scope", ""),
                "debug": bool(cfg.get("debug") or job_meta.get("debug_only", False)),
                "dataset_meta": job_meta,
                "base_config": {
                    k: cfg[k]
                    for k in (
                        "epochs",
                        "lr",
                        "lora_r",
                        "lora_alpha",
                        "batch_size",
                        "grad_accum",
                        "max_seq_len",
                        "seed",
                    )
                },
            }
        )
        metrics_path = Path(f"metrics_{short}_{job}.json")
        metrics_path.write_text(
            json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        result["metrics_path"] = str(metrics_path)
        headline = metrics["scenarios"].get("none", {}).get("tol_3", {}).get("macro_f1")
        result["macro_f1_tol3_raw"] = headline
        print(f"metrics: raw macro_f1@3 = {headline} -> {metrics_path}")
        if cfg["hf_user"] and hf_token:
            try:
                from huggingface_hub import upload_file  # noqa: PLC0415

                upload_file(
                    path_or_fileobj=str(metrics_path),
                    path_in_repo=metrics_path.name,
                    repo_id=repo,
                    token=hf_token,
                    repo_type="model",
                )
                print(f"Uploaded {metrics_path.name} -> {repo}")
            except Exception as exc:  # noqa: BLE001
                print(f"WARNING: could not upload metrics to {repo}: {exc}")
    else:
        print(
            f"Skipping eval for {job} (eval_after_train={cfg['eval_after_train']}, "
            f"eval.jsonl exists={eval_path.exists()})"
        )

    return result


def main() -> None:
    import torch  # noqa: PLC0415

    if not torch.cuda.is_available():
        print("ERROR: CUDA required. Use HF Jobs or a machine with a GPU.")
        sys.exit(1)

    cfg = load_config()
    hf_token = resolve_hf_token(cfg)
    if not cfg.get("hf_user"):
        try:
            from huggingface_hub import whoami  # noqa: PLC0415

            cfg["hf_user"] = whoami(token=hf_token or None)["name"]
        except Exception:  # noqa: BLE001
            pass

    data_root = resolve_data_dir(cfg, hf_token)
    jobs = cfg.get("jobs") or []
    print(f"Config: models={cfg['models']} jobs={jobs} data_root={data_root}")

    queue: List[Tuple[str, str]] = [(m, j) for m in cfg["models"] for j in jobs]
    budget = float(cfg["max_runtime_seconds"])
    t0 = time.time()
    results: List[Dict[str, Any]] = []
    remaining: List[Dict[str, str]] = []

    for model_id, job in queue:
        elapsed = time.time() - t0
        if elapsed > budget:
            remaining.append({"model": model_id, "job": job})
            continue
        print(f"\n=== Training {model_id} on {job} (elapsed {elapsed/3600:.2f}h) ===")
        try:
            results.append(train_one(model_id, job, cfg, hf_token, data_root))
        except Exception as exc:  # noqa: BLE001
            print(f"ERROR on ({model_id}, {job}): {exc}")
            results.append({"model": model_id, "job": job, "error": str(exc)})

    Path("train_results.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    if remaining:
        Path("remaining_jobs.json").write_text(
            json.dumps(remaining, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(
            f"\nTime budget ({budget/3600:.1f}h) reached; {len(remaining)} job(s) "
            "deferred -> remaining_jobs.json."
        )
    print("\nDone:", json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
