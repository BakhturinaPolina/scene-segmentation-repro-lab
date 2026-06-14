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
"""HF Jobs / local GPU: eval-only for an existing LoRA adapter (no training).

Loads adapter + held-out ``eval.jsonl`` from the SFT dataset, runs batched greedy
generation with parse diagnostics, writes ``metrics_<model>_<job>.json``, and
uploads it next to the adapter repo.

HF Jobs spot-check::

    hf jobs uv run --flavor t4-small --timeout 1h --secrets HF_TOKEN -d \\
      -e HF_USER=RuthonField \\
      -e DATA_REPO=RuthonField/scene-seg-sft \\
      -e SCENE_SEG_JOBS=fold_A \\
      -e EVAL_LIMIT=20 \\
      -e EVAL_MAX_NEW_TOKENS=256 \\
      -e ADAPTER=RuthonField/scene-seg-llama-3-2-3b-instruct-fold_A \\
      src/finetune/hf_jobs/eval_job.py
"""

from __future__ import annotations

import importlib
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

_HF_JOB_BUNDLE_PREFIX = "_hf_job_bundle"
_HF_JOB_SRC_CACHE = Path("/tmp/scene_seg_src")


def _has_project_modules(root: Path) -> bool:
    return (
        (root / "finetune" / "run_log.py").is_file()
        and (root / "finetune" / "label_parse.py").is_file()
        and (root / "postprocess" / "postprocess.py").is_file()
        and (root / "train_job.py").is_file()
    )


def _materialize_hf_job_bundle() -> Path:
    if _has_project_modules(_HF_JOB_SRC_CACHE):
        return _HF_JOB_SRC_CACHE

    data_repo = os.environ.get("DATA_REPO")
    if not data_repo:
        raise ImportError("Set DATA_REPO for HF Jobs eval (dataset with _hf_job_bundle/).")

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
        raise FileNotFoundError(f"{data_repo} missing {_HF_JOB_BUNDLE_PREFIX}/")

    if _HF_JOB_SRC_CACHE.exists():
        shutil.rmtree(_HF_JOB_SRC_CACHE)
    shutil.copytree(bundle, _HF_JOB_SRC_CACHE)
    return _HF_JOB_SRC_CACHE


def _load_train_job_module():
    here = Path(__file__).resolve().parent
    for candidate in (here, _materialize_hf_job_bundle()):
        if _has_project_modules(candidate):
            if str(candidate) not in sys.path:
                sys.path.insert(0, str(candidate))
            return importlib.import_module("train_job")
    raise ImportError("Cannot locate train_job.py with project bundle")


tj = _load_train_job_module()
evaluate_adapter = tj.evaluate_adapter
load_config = tj.load_config
log = tj.log
model_short_name = tj.model_short_name
read_jsonl = tj.read_jsonl
resolve_data_dir = tj.resolve_data_dir
resolve_hf_token = tj.resolve_hf_token
upload_if_hub = tj.upload_if_hub


def _adapter_repo(cfg: Dict[str, Any], model_id: str, job: str) -> str:
    if cfg.get("adapter"):
        return str(cfg["adapter"])
    user = cfg.get("hf_user", "")
    short = model_short_name(model_id)
    return f"{user}/scene-seg-{short}-{job}" if user else f"scene-seg-{short}-{job}"


def eval_one(
    model_id: str,
    job: str,
    cfg: Dict[str, Any],
    hf_token: str,
    data_root: Path,
) -> Dict[str, Any]:
    from unsloth import FastLanguageModel  # noqa: F401, PLC0415

    job_dir = data_root / job
    eval_path = job_dir / "eval.jsonl"
    if not eval_path.exists():
        raise FileNotFoundError(f"Missing eval file: {eval_path}")

    adapter_repo = _adapter_repo(cfg, model_id, job)
    max_len = int(cfg.get("max_seq_len", 1280))
    log(f"Loading adapter {adapter_repo} max_seq_len={max_len}")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=adapter_repo,
        max_seq_length=max_len,
        load_in_4bit=True,
        dtype=None,
    )

    eval_rows = read_jsonl(eval_path)
    log(f"Evaluating {len(eval_rows)} rows (eval_limit={cfg.get('eval_limit', 0)})")
    metrics = evaluate_adapter(model, tokenizer, eval_rows, cfg)
    metrics.update(
        {
            "model": model_id,
            "job": job,
            "adapter": adapter_repo,
            "family": cfg.get("family", "L"),
            "eval_mode": "eval_only",
            "eval_limit": int(cfg.get("eval_limit", 0)),
        }
    )

    short = model_short_name(model_id)
    metrics_path = Path(f"metrics_{short}_{job}.json")
    metrics_path.write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    log(
        f"metrics: n_pred_border={metrics.get('n_pred_border')} "
        f"parse_fail={metrics.get('parse_failure_rate')} "
        f"macro_f1@3={metrics.get('scenarios', {}).get('none', {}).get('tol_3', {}).get('macro_f1')} "
        f"-> {metrics_path}"
    )
    upload_if_hub(metrics_path, adapter_repo, hf_token)
    return {"model": model_id, "job": job, "adapter": adapter_repo, "metrics_path": str(metrics_path)}


def main() -> None:
    import torch  # noqa: PLC0415

    if not torch.cuda.is_available():
        log("ERROR: CUDA required. Use HF Jobs or a machine with a GPU.", level="error")
        sys.exit(1)

    cfg = load_config()
    cfg["eval_after_train"] = False
    if os.environ.get("EVAL_LIMIT"):
        cfg["eval_limit"] = int(os.environ["EVAL_LIMIT"])
    if os.environ.get("EVAL_MAX_NEW_TOKENS"):
        cfg["eval_max_new_tokens"] = int(os.environ["EVAL_MAX_NEW_TOKENS"])
    if os.environ.get("ADAPTER"):
        cfg["adapter"] = os.environ["ADAPTER"]

    hf_token = resolve_hf_token(cfg)
    if not cfg.get("hf_user"):
        try:
            from huggingface_hub import whoami  # noqa: PLC0415

            cfg["hf_user"] = whoami(token=hf_token or None)["name"]
        except Exception:  # noqa: BLE001
            pass

    data_root = resolve_data_dir(cfg, hf_token)
    extra_cfg_path = data_root / "hf_eval_spotcheck.json"
    if extra_cfg_path.exists():
        cfg.update(json.loads(extra_cfg_path.read_text(encoding="utf-8")))
        log(f"Merged config from {extra_cfg_path}")

    jobs = cfg.get("jobs") or []
    models = cfg.get("models") or []
    log(f"Eval-only: models={models} jobs={jobs} eval_limit={cfg.get('eval_limit', 0)}")

    results: List[Dict[str, Any]] = []
    for model_id in models:
        for job in jobs:
            log(f"\n=== Eval-only {model_id} on {job} ===")
            try:
                result = eval_one(model_id, job, cfg, hf_token, data_root)
                results.append(result)
            except Exception as exc:  # noqa: BLE001
                log(f"ERROR on ({model_id}, {job}): {exc}", level="error")
                results.append({"model": model_id, "job": job, "error": str(exc)})

    Path("eval_results.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    log(f"Done: {len(results)} eval job(s)")


if __name__ == "__main__":
    main()
