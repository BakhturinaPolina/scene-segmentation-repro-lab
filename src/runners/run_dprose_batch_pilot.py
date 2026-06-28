#!/usr/bin/env python3
"""dProse scene segmentation pilot via Gemini Batch API.

Builds Prompt Family B requests from a dProse manifest, submits a batch job
(inline smoke or JSONL file upload), polls for completion, and writes
predictions + summary artifacts.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from google import genai

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.core.prompt_runtime import get_template_text, load_prompt_registry  # noqa: E402
from src.runners.dprose_batch_core import (  # noqa: E402
    BatchRunConfig,
    SentenceRecord,
    build_generation_config,
    load_manifest,
    load_response_schema,
    log,
    poll_batch_job,
    prepare_requests,
    process_results,
    submit_batch_job,
    iter_file_results,
    iter_inline_results,
)

COMPLETED_STATES = frozenset()  # kept for backward compat imports; use dprose_batch_core


def _require_api_key() -> str:
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        log("ERROR: Set GEMINI_API_KEY (e.g. set -a && source .env && set +a)")
        sys.exit(1)
    return api_key


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("data/manifests/dprose_pilot.json"))
    parser.add_argument("--data_root", type=Path, default=Path("data"))
    parser.add_argument("--mode", choices=["inline", "file"], default="inline")
    parser.add_argument("--model", default="gemini-2.5-pro")
    parser.add_argument("--prompt_family", default="B")
    parser.add_argument("--prompts_dir", type=Path, default=Path("src/prompts"))
    parser.add_argument(
        "--schema_file",
        type=Path,
        default=Path("src/prompts/json_schema_label_reason.json"),
    )
    parser.add_argument("--context_sentences", type=int, default=12)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max_output_tokens", type=int, default=2048)
    parser.add_argument("--thinking_budget", type=int, default=-1)
    parser.add_argument("--max_sentences", type=int, default=None)
    parser.add_argument("--poll_interval", type=int, default=30)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--date", default=None, help="Run tag / output folder name.")
    parser.add_argument(
        "--resume",
        type=Path,
        default=None,
        help="Path to job_meta.json from a prior submit.",
    )
    parser.add_argument(
        "--output_root",
        type=Path,
        default=Path("outputs/runs/dprose_batch"),
    )
    return parser.parse_args()


def output_dir_for(args: argparse.Namespace) -> Path:
    tag = args.date or datetime.now(timezone.utc).strftime("%Y-%m-%d-dprose-batch")
    return args.output_root / tag


def main() -> int:
    args = parse_args()
    _require_api_key()
    client = genai.Client()

    out_dir = output_dir_for(args)
    out_dir.mkdir(parents=True, exist_ok=True)

    run_config = BatchRunConfig(
        model=args.model,
        mode=args.mode,
        prompt_family=args.prompt_family,
        context_sentences=args.context_sentences,
        temperature=args.temperature,
        max_output_tokens=args.max_output_tokens,
        thinking_budget=args.thinking_budget,
        poll_interval=args.poll_interval,
    )

    if args.resume:
        meta = json.loads(args.resume.read_text(encoding="utf-8"))
        job_name = meta["job_name"]
        job_mode = meta.get("mode", args.mode)
        records = [SentenceRecord(**r) for r in meta["records"]]
        records_by_key = {r.key: r for r in records}
        log(f"Resuming job from {args.resume} (mode={job_mode})")
        batch_job = poll_batch_job(client, job_name, args.poll_interval)
    else:
        manifest = load_manifest(args.manifest)
        registry = load_prompt_registry(args.prompts_dir)
        template_text = get_template_text(args.prompts_dir, args.prompt_family, registry)
        response_schema = load_response_schema(args.schema_file)
        generation_config = build_generation_config(
            temperature=args.temperature,
            max_output_tokens=args.max_output_tokens,
            thinking_budget=args.thinking_budget,
            response_schema=response_schema,
        )

        records, inline_requests = prepare_requests(
            manifest,
            args.data_root,
            prompt_family=args.prompt_family,
            template_text=template_text,
            context_sentences=args.context_sentences,
            generation_config=generation_config,
            max_sentences=args.max_sentences,
        )
        records_by_key = {r.key: r for r in records}
        log(f"Prepared {len(records)} requests from {args.manifest}")

        batch_job, _job_meta_path = submit_batch_job(
            client,
            out_dir=out_dir,
            records=records,
            inline_requests=inline_requests,
            generation_config=generation_config,
            config=run_config,
            manifest_path=args.manifest,
        )
        job_mode = args.mode
        batch_job = poll_batch_job(client, batch_job.name or "", args.poll_interval)

    if job_mode == "file":
        result_rows = iter_file_results(client, batch_job)
    else:
        result_rows = iter_inline_results(batch_job)

    if not result_rows:
        log("ERROR: No batch results found")
        return 1

    predictions, summary = process_results(
        result_rows,
        records_by_key,
        prompt_family=args.prompt_family,
        verbose=args.verbose,
    )

    summary.update(
        {
            "model": args.model if not args.resume else json.loads((out_dir / "job_meta.json").read_text())["model"],
            "job_name": batch_job.name,
            "job_state": batch_job.state.name if batch_job.state else None,
            "mode": job_mode,
            "manifest": str(args.manifest),
            "prompt_family": args.prompt_family,
            "context_sentences": args.context_sentences,
            "thinking_budget": args.thinking_budget,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
    )

    pred_path = out_dir / "predictions.jsonl"
    with pred_path.open("w", encoding="utf-8") as handle:
        for row in predictions:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    summary_path = out_dir / "pilot_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    log("--- Summary ---")
    log(json.dumps(summary, indent=2))
    log(f"Wrote predictions: {pred_path}")
    log(f"Wrote summary: {summary_path}")
    return 0 if summary.get("parse_ok_rate", 0) >= 0.95 else 1


if __name__ == "__main__":
    raise SystemExit(main())
