"""Run LLaMA STSS-Test-2 baseline with a small 4-bit model."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
import time
from datetime import date
from datetime import datetime
from pathlib import Path

from workflow_runtime import output_dir_for, project_root, write_repro_files

DEBUG_LOG_PATH = Path("/home/polina/Documents/Cursor_Projects/scene-segmentation-research/.cursor/debug-efbea3.log")
DEBUG_SESSION_ID = "efbea3"


def _debug_log(run_id: str, hypothesis_id: str, location: str, message: str, data: dict) -> None:
    payload = {
        "sessionId": DEBUG_SESSION_ID,
        "runId": run_id,
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
        "timestamp": int(time.time() * 1000),
    }
    with DEBUG_LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def log(msg: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def _timeout_bar(elapsed: float, timeout_seconds: int, width: int = 24) -> str:
    timeout_seconds = max(1, timeout_seconds)
    frac = max(0.0, min(1.0, elapsed / timeout_seconds))
    filled = int(width * frac)
    return (
        "["
        + ("#" * filled)
        + ("-" * (width - filled))
        + f"] {int(elapsed)}s/{timeout_seconds}s"
    )


def _pump_stream(stream, log_handle, stream_name: str) -> None:
    for line in iter(stream.readline, ""):
        log_handle.write(line)
        log_handle.flush()
        log(f"[llama:{stream_name}] {line.rstrip()}")
    stream.close()


def run() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", type=str, default=None, help="Output date folder override.")
    parser.add_argument(
        "--model",
        type=str,
        default="unsloth/Phi-3-mini-4k-instruct-bnb-4bit",
    )
    parser.add_argument("--context_size", type=int, default=128)
    parser.add_argument("--num_train_epochs", type=int, default=1)
    parser.add_argument("--cot_config", type=str, default="no_cot")
    parser.add_argument("--random_seed", type=int, default=42)
    parser.add_argument("--per_device_train_batch_size", type=int, default=1)
    parser.add_argument("--gradient_accumulation_steps", type=int, default=16)
    parser.add_argument(
        "--timeout_seconds",
        type=int,
        default=1800,
        help="Hard timeout for the LLaMA subprocess (default: 1800).",
    )
    args = parser.parse_args()

    root = project_root(Path(__file__))
    run_date = args.date or date.today().isoformat()
    out_dir = output_dir_for(root, "llama", run_date, "baseline_phi3mini_stss_test_2")
    out_dir.mkdir(parents=True, exist_ok=True)
    run_id = f"llama_baseline_{run_date}"
    # region agent log
    _debug_log(
        run_id,
        "H5",
        "src/run_llama_baseline.py:49",
        "llama_wrapper_start",
        {
            "model": args.model,
            "context_size": args.context_size,
            "batch_size": args.per_device_train_batch_size,
            "grad_accum": args.gradient_accumulation_steps,
            "timeout_seconds": args.timeout_seconds,
        },
    )
    # endregion

    cfg = {
        "model": args.model,
        "context_size": args.context_size,
        "num_train_epochs": args.num_train_epochs,
        "cot_config": args.cot_config,
        "random_seed": args.random_seed,
        "per_device_train_batch_size": args.per_device_train_batch_size,
        "gradient_accumulation_steps": args.gradient_accumulation_steps,
        "timeout_seconds": args.timeout_seconds,
        "train_folder": "data/full/stss_test_2",
        "test_folder": "data/full/stss_test_2",
        "model_identifier": str(out_dir),
    }
    write_repro_files(out_dir, sys.argv, cfg)

    summary_path = out_dir / "run_summary.json"
    if ".venv-gpu" not in os.environ.get("VIRTUAL_ENV", ""):
        msg = (
            "LLaMA baseline wrapper expects .venv-gpu to be active. "
            "Activate with: source .venv-gpu/bin/activate"
        )
        # region agent log
        _debug_log(
            run_id,
            "H3",
            "src/run_llama_baseline.py:83",
            "llama_wrapper_skip_no_gpu_env",
            {"virtual_env": os.environ.get("VIRTUAL_ENV", "")},
        )
        # endregion
        (out_dir / "stderr.log").write_text(msg + "\n", encoding="utf-8")
        summary_path.write_text(
            json.dumps(
                {
                    "status": "skipped",
                    "failure_category": "gpu_env_not_active",
                    "message": msg,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        log(msg)
        return 2

    upstream_root = root / "upstream" / "scene-segmentation"
    cmd = [
        sys.executable,
        "llama/train_unsloth.py",
        "--train_folder",
        "data/full/stss_test_2",
        "--test_folder",
        "data/full/stss_test_2",
        "--model_identifier",
        str(out_dir),
        "--context_size",
        str(args.context_size),
        "--random_seed",
        str(args.random_seed),
        "--model",
        args.model,
        "--num_train_epochs",
        str(args.num_train_epochs),
        "--cot_config",
        args.cot_config,
        "--per_device_train_batch_size",
        str(args.per_device_train_batch_size),
        "--gradient_accumulation_steps",
        str(args.gradient_accumulation_steps),
    ]

    env = os.environ.copy()
    env["PYTHONPATH"] = str(upstream_root) + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONUNBUFFERED"] = "1"
    stdout_path = out_dir / "stdout.log"
    stderr_path = out_dir / "stderr.log"
    # region agent log
    _debug_log(
        run_id,
        "H5",
        "src/run_llama_baseline.py:123",
        "llama_subprocess_start",
        {"cmd": cmd, "cwd": str(upstream_root)},
    )
    # endregion
    log(f"Starting LLaMA subprocess with timeout={args.timeout_seconds}s")
    log(f"Command: {' '.join(cmd)}")
    t0 = time.time()
    timed_out = False
    with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
        proc = subprocess.Popen(
            cmd,
            cwd=upstream_root,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        out_thread = threading.Thread(target=_pump_stream, args=(proc.stdout, stdout, "stdout"), daemon=True)
        err_thread = threading.Thread(target=_pump_stream, args=(proc.stderr, stderr, "stderr"), daemon=True)
        out_thread.start()
        err_thread.start()
        heartbeat_every = 30
        last_heartbeat = t0
        while proc.poll() is None:
            now = time.time()
            if now - t0 >= args.timeout_seconds:
                timed_out = True
                log(f"Timeout reached: {args.timeout_seconds}s, terminating LLaMA subprocess")
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()
                break
            if now - last_heartbeat >= heartbeat_every:
                log(f"[llama-progress] {_timeout_bar(now - t0, args.timeout_seconds)}")
                last_heartbeat = now
            time.sleep(1)
        out_thread.join(timeout=5)
        err_thread.join(timeout=5)
        return_code = 124 if timed_out else proc.returncode
        if timed_out:
            stderr.write(f"\nLLaMA subprocess timed out after {args.timeout_seconds}s.\n")
        proc = subprocess.CompletedProcess(cmd, returncode=return_code)
    elapsed = round(time.time() - t0, 2)
    log(f"LLaMA subprocess finished with exit={proc.returncode} in {elapsed}s")

    stderr_text = stderr_path.read_text(encoding="utf-8", errors="ignore").lower()
    stdout_text = stdout_path.read_text(encoding="utf-8", errors="ignore").lower()
    oom = "out of memory" in stderr_text or "out of memory" in stdout_text
    # region agent log
    _debug_log(
        run_id,
        "H5",
        "src/run_llama_baseline.py:139",
        "llama_subprocess_end",
        {"exit_code": proc.returncode, "elapsed_seconds": elapsed, "oom_detected": oom, "timed_out": timed_out},
    )
    # endregion
    summary_path.write_text(
        json.dumps(
            {
                "status": "success" if proc.returncode == 0 else "failed",
                "exit_code": proc.returncode,
                "failure_category": (
                    ""
                    if proc.returncode == 0
                    else ("timeout" if timed_out else ("cuda_oom" if oom else "llama_runtime_error"))
                ),
                "stdout_log": str(stdout_path),
                "stderr_log": str(stderr_path),
                "timed_out": timed_out,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(run())
