"""Run SSC STSS-Test-2 baseline with reproducibility artifacts."""

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
        log(f"[ssc:{stream_name}] {line.rstrip()}")
    stream.close()


def run() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", type=str, default=None, help="Output date folder override.")
    parser.add_argument("--model_name", type=str, default="bert-base-german-cased")
    parser.add_argument("--tokenizer_name", type=str, default="bert-base-german-cased")
    parser.add_argument("--context_size", type=int, default=512)
    parser.add_argument("--stride", type=str, default="full")
    parser.add_argument("--label_set", type=str, default="Coarse")
    parser.add_argument("--train_batch_size", type=int, default=1)
    parser.add_argument("--eval_batch_size", type=int, default=1)
    parser.add_argument("--num_train_epochs", type=int, default=1)
    parser.add_argument("--random_seed", type=int, default=42)
    parser.add_argument(
        "--timeout_seconds",
        type=int,
        default=1800,
        help="Hard timeout for the SSC subprocess (default: 1800).",
    )
    args = parser.parse_args()

    root = project_root(Path(__file__))
    run_date = args.date or date.today().isoformat()
    out_dir = output_dir_for(root, "ssc", run_date, "baseline_bert_stss_test_2")
    out_dir.mkdir(parents=True, exist_ok=True)
    run_id = f"ssc_baseline_{run_date}"
    # region agent log
    _debug_log(
        run_id,
        "H1",
        "src/run_ssc_baseline.py:43",
        "ssc_wrapper_start",
        {
            "model_name": args.model_name,
            "epochs": args.num_train_epochs,
            "train_batch_size": args.train_batch_size,
            "eval_batch_size": args.eval_batch_size,
            "timeout_seconds": args.timeout_seconds,
        },
    )
    # endregion

    cfg = {
        "model_name": args.model_name,
        "tokenizer_name": args.tokenizer_name,
        "context_size": args.context_size,
        "stride": args.stride,
        "label_set": args.label_set,
        "train_batch_size": args.train_batch_size,
        "eval_batch_size": args.eval_batch_size,
        "num_train_epochs": args.num_train_epochs,
        "random_seed": args.random_seed,
        "timeout_seconds": args.timeout_seconds,
        "train_files": "data/full/stss_test_2",
        "test_files": "data/full/stss_test_2",
        "output_dir": str(out_dir),
    }
    # Upstream SSC serialization writes annotated XMI files into
    # <output_dir>/<dataset_folder_name>/..., so pre-create that subdir.
    (out_dir / Path(cfg["test_files"]).name).mkdir(parents=True, exist_ok=True)
    write_repro_files(out_dir, sys.argv, cfg)

    summary_path = out_dir / "run_summary.json"
    if ".venv-gpu" not in os.environ.get("VIRTUAL_ENV", ""):
        msg = (
            "SSC baseline wrapper expects .venv-gpu to be active. "
            "Activate with: source .venv-gpu/bin/activate"
        )
        # region agent log
        _debug_log(
            run_id,
            "H3",
            "src/run_ssc_baseline.py:72",
            "ssc_wrapper_skip_no_gpu_env",
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
        "-m",
        "ssc.main",
        "--model_name",
        args.model_name,
        "--tokenizer_name",
        args.tokenizer_name,
        "--context_size",
        str(args.context_size),
        "--stride",
        args.stride,
        "--label_set",
        args.label_set,
        "--train_files",
        "data/full/stss_test_2",
        "--test_files",
        "data/full/stss_test_2",
        "--train_batch_size",
        str(args.train_batch_size),
        "--eval_batch_size",
        str(args.eval_batch_size),
        "--num_train_epochs",
        str(args.num_train_epochs),
        "--output_dir",
        str(out_dir),
        "--random_seed",
        str(args.random_seed),
        "--lstm_num_layers",
        "0",
        "--lstm_hidden_size",
        "0",
    ]

    env = os.environ.copy()
    env["PYTHONPATH"] = str(upstream_root) + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONUNBUFFERED"] = "1"
    stdout_path = out_dir / "stdout.log"
    stderr_path = out_dir / "stderr.log"
    # region agent log
    _debug_log(
        run_id,
        "H2",
        "src/run_ssc_baseline.py:127",
        "ssc_subprocess_start",
        {"cwd": str(upstream_root), "cmd": cmd, "output_dir": str(out_dir)},
    )
    # endregion
    log(f"Starting SSC subprocess with timeout={args.timeout_seconds}s")
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
                log(f"Timeout reached: {args.timeout_seconds}s, terminating SSC subprocess")
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()
                break
            if now - last_heartbeat >= heartbeat_every:
                log(f"[ssc-progress] {_timeout_bar(now - t0, args.timeout_seconds)}")
                last_heartbeat = now
            time.sleep(1)
        out_thread.join(timeout=5)
        err_thread.join(timeout=5)
        return_code = 124 if timed_out else proc.returncode
        if timed_out:
            stderr.write(f"\nSSC subprocess timed out after {args.timeout_seconds}s.\n")
        proc = subprocess.CompletedProcess(cmd, returncode=return_code)
    elapsed = round(time.time() - t0, 2)
    log(f"SSC subprocess finished with exit={proc.returncode} in {elapsed}s")
    # region agent log
    _debug_log(
        run_id,
        "H1",
        "src/run_ssc_baseline.py:140",
        "ssc_subprocess_end",
        {"exit_code": proc.returncode, "elapsed_seconds": elapsed, "timed_out": timed_out},
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
                    else ("timeout" if timed_out else "ssc_runtime_error")
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
