"""Shared helpers for dProse Gemini Batch API runners."""

from __future__ import annotations

import json
import time
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from google import genai
from google.genai import types

from src.core.prompt_runtime import parse_family_output, render_prompt_for_family

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
PILOT_COST_PER_SENTENCE_USD = 4.40 / 989


@dataclass
class SentenceRecord:
    key: str
    source_file: str
    sentence_index: int
    sentence_text_full: str


@dataclass
class BatchRunConfig:
    model: str = "gemini-2.5-pro"
    mode: str = "file"
    prompt_family: str = "B"
    context_sentences: int = 12
    temperature: float = 0.0
    max_output_tokens: int = 2048
    thinking_budget: int = -1
    poll_interval: int = 30


def log(msg: str) -> None:
    print(msg, flush=True)


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    with manifest_path.open(encoding="utf-8") as handle:
        return json.load(handle)


def manifest_for_slugs(full_manifest: dict[str, Any], slugs: set[str]) -> dict[str, Any]:
    files = [entry for entry in full_manifest.get("files", []) if entry.get("slug") in slugs]
    if not files:
        raise ValueError(f"No manifest entries for slugs: {sorted(slugs)}")
    return {
        "dataset": full_manifest.get("dataset", "dprose"),
        "source": full_manifest.get("source", "local/dprose_sentence_level"),
        "files": files,
        "total_sentences": sum(int(f.get("sentence_count", 0)) for f in files),
    }


def manifest_for_book(full_manifest: dict[str, Any], slug: str) -> dict[str, Any]:
    return manifest_for_slugs(full_manifest, {slug})


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


def prepare_requests(
    manifest: dict[str, Any],
    data_root: Path,
    *,
    prompt_family: str,
    template_text: str,
    context_sentences: int,
    generation_config: dict[str, Any],
    max_sentences: int | None = None,
    keys_filter: set[str] | None = None,
) -> tuple[list[SentenceRecord], list[dict[str, Any]]]:
    by_file = load_sentences_by_file(manifest, data_root)
    records: list[SentenceRecord] = []
    requests: list[dict[str, Any]] = []

    for rec in iter_sentences(manifest, data_root):
        if keys_filter is not None and rec.key not in keys_filter:
            continue
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
    verbose: bool = False,
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


def estimate_cost_usd(sentence_count: int) -> float:
    return round(sentence_count * PILOT_COST_PER_SENTENCE_USD, 4)


def submit_batch_job(
    client: genai.Client,
    *,
    out_dir: Path,
    records: list[SentenceRecord],
    inline_requests: list[dict[str, Any]],
    generation_config: dict[str, Any],
    config: BatchRunConfig,
    manifest_path: Path | None = None,
) -> tuple[types.BatchJob, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)

    if config.mode == "file":
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
    log(f"Submitting batch: model={config.model} mode={config.mode} n={len(records)}")
    batch_job = client.batches.create(
        model=config.model,
        src=src,
        config={"display_name": display_name},
    )
    job_name = batch_job.name or ""
    log(f"Created batch job: {job_name}")

    job_meta = {
        "job_name": job_name,
        "model": config.model,
        "mode": config.mode,
        "manifest": str(manifest_path) if manifest_path else None,
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
    job_meta_path = out_dir / "job_meta.json"
    job_meta_path.write_text(json.dumps(job_meta, indent=2), encoding="utf-8")
    return batch_job, job_meta_path


def run_batch_to_completion(
    client: genai.Client,
    *,
    out_dir: Path,
    records_by_key: dict[str, SentenceRecord],
    config: BatchRunConfig,
    prompt_family: str,
    job_meta_path: Path | None = None,
    verbose: bool = False,
) -> tuple[list[dict[str, Any]], dict[str, Any], types.BatchJob]:
    if job_meta_path and job_meta_path.is_file():
        meta = json.loads(job_meta_path.read_text(encoding="utf-8"))
        job_name = meta["job_name"]
        job_mode = meta.get("mode", config.mode)
        log(f"Resuming job from {job_meta_path} (mode={job_mode})")
        batch_job = poll_batch_job(client, job_name, config.poll_interval)
    else:
        raise ValueError("job_meta_path required for resume path in run_batch_to_completion")

    if job_mode == "file":
        result_rows = iter_file_results(client, batch_job)
    else:
        result_rows = iter_inline_results(batch_job)

    if not result_rows:
        raise RuntimeError("No batch results found")

    predictions, summary = process_results(
        result_rows,
        records_by_key,
        prompt_family=prompt_family,
        verbose=verbose,
    )
    summary.update(
        {
            "model": meta["model"],
            "job_name": batch_job.name,
            "job_state": batch_job.state.name if batch_job.state else None,
            "mode": job_mode,
            "manifest": meta.get("manifest"),
            "prompt_family": prompt_family,
            "context_sentences": config.context_sentences,
            "thinking_budget": config.thinking_budget,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    return predictions, summary, batch_job
