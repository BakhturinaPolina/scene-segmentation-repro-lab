"""Top-level STSS-Test-2 reproducibility orchestrator."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import date
from datetime import datetime
from pathlib import Path

_FILE = Path(__file__).resolve()
_SRC_ROOT = _FILE.parents[1]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from core.workflow_runtime import output_dir_for, project_root, write_repro_files

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


def _bar(done: int, total: int, width: int = 24) -> str:
    total = max(1, total)
    done = max(0, min(done, total))
    filled = int((done / total) * width)
    return "[" + ("#" * filled) + ("-" * (width - filled)) + f"] {done}/{total}"


def run_step(
    name: str,
    cmd: list[str],
    cwd: Path,
    env: dict[str, str] | None = None,
    step_index: int = 1,
    total_steps: int = 1,
) -> dict[str, object]:
    # region agent log
    _debug_log(
        "stss2_repro_runtime",
        "H1",
        "src/reproduce_stss_test_2.py:35",
        "orchestrator_step_start",
        {"step": name, "cmd": cmd, "cwd": str(cwd)},
    )
    # endregion
    t0 = time.time()
    log(f"{_bar(step_index, total_steps)} start `{name}`")
    log(f"  cwd={cwd}")
    log(f"  cmd={' '.join(cmd)}")
    proc = subprocess.Popen(cmd, cwd=cwd, env=env)
    heartbeat_every = 30
    last_heartbeat = t0
    while proc.poll() is None:
        now = time.time()
        if now - last_heartbeat >= heartbeat_every:
            elapsed = round(now - t0, 1)
            log(f"  {name}: still running ({elapsed}s elapsed)")
            last_heartbeat = now
        time.sleep(1)
    return_code = proc.returncode
    result = {
        "name": name,
        "command": cmd,
        "cwd": str(cwd),
        "exit_code": return_code,
        "elapsed_seconds": round(time.time() - t0, 2),
        "status": "success" if return_code == 0 else "failed",
    }
    log(
        f"{_bar(step_index, total_steps)} done `{name}` "
        f"status={result['status']} exit={return_code} elapsed={result['elapsed_seconds']}s"
    )
    # region agent log
    _debug_log(
        "stss2_repro_runtime",
        "H1",
        "src/reproduce_stss_test_2.py:50",
        "orchestrator_step_end",
        {"step": name, "exit_code": return_code, "elapsed_seconds": result["elapsed_seconds"]},
    )
    # endregion
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", type=str, default=None, help="Output date folder override.")
    parser.add_argument(
        "--heavy_timeout_seconds",
        type=int,
        default=1800,
        help="Timeout passed to SSC/LLaMA wrapper steps (default: 1800).",
    )
    args = parser.parse_args()

    root = project_root(Path(__file__))
    run_date = args.date or date.today().isoformat()
    out_dir = output_dir_for(root, "reproduction", run_date, "stss_test_2")
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = out_dir / "manifest.json"
    write_repro_files(
        out_dir,
        sys.argv,
        {"date": run_date, "manifest": str(manifest_path), "scope": "stss_test_2_only"},
    )

    steps: list[dict[str, object]] = []
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    total_steps = 7
    # region agent log
    _debug_log(
        "stss2_repro_runtime",
        "H2",
        "src/reproduce_stss_test_2.py:75",
        "orchestrator_start",
        {"date": run_date, "has_api_key": bool(env.get("OPENROUTER_API_KEY"))},
    )
    # endregion

    steps.append(
        run_step(
            "verify_data_manifest",
            [sys.executable, "src/data/verify_data_manifest.py"],
            cwd=root,
            env=env,
            step_index=1,
            total_steps=total_steps,
        )
    )
    steps.append(
        run_step(
            "unit_tests",
            [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
            cwd=root,
            env=env,
            step_index=2,
            total_steps=total_steps,
        )
    )

    api_key = env.get("OPENROUTER_API_KEY", "")
    has_api = bool(api_key and api_key != "Your OpenRouter API Key")
    if has_api:
        steps.append(
            run_step(
                "prompting_baseline_smoke",
                [
                    sys.executable,
                    "src/runners/run_prompting_baseline.py",
                    "--model",
                    "nvidia/nemotron-3-super-120b-a12b:free",
                    "--max_sentences",
                    "5",
                    "--reasoning",
                    "low",
                ],
                cwd=root,
                env=env,
                step_index=3,
                total_steps=total_steps,
            )
        )
        steps.append(
            run_step(
                "prompting_stratified_smoke",
                [
                    sys.executable,
                    "src/runners/run_prompting_stratified.py",
                    "--model",
                    "nvidia/nemotron-3-super-120b-a12b:free",
                    "--dry_run",
                    "3",
                    "--max_per_class",
                    "2",
                    "--reasoning",
                    "low",
                ],
                cwd=root,
                env=env,
                step_index=4,
                total_steps=total_steps,
            )
        )
        steps.append(
            run_step(
                "prompting_phase_a_smoke",
                [
                    sys.executable,
                    "src/runners/run_prompting_phase_a.py",
                    "--families",
                    "A",
                    "--model",
                    "nvidia/nemotron-3-super-120b-a12b:free",
                    "--dry_run",
                    "1",
                    "--max_per_class",
                    "1",
                    "--reasoning",
                    "low",
                ],
                cwd=root,
                env=env,
                step_index=5,
                total_steps=total_steps,
            )
        )
    else:
        # region agent log
        _debug_log(
            "stss2_repro_runtime",
            "H4",
            "src/reproduce_stss_test_2.py:140",
            "api_steps_skipped",
            {"reason": "OPENROUTER_API_KEY not set"},
        )
        # endregion
        steps.extend(
            [
                {
                    "name": "prompting_baseline_smoke",
                    "status": "skipped",
                    "reason": "OPENROUTER_API_KEY not set",
                    "progress_index": 3,
                },
                {
                    "name": "prompting_stratified_smoke",
                    "status": "skipped",
                    "reason": "OPENROUTER_API_KEY not set",
                    "progress_index": 4,
                },
                {
                    "name": "prompting_phase_a_smoke",
                    "status": "skipped",
                    "reason": "OPENROUTER_API_KEY not set",
                    "progress_index": 5,
                },
            ]
        )
        log(f"{_bar(3, total_steps)} skipped `prompting_baseline_smoke` (no API key)")
        log(f"{_bar(4, total_steps)} skipped `prompting_stratified_smoke` (no API key)")
        log(f"{_bar(5, total_steps)} skipped `prompting_phase_a_smoke` (no API key)")

    if ".venv-gpu" in env.get("VIRTUAL_ENV", ""):
        steps.append(
            run_step(
                "ssc_baseline",
                [
                    sys.executable,
                    "src/runners/run_ssc_baseline.py",
                    "--timeout_seconds",
                    str(args.heavy_timeout_seconds),
                ],
                cwd=root,
                env=env,
                step_index=6,
                total_steps=total_steps,
            )
        )
        steps.append(
            run_step(
                "llama_baseline",
                [
                    sys.executable,
                    "src/runners/run_llama_baseline.py",
                    "--timeout_seconds",
                    str(args.heavy_timeout_seconds),
                ],
                cwd=root,
                env=env,
                step_index=7,
                total_steps=total_steps,
            )
        )
    else:
        # region agent log
        _debug_log(
            "stss2_repro_runtime",
            "H3",
            "src/reproduce_stss_test_2.py:165",
            "gpu_steps_skipped",
            {"reason": ".venv-gpu not active", "virtual_env": env.get("VIRTUAL_ENV", "")},
        )
        # endregion
        steps.extend(
            [
                {"name": "ssc_baseline", "status": "skipped", "reason": ".venv-gpu not active", "progress_index": 6},
                {"name": "llama_baseline", "status": "skipped", "reason": ".venv-gpu not active", "progress_index": 7},
            ]
        )
        log(f"{_bar(6, total_steps)} skipped `ssc_baseline` (.venv-gpu not active)")
        log(f"{_bar(7, total_steps)} skipped `llama_baseline` (.venv-gpu not active)")

    manifest = {"date": run_date, "scope": "stss_test_2_only", "steps": steps}
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    log(f"Wrote manifest: {manifest_path}")

    failed = [s for s in steps if s.get("status") == "failed"]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
