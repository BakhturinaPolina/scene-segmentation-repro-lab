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
import shutil
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

_HF_JOB_BUNDLE_PREFIX = "_hf_job_bundle"
_HF_JOB_SRC_CACHE = Path("/tmp/scene_seg_src")


def _has_project_modules(root: Path) -> bool:
    return (
        (root / "finetune" / "run_log.py").is_file()
        and (root / "postprocess" / "postprocess.py").is_file()
    )


def _resolve_src_root() -> Path:
    """Locate ``src/`` for local runs; on HF Jobs fetch bundled modules from DATA_REPO."""
    env_root = os.environ.get("SCENE_SEG_SRC_ROOT")
    if env_root:
        root = Path(env_root).resolve()
        if _has_project_modules(root):
            return root
        raise FileNotFoundError(f"SCENE_SEG_SRC_ROOT={root} missing finetune/postprocess modules")

    here = Path(__file__).resolve()
    for base in (here.parent, *here.parents):
        for candidate in (base, base / "src"):
            if _has_project_modules(candidate):
                return candidate

    return _materialize_hf_job_bundle()


def _materialize_hf_job_bundle() -> Path:
    """HF Jobs copies this script to ``/tmp/script.py``; pull helper modules from the dataset."""
    if _has_project_modules(_HF_JOB_SRC_CACHE):
        return _HF_JOB_SRC_CACHE

    data_repo = os.environ.get("DATA_REPO")
    if not data_repo:
        raise ImportError(
            "Cannot import finetune/postprocess: set SCENE_SEG_SRC_ROOT locally or "
            "DATA_REPO on HF Jobs (dataset must include _hf_job_bundle/)."
        )

    from huggingface_hub import snapshot_download  # noqa: PLC0415

    cache = Path(
        snapshot_download(
            repo_id=data_repo,
            repo_type="dataset",
            allow_patterns=[f"{_HF_JOB_BUNDLE_PREFIX}/**"],
            token=os.environ.get("HF_TOKEN") or None,
        )
    )
    bundle = cache / _HF_JOB_BUNDLE_PREFIX
    if not bundle.is_dir():
        raise FileNotFoundError(
            f"{data_repo} is missing {_HF_JOB_BUNDLE_PREFIX}/; rerun submit_job.sh upload step."
        )

    if _HF_JOB_SRC_CACHE.exists():
        shutil.rmtree(_HF_JOB_SRC_CACHE)
    shutil.copytree(bundle, _HF_JOB_SRC_CACHE)
    return _HF_JOB_SRC_CACHE


_SRC_ROOT = _resolve_src_root()
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from finetune.run_log import RunState, log, progress, upload_if_hub  # noqa: E402
from postprocess.postprocess import apply_scenario  # noqa: E402

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
    "postprocess": [
        "none",
        "cluster_merge",
        "min_scene_len_3",
        "cluster_merge_plus_min_scene_len_3",
        "confidence_threshold_plus_min_scene_len_3",
    ],
    "confidence_threshold": 0.85,
    "cluster_merge_radius": 3,
    "max_runtime_seconds": 21600,
    "completion_only_loss": True,
    "eval_during_training": False,
    "eval_steps": 50,
    "save_steps": 50,
    "save_total_limit": 2,
    "load_best_model_at_end": True,
    "metric_for_best_model": "eval_macro_f1_tol3",
    "early_stopping_patience": 0,
    "val_eval_limit": 500,
    "resume": True,
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
    log(f"Downloaded dataset {data_repo} -> {root}")
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
    cluster_merge_radius: int = 3,
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
        preds = apply_scenario(
            preds,
            scenario,
            confidences=confs,
            confidence_threshold=thr,
            cluster_merge_radius=cluster_merge_radius,
        )
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


def _response_template_parts(model_id: str, chat_template: str) -> Tuple[str, str]:
    """Instruction/response delimiter strings for train_on_responses_only."""
    if "llama" in model_id.lower() or chat_template == "llama-3.1":
        return (
            "<|start_header_id|>user<|end_header_id|>",
            "<|start_header_id|>assistant<|end_header_id|>",
        )
    return ("<|im_start|>user\n", "<|im_start|>assistant\n")


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

    was_training = model.training
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
    radius = int(cfg.get("cluster_merge_radius", 3))

    batch_starts = range(0, len(eval_rows), bs)
    for start in progress(batch_starts, desc="eval inference"):
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
            f"tol_{t}": evaluate_macro(by_source, t, scenario, thr, radius)
            for t in cfg["tolerances"]
        }
    metrics["n_eval_rows"] = sum(len(v) for v in by_source.values())
    metrics["n_texts"] = len(by_source)
    metrics["n_gold_border"] = sum(
        1 for items in by_source.values() for (_, g, _) in items.values() if g == "BORDER"
    )
    if was_training:
        model.train()
    return metrics


class FinetuneF1Callback:
    """Periodic val-set macro F1@3 during training (E10)."""

    def __init__(
        self,
        val_rows: List[dict],
        cfg: Dict[str, Any],
        tokenizer,
    ) -> None:
        from transformers import TrainerCallback  # noqa: PLC0415

        class _Inner(TrainerCallback):
            def __init__(self, outer: "FinetuneF1Callback") -> None:
                self.outer = outer

            def on_train_begin(self, args, state, control, **kwargs):  # noqa: ANN001
                self.outer.trainer = kwargs.get("trainer")

            def on_step_end(self, args, state, control, **kwargs):  # noqa: ANN001
                self.outer._on_step_end(args, state, control, **kwargs)

        self.val_rows = val_rows
        self.cfg = cfg
        self.tokenizer = tokenizer
        self.trainer = None
        self.best_f1 = -1.0
        self.best_step = 0
        self._patience_left = int(cfg.get("early_stopping_patience", 0))
        self._callback = _Inner(self)

    def _on_step_end(self, args, state, control, **kwargs):  # noqa: ANN001
        if not self.cfg.get("eval_during_training") or not self.val_rows:
            return
        step = state.global_step
        if step <= 0 or step % int(self.cfg["eval_steps"]) != 0:
            return
        model = kwargs.get("model")
        if model is None:
            return
        log(f"[val] step={step} running quick F1@3 eval (limit={self.cfg['val_eval_limit']})")
        quick_cfg = dict(self.cfg)
        quick_cfg["eval_limit"] = int(self.cfg.get("val_eval_limit", 500))
        metrics = evaluate_adapter(model, self.tokenizer, self.val_rows, quick_cfg)
        f1 = metrics["scenarios"].get("none", {}).get("tol_3", {}).get("macro_f1", 0.0)
        if self.trainer is not None:
            self.trainer.log({"eval_macro_f1_tol3": f1, "eval_step": step})
        log(f"[val] step={step} macro_f1@3={f1} (best={self.best_f1:.4f} @ step {self.best_step})")
        if f1 > self.best_f1:
            self.best_f1 = f1
            self.best_step = step
            self._patience_left = int(self.cfg.get("early_stopping_patience", 0))
            if self.trainer is not None and self.cfg.get("load_best_model_at_end"):
                self.trainer.save_model(os.path.join(args.output_dir, "best_adapter"))
        elif self.cfg.get("early_stopping_patience", 0) > 0:
            self._patience_left -= 1
            if self._patience_left <= 0:
                log("[val] early stopping triggered", level="warning")
                control.should_training_stop = True


def _sft_config_kwargs(
    cfg: Dict[str, Any], *, out_dir: str, eval_during: bool
) -> Dict[str, Any]:
    """Build SFTConfig kwargs compatible with TRL 0.9 (max_seq_length) and 0.10+ (max_length)."""
    import inspect  # noqa: PLC0415

    from trl import SFTConfig  # noqa: PLC0415

    max_len = cfg["max_seq_len"]
    params = inspect.signature(SFTConfig.__init__).parameters
    max_key = "max_length" if "max_length" in params else "max_seq_length"

    kwargs: Dict[str, Any] = {
        "dataset_text_field": "text",
        max_key: max_len,
        "per_device_train_batch_size": cfg["batch_size"],
        "gradient_accumulation_steps": cfg["grad_accum"],
        "num_train_epochs": cfg["epochs"],
        "learning_rate": cfg["lr"],
        "warmup_ratio": 0.05,
        "logging_steps": 10,
        "optim": "adamw_8bit",
        "weight_decay": 0.01,
        "lr_scheduler_type": "cosine",
        "seed": cfg["seed"],
        "output_dir": out_dir,
        "report_to": "none",
        "save_strategy": "steps" if eval_during else "no",
        "save_steps": int(cfg.get("save_steps", 50)) if eval_during else None,
        "save_total_limit": int(cfg.get("save_total_limit", 2)) if eval_during else None,
        "load_best_model_at_end": False,
    }
    return kwargs


def train_one(
    model_id: str, job: str, cfg: Dict[str, Any], hf_token: str, data_root: Path
) -> Dict[str, Any]:
    import unsloth  # noqa: F401, PLC0415 — must precede trl/transformers
    import torch  # noqa: PLC0415
    from datasets import load_dataset  # noqa: PLC0415
    from transformers.trainer_utils import get_last_checkpoint  # noqa: PLC0415
    from trl import SFTConfig, SFTTrainer  # noqa: PLC0415
    from unsloth import FastLanguageModel  # noqa: PLC0415
    from unsloth.chat_templates import get_chat_template, train_on_responses_only  # noqa: PLC0415

    job_dir = data_root / job
    train_path = job_dir / "train.jsonl"
    eval_path = job_dir / "eval.jsonl"
    val_path = job_dir / "val.jsonl"
    meta_path = job_dir / "meta.json"
    job_meta: Dict[str, Any] = {}
    if meta_path.exists():
        job_meta = json.loads(meta_path.read_text(encoding="utf-8"))
    if not train_path.exists():
        raise FileNotFoundError(f"Missing training file: {train_path}")

    if job_meta.get("max_seq_len_recommended") and not os.environ.get("HF_RUN_CONFIG_FORCE_MAX_LEN"):
        cfg = dict(cfg)
        cfg["max_seq_len"] = job_meta["max_seq_len_recommended"]
        log(f"[1/5] max_seq_len from meta.json -> {cfg['max_seq_len']}")

    if job_meta.get("debug_only") or cfg.get("debug"):
        log(
            "WARNING: debug/pilot run — metrics are for pipeline validation only; "
            "do not report as model performance.",
            level="warning",
        )

    log(f"[1/5] Loading model {model_id} max_seq_len={cfg['max_seq_len']}")
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

    log(f"[2/5] Loading train data from {train_path}")
    raw = load_dataset("json", data_files=str(train_path), split="train")
    dataset = raw.map(formatting, remove_columns=raw.column_names)

    val_rows: List[dict] = []
    if val_path.exists():
        val_rows = read_jsonl(val_path)
        log(f"[2/5] val.jsonl rows={len(val_rows)}")
    elif cfg.get("eval_during_training"):
        log("[2/5] eval_during_training set but no val.jsonl; disabling", level="warning")
        cfg = dict(cfg)
        cfg["eval_during_training"] = False

    short = model_short_name(model_id)
    out_dir = f"out-{short}-{job}"
    eval_during = bool(cfg.get("eval_during_training") and val_rows)
    sft_args = SFTConfig(
        **_sft_config_kwargs(cfg, out_dir=out_dir, eval_during=eval_during)
    )

    callbacks = []
    f1_cb: Optional[FinetuneF1Callback] = None
    if eval_during:
        f1_cb = FinetuneF1Callback(val_rows, cfg, tokenizer)
        callbacks.append(f1_cb._callback)

    log(f"[3/5] Building SFTTrainer (completion_only={cfg.get('completion_only_loss', True)})")
    trainer = SFTTrainer(
        model=model,
        processing_class=tokenizer,
        train_dataset=dataset,
        args=sft_args,
        callbacks=callbacks,
    )

    if cfg.get("completion_only_loss", True):
        instr, resp = _response_template_parts(model_id, chosen)
        trainer = train_on_responses_only(
            trainer,
            instruction_part=instr,
            response_part=resp,
        )
        log(f"[3/5] completion-only loss enabled (instr/resp markers set)")

    resume_ckpt = None
    if cfg.get("resume", True):
        resume_ckpt = get_last_checkpoint(out_dir)
        if resume_ckpt:
            log(f"[4/5] Resuming from checkpoint {resume_ckpt}")

    gpu_stats = torch.cuda.get_device_properties(0)
    log(f"[4/5] Training on {gpu_stats.name} ({gpu_stats.total_memory / 1e9:.1f} GB)")
    trainer.train(resume_from_checkpoint=resume_ckpt)

    if f1_cb and f1_cb.best_f1 >= 0 and cfg.get("load_best_model_at_end"):
        best_dir = os.path.join(out_dir, "best_adapter")
        if os.path.isdir(best_dir):
            log(f"[4/5] Loading best adapter from step {f1_cb.best_step} (F1@3={f1_cb.best_f1:.4f})")
            model.load_adapter(best_dir)

    if trainer.state.log_history:
        log_path = Path(f"training_log_{short}_{job}.json")
        log_path.write_text(json.dumps(trainer.state.log_history, indent=2), encoding="utf-8")

    repo = f"{cfg['hf_user']}/scene-seg-{short}-{job}"
    log(f"[5/5] Saving adapter -> {repo or out_dir}")
    if cfg["hf_user"] and hf_token:
        model.push_to_hub(repo, token=hf_token)
        tokenizer.push_to_hub(repo, token=hf_token)
        log(f"Pushed adapter -> https://huggingface.co/{repo}")
    else:
        model.save_pretrained(out_dir)
        tokenizer.save_pretrained(out_dir)
        log(f"hf_user/token missing; saved adapter locally to {out_dir}")

    result: Dict[str, Any] = {"model": model_id, "job": job, "repo": repo}

    if cfg["eval_after_train"] and eval_path.exists():
        log(f"=== Evaluating {short} on {job} (eval split) ===")
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
                "completion_only_loss": bool(cfg.get("completion_only_loss", True)),
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
                        "completion_only_loss",
                        "eval_during_training",
                    )
                    if k in cfg
                },
            }
        )
        if f1_cb:
            metrics["val_selection"] = {
                "best_macro_f1_tol3": f1_cb.best_f1,
                "best_step": f1_cb.best_step,
            }
        metrics_path = Path(f"metrics_{short}_{job}.json")
        metrics_path.write_text(
            json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        result["metrics_path"] = str(metrics_path)
        headline = metrics["scenarios"].get("none", {}).get("tol_3", {}).get("macro_f1")
        result["macro_f1_tol3_raw"] = headline
        log(f"metrics: raw macro_f1@3 = {headline} -> {metrics_path}")
        upload_if_hub(metrics_path, repo, hf_token)
    else:
        log(
            f"Skipping eval for {job} (eval_after_train={cfg['eval_after_train']}, "
            f"eval.jsonl exists={eval_path.exists()})"
        )

    return result


def main() -> None:
    import torch  # noqa: PLC0415

    if not torch.cuda.is_available():
        log("ERROR: CUDA required. Use HF Jobs or a machine with a GPU.", level="error")
        sys.exit(1)

    cfg = load_config()
    if os.environ.get("RESUME", "1") == "0":
        cfg["resume"] = False
    hf_token = resolve_hf_token(cfg)
    if not cfg.get("hf_user"):
        try:
            from huggingface_hub import whoami  # noqa: PLC0415

            cfg["hf_user"] = whoami(token=hf_token or None)["name"]
        except Exception:  # noqa: BLE001
            pass

    data_root = resolve_data_dir(cfg, hf_token)
    jobs = cfg.get("jobs") or []
    log(f"Config: models={cfg['models']} jobs={jobs} data_root={data_root}")

    state = RunState(Path("run_state.json"))
    queue: List[Tuple[str, str]] = [(m, j) for m in cfg["models"] for j in jobs]
    budget = float(cfg["max_runtime_seconds"])
    t0 = time.time()
    results: List[Dict[str, Any]] = []
    remaining: List[Dict[str, str]] = []

    for model_id, job in queue:
        if cfg.get("resume", True) and state.is_done(model_id, job):
            log(f"Skipping completed ({model_id}, {job}) — resume=on")
            continue
        elapsed = time.time() - t0
        if elapsed > budget:
            remaining.append({"model": model_id, "job": job})
            continue
        log(f"\n=== Training {model_id} on {job} (elapsed {elapsed/3600:.2f}h) ===")
        try:
            result = train_one(model_id, job, cfg, hf_token, data_root)
            results.append(result)
            state.record(model_id, job, status="ok", result=result)
        except Exception as exc:  # noqa: BLE001
            log(f"ERROR on ({model_id}, {job}): {exc}", level="error")
            err_result = {"model": model_id, "job": job, "error": str(exc)}
            results.append(err_result)
            state.record(model_id, job, status="error", error=str(exc))

        Path("train_results.json").write_text(
            json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    if remaining:
        Path("remaining_jobs.json").write_text(
            json.dumps(remaining, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        log(
            f"Time budget ({budget/3600:.1f}h) reached; {len(remaining)} job(s) "
            "deferred -> remaining_jobs.json.",
            level="warning",
        )
    log(f"\nDone: {len(results)} job(s) processed")


if __name__ == "__main__":
    main()
