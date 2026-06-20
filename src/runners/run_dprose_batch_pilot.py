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
import time
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from google import genai
from google.genai import types

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.core.prompt_runtime import (  # noqa: E402
    get_template_text,
    load_prompt_registry,
    parse_family_output,
    render_prompt_for_family,
)

COMPLETED_STATES = frozenset(
    {
        "JOB_STATE_SUCCEEDED",
        "JOB_STATE_FAILED",
        "JOB_STATE_CANCELLED",
        "JOB_STATE_EXPIRED",
    }
)

# Gemini 2.5 Pro batch pricing (USD per 1M tokens), per DPROSE_COST_ESTIMATE.md
BATCH_INPUT_USD_PER_M = 0.625
BATCH_OUTPUT_USD_PER_M = 5.0


@dataclass
class SentenceRecord:
    key: str
    source_file: str
    sentence_index: int
    sentence_text_full: str


def log(msg: str) -> None:
    print(msg, flush=True)


def _require_api_key() -> str:
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        log("ERROR: Set GEMINI_API_KEY (e.g. set -a && source .env && set +a)")
        sys.exit(1)
    return api_key


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    with manifest_path.open(encoding="utf-8") as handle:
        return json.load(handle)


def iter_sentences(manifest: dict[str, Any], data_root: Path) -> Iterator[SentenceRecord]:
    for entry in manifest.get("files", []):
        source_file = entry["source_file"]
        slug = entry.get("slug") or Path(source_file).stem
        jsonl_rel = entry.get("jsonl")
        if not jsonl_rel:
            raise ValueError(f"Manifest entry missing jsonl path: {entry}")
        jsonl_path = data_root / jsonl_rel
        with jsonl_path.open(encoding="utf-8") as handle:
            for line in handle:
                row = json.loads(line)
                idx = int(row["sentence_index"])
                key = f"{slug}:{idx}"
                yield SentenceRecord(
                    key=key,
                    source_file=source_file,
                    sentence_index=idx,
                    sentence_text_full=row["sentence_text_full"],
                )


def load_sentences_by_file(manifest: dict[str, Any], data_root: Path) -> dict[str, list[str]]:
    by_file: dict[str, list[str]] = {}
    for entry in manifest.get("files", []):
        source_file = entry["source_file"]
        txt_path = data_root / entry["name"]
        lines = [ln.strip() for ln in txt_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        by_file[source_file] = lines
    return by_file


def build_sample_text(
    sentences: list[str],
    index: int,
    *,
    context_sentences: int,
) -> str:
    start = max(0, index - context_sentences)
    end = min(len(sentences), index + context_sentences + 1)
    parts: list[str] = []
    for i in range(start, end):
        if i == index:
            parts.append(f"<sentence>{sentences[i]}</sentence>")
        else:
            parts.append(sentences[i])
    return " ".join(parts)


def load_response_schema(schema_path: Path) -> dict[str, Any]:
    payload = json.loads(schema_path.read_text(encoding="utf-8"))
    schema = payload["schema"] if "schema" in payload else payload
    return _sanitize_gemini_schema(schema)


def _sanitize_gemini_schema(obj: Any) -> Any:
    """Strip OpenAI-strict fields unsupported by Gemini response_schema."""
    if isinstance(obj, dict):
        cleaned: dict[str, Any] = {}
        for key, value in obj.items():
            if key in {"additionalProperties", "additional_properties", "strict", "name"}:
                continue
            cleaned[key] = _sanitize_gemini_schema(value)
        return cleaned
    if isinstance(obj, list):
        return [_sanitize_gemini_schema(item) for item in obj]
    return obj


def build_generation_config(
    *,
    temperature: float,
    max_output_tokens: int,
    thinking_budget: int,
    response_schema: dict[str, Any],
) -> dict[str, Any]:
    return {
        "temperature": temperature,
        "max_output_tokens": max_output_tokens,
        "response_mime_type": "application/json",
        "response_schema": response_schema,
        "thinking_config": {
            "thinking_budget": thinking_budget,
            "include_thoughts": True,
        },
    }


def build_inline_request(
    prompt_text: str,
    *,
    key: str,
    generation_config: dict[str, Any],
) -> dict[str, Any]:
    return {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt_text}],
            }
        ],
        "metadata": {"key": key},
        "config": generation_config,
    }


def build_file_request_line(
    prompt_text: str,
    *,
    key: str,
    generation_config: dict[str, Any],
) -> dict[str, Any]:
    return {
        "key": key,
        "request": {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt_text}],
                }
            ],
            "generation_config": generation_config,
        },
    }


def index_sentences_in_file(sentences: list[str]) -> dict[int, int]:
    """Map sentence_index (from jsonl) to position in txt file list."""
    return {i: i for i in range(len(sentences))}


def prepare_requests(
    manifest: dict[str, Any],
    data_root: Path,
    *,
    prompt_family: str,
    template_text: str,
    context_sentences: int,
    generation_config: dict[str, Any],
    max_sentences: int | None,
) -> tuple[list[SentenceRecord], list[dict[str, Any]]]:
    by_file = load_sentences_by_file(manifest, data_root)
    records: list[SentenceRecord] = []
    requests: list[dict[str, Any]] = []

    for rec in iter_sentences(manifest, data_root):
        if max_sentences is not None and len(records) >= max_sentences:
            break
        file_sentences = by_file[rec.source_file]
        pos = rec.sentence_index
        if pos < 0 or pos >= len(file_sentences):
            pos = len(records) % len(file_sentences)
        sample_text = build_sample_text(
            file_sentences, pos, context_sentences=context_sentences
        )
        prompt_text = render_prompt_for_family(prompt_family, template_text, sample_text)
        records.append(rec)
        requests.append(
            build_inline_request(
                prompt_text,
                key=rec.key,
                generation_config=generation_config,
            )
        )
    return records, requests


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def extract_usage(response: Any) -> dict[str, int]:
    usage = getattr(response, "usage_metadata", None)
    if usage is None:
        return {"prompt_tokens": 0, "output_tokens": 0, "thought_tokens": 0}
    prompt_tokens = int(getattr(usage, "prompt_token_count", 0) or 0)
    output_tokens = int(getattr(usage, "candidates_token_count", 0) or 0)
    thought_tokens = int(getattr(usage, "thoughts_token_count", 0) or 0)
    return {
        "prompt_tokens": prompt_tokens,
        "output_tokens": output_tokens,
        "thought_tokens": thought_tokens,
    }


def response_text_from_dict(response: dict[str, Any]) -> str:
    candidates = response.get("candidates") or []
    if not candidates:
        return ""
    content = candidates[0].get("content") or {}
    parts = content.get("parts") or []
    visible = [
        p.get("text", "")
        for p in parts
        if p.get("text") and not p.get("thought")
    ]
    if visible:
        return "".join(visible)
    return "".join(p.get("text", "") for p in parts if p.get("text"))


def usage_from_dict(response: dict[str, Any]) -> dict[str, int]:
    usage = response.get("usageMetadata") or response.get("usage_metadata") or {}
    return {
        "prompt_tokens": int(usage.get("promptTokenCount") or usage.get("prompt_token_count") or 0),
        "output_tokens": int(
            usage.get("candidatesTokenCount") or usage.get("candidates_token_count") or 0
        ),
        "thought_tokens": int(
            usage.get("thoughtsTokenCount") or usage.get("thoughts_token_count") or 0
        ),
    }


def response_text(response: Any) -> str:
    if response is None:
        return ""
    if isinstance(response, dict):
        return response_text_from_dict(response)
    text = getattr(response, "text", None)
    if text:
        return text
    candidates = getattr(response, "candidates", None) or []
    if not candidates:
        return ""
    parts = candidates[0].content.parts if candidates[0].content else []
    visible = [p.text for p in parts if getattr(p, "text", None) and not getattr(p, "thought", False)]
    if visible:
        return "".join(visible)
    all_text = [p.text for p in parts if getattr(p, "text", None)]
    return "".join(all_text)


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
    parser.add_argument("--max_output_tokens", type=int, default=1024)
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


def poll_batch_job(client: genai.Client, job_name: str, poll_interval: int) -> types.BatchJob:
    log(f"Polling batch job: {job_name}")
    batch_job = client.batches.get(name=job_name)
    state_name = batch_job.state.name if batch_job.state else "UNKNOWN"
    log(f"Initial state: {state_name}")
    while state_name not in COMPLETED_STATES:
        time.sleep(poll_interval)
        batch_job = client.batches.get(name=job_name)
        state_name = batch_job.state.name if batch_job.state else "UNKNOWN"
        log(f"  state={state_name}")
    log(f"Final state: {state_name}")
    if state_name == "JOB_STATE_FAILED" and batch_job.error:
        log(f"Job error: {batch_job.error}")
    return batch_job


def iter_inline_results(batch_job: types.BatchJob) -> list[tuple[str | None, Any, Any | None]]:
    dest = batch_job.dest
    if not dest or not dest.inlined_responses:
        return []
    rows: list[tuple[str | None, Any, Any | None]] = []
    for item in dest.inlined_responses:
        key = None
        if item.metadata:
            key = item.metadata.get("key")
        rows.append((key, item.response, item.error))
    return rows


def iter_file_results(client: genai.Client, batch_job: types.BatchJob) -> list[tuple[str | None, Any, Any | None]]:
    dest = batch_job.dest
    if not dest or not dest.file_name:
        return []
    log(f"Downloading result file: {dest.file_name}")
    raw = client.files.download(file=dest.file_name)
    text = raw.decode("utf-8") if isinstance(raw, (bytes, bytearray)) else str(raw)
    rows: list[tuple[str | None, Any, Any | None]] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        obj = json.loads(line)
        key = obj.get("key")
        if "response" in obj:
            rows.append((key, obj["response"], None))
        elif "error" in obj:
            rows.append((key, None, obj["error"]))
    return rows


def process_results(
    result_rows: list[tuple[str | None, Any, Any | None]],
    records_by_key: dict[str, SentenceRecord],
    *,
    prompt_family: str,
    verbose: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    predictions: list[dict[str, Any]] = []
    label_counts: Counter[str] = Counter()
    parse_ok_count = 0
    fail_count = 0
    prompt_tokens = 0
    output_tokens = 0
    thought_tokens = 0

    for key, response, error in result_rows:
        rec = records_by_key.get(key or "", None)
        entry: dict[str, Any] = {
            "key": key,
            "source_file": rec.source_file if rec else None,
            "sentence_index": rec.sentence_index if rec else None,
            "sentence_text_full": rec.sentence_text_full if rec else None,
            "parse_ok": False,
            "prediction_label": None,
            "prediction_bool": None,
            "raw_model_response": None,
            "parse_error": None,
            "usage": None,
            "error": error,
        }

        if error:
            fail_count += 1
            entry["parse_error"] = str(error)
            predictions.append(entry)
            if verbose:
                log(f"FAIL key={key} error={error}")
            continue

        if isinstance(response, dict):
            text = response_text_from_dict(response)
            usage_norm = usage_from_dict(response)
        else:
            text = response_text(response)
            usage_norm = extract_usage(response)

        entry["raw_model_response"] = text
        entry["usage"] = usage_norm
        prompt_tokens += usage_norm["prompt_tokens"]
        output_tokens += usage_norm["output_tokens"]
        thought_tokens += usage_norm["thought_tokens"]

        parsed = parse_family_output(prompt_family, text)
        entry["parse_ok"] = parsed.is_valid
        if parsed.is_valid and parsed.label:
            entry["prediction_label"] = parsed.label
            entry["prediction_bool"] = parsed.label == "BORDER"
            label_counts[parsed.label] += 1
            parse_ok_count += 1
        else:
            entry["parse_error"] = parsed.error
            fail_count += 1

        predictions.append(entry)
        if verbose:
            reason_preview = ""
            if isinstance(parsed.payload, dict):
                reason_preview = str(parsed.payload.get("reason", ""))[:80]
            log(
                f"key={key} parse_ok={entry['parse_ok']} label={entry['prediction_label']} "
                f"tokens_in={usage_norm['prompt_tokens']} tokens_out={usage_norm['output_tokens']} "
                f"thoughts={usage_norm['thought_tokens']} reason={reason_preview!r}"
            )

    n = len(predictions) or 1
    total_output_billed = output_tokens + thought_tokens
    est_cost = (
        (prompt_tokens / 1_000_000) * BATCH_INPUT_USD_PER_M
        + (total_output_billed / 1_000_000) * BATCH_OUTPUT_USD_PER_M
    )
    summary = {
        "request_count": len(predictions),
        "parse_ok_count": parse_ok_count,
        "parse_ok_rate": parse_ok_count / n,
        "fail_count": fail_count,
        "label_counts": dict(label_counts),
        "avg_input_tokens": prompt_tokens / n,
        "avg_output_tokens": output_tokens / n,
        "avg_thought_tokens": thought_tokens / n,
        "total_input_tokens": prompt_tokens,
        "total_output_tokens": output_tokens,
        "total_thought_tokens": thought_tokens,
        "estimated_batch_cost_usd": round(est_cost, 4),
    }
    return predictions, summary


def main() -> int:
    args = parse_args()
    _require_api_key()
    client = genai.Client()

    out_dir = output_dir_for(args)
    out_dir.mkdir(parents=True, exist_ok=True)

    job_mode = args.mode
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

        if args.mode == "file":
            file_lines = [
                build_file_request_line(
                    req["contents"][0]["parts"][0]["text"],
                    key=req["metadata"]["key"],
                    generation_config=generation_config,
                )
                for req in inline_requests
            ]
            batch_jsonl = out_dir / "batch_requests.jsonl"
            write_jsonl(batch_jsonl, file_lines)
            log(f"Wrote batch JSONL: {batch_jsonl} ({batch_jsonl.stat().st_size} bytes)")

            uploaded = client.files.upload(
                file=str(batch_jsonl),
                config=types.UploadFileConfig(
                    display_name=batch_jsonl.name,
                    mime_type="jsonl",
                ),
            )
            log(f"Uploaded input file: {uploaded.name}")
            src = uploaded.name
        else:
            src = inline_requests
            batch_jsonl = out_dir / "batch_requests.jsonl"
            write_jsonl(
                batch_jsonl,
                [
                    build_file_request_line(
                        req["contents"][0]["parts"][0]["text"],
                        key=req["metadata"]["key"],
                        generation_config=generation_config,
                    )
                    for req in inline_requests
                ],
            )
            log(f"Wrote request archive: {batch_jsonl}")

        display_name = out_dir.name
        log(f"Submitting batch: model={args.model} mode={args.mode} n={len(records)}")
        batch_job = client.batches.create(
            model=args.model,
            src=src,
            config={"display_name": display_name},
        )
        job_name = batch_job.name or ""
        log(f"Created batch job: {job_name}")

        job_meta = {
            "job_name": job_name,
            "model": args.model,
            "mode": args.mode,
            "manifest": str(args.manifest),
            "request_count": len(records),
            "records": [
                {
                    "key": r.key,
                    "source_file": r.source_file,
                    "sentence_index": r.sentence_index,
                    "sentence_text_full": r.sentence_text_full,
                }
                for r in records
            ],
            "submitted_at": datetime.now(timezone.utc).isoformat(),
        }
        (out_dir / "job_meta.json").write_text(json.dumps(job_meta, indent=2), encoding="utf-8")

        batch_job = poll_batch_job(client, job_name, args.poll_interval)

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
