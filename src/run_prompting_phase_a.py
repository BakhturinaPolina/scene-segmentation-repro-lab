"""Phase A orchestrator: prompt-family sweep on OpenRouter free baseline.

Runs prompt families (A-J by default) via run_prompting_stratified.py with
consistent decode settings, then writes a manifest with per-family outcomes.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import date
from pathlib import Path


STRUCTURED_FAMILIES = {"B", "C", "D", "E", "F", "G", "I", "J"}


def parse_families(value: str) -> list[str]:
    raw = [x.strip().upper() for x in value.split(",") if x.strip()]
    valid = [x for x in raw if x in set("ABCDEFGHIJ")]
    if not valid:
        raise ValueError("No valid families in --families (expected A..J)")
    return valid


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--families", type=str, default="A,B,C,D,E,F,G,H,I,J",
                        help="Comma-separated prompt families (default: A..J)")
    parser.add_argument("--model", type=str, default="openrouter/free",
                        help="Model for Phase A sweep (default: openrouter/free)")
    parser.add_argument("--date", type=str, default=None,
                        help="Output date folder override (default: today)")
    parser.add_argument("--dry_run", type=int, default=20,
                        help="Per-document sentence cap for fast screening (default: 20)")
    parser.add_argument("--max_per_class", type=int, default=15,
                        help="Per-class cap when not using full_eval (default: 15)")
    parser.add_argument("--full_eval", action="store_true",
                        help="Use full-eval mode instead of stratified sampling")
    parser.add_argument("--reasoning", choices=["on", "off", "low"], default="off",
                        help="Reasoning effort for baseline sweep (default: off)")
    parser.add_argument("--temperature", type=float, default=0.0,
                        help="Decoding temperature (default: 0.0)")
    parser.add_argument("--top_p", type=float, default=1.0,
                        help="Decoding top_p (default: 1.0)")
    parser.add_argument("--max_tokens", type=int, default=256,
                        help="Max output tokens (default: 256)")
    parser.add_argument("--chunk_window", type=int, default=2,
                        help="Chunk half-window for H/I families (default: 2)")
    parser.add_argument("--score_threshold", type=float, default=50.0,
                        help="Score threshold for I family (default: 50)")
    parser.add_argument("--prompts_dir", type=Path,
                        default=Path(__file__).resolve().parent / "prompts",
                        help="Prompt templates directory (default: src/prompts)")
    parser.add_argument("--manifest_file", type=Path, default=None,
                        help="Optional manifest output path")
    args = parser.parse_args()

    families = parse_families(args.families)
    run_date = args.date or date.today().isoformat()
    root = Path(__file__).resolve().parent.parent
    stratified_script = root / "src" / "run_prompting_stratified.py"
    requested_reasoning = args.reasoning
    effective_reasoning = requested_reasoning
    if args.model == "openrouter/free" and requested_reasoning == "off":
        # OpenRouter free endpoint requires reasoning to be enabled.
        effective_reasoning = "low"
        print(
            "Phase A note: openrouter/free rejects '--reasoning off'; "
            "using '--reasoning low' instead.",
            flush=True,
        )

    manifest = {
        "phase": "A",
        "date": run_date,
        "model": args.model,
        "families": families,
        "config": {
            "dry_run": args.dry_run,
            "max_per_class": args.max_per_class,
            "full_eval": args.full_eval,
            "reasoning_requested": requested_reasoning,
            "reasoning_effective": effective_reasoning,
            "temperature": args.temperature,
            "top_p": args.top_p,
            "max_tokens": args.max_tokens,
            "chunk_window": args.chunk_window,
            "score_threshold": args.score_threshold,
        },
        "runs": [],
    }

    for family in families:
        response_format = "json_object" if family in STRUCTURED_FAMILIES else "none"
        cmd = [
            sys.executable,
            str(stratified_script),
            "--model", args.model,
            "--date", run_date,
            "--prompt_family", family,
            "--reasoning", effective_reasoning,
            "--temperature", str(args.temperature),
            "--top_p", str(args.top_p),
            "--max_tokens", str(args.max_tokens),
            "--response_format", response_format,
            "--prompts_dir", str(args.prompts_dir),
            "--dry_run", str(args.dry_run),
            "--max_per_class", str(args.max_per_class),
            "--chunk_window", str(args.chunk_window),
            "--score_threshold", str(args.score_threshold),
        ]
        if args.full_eval:
            cmd.append("--full_eval")

        print(f"\n=== Phase A family {family} ===", flush=True)
        print(" ".join(cmd), flush=True)
        t0 = time.time()
        completed = subprocess.run(cmd, check=False)
        elapsed = round(time.time() - t0, 2)

        manifest["runs"].append(
            {
                "family": family,
                "response_format": response_format,
                "exit_code": completed.returncode,
                "elapsed_seconds": elapsed,
                "command": cmd,
            }
        )

    if args.manifest_file:
        manifest_path = args.manifest_file
    else:
        manifest_path = root / "outputs" / "prompting" / run_date / "phase_a_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\nPhase A manifest: {manifest_path}", flush=True)


if __name__ == "__main__":
    main()
