#!/usr/bin/env python3
"""Prompt-family sweep on the close-reading gold texts via the Gemini Batch API.

Reuses the dProse batch engine (``src/runners/dprose_batch_core.py``) to run one
Gemini Batch job per prompt family on the two Excel gold documents
(Gaensemagd + Kleist), then scores each family's predictions against the gold
scene borders at tolerances 0/1/3.

Wave 1 (fully batch-compatible, run + reported): B, K, L, M, N, O, P, Q.
Prepared-but-not-swept (schema wiring ready): C, D, E, F, G, J.
Pipeline stubs (chunk / label-only, dry-run only): A, H, I.

Same processed inputs and gold as EXCEL_PROMPTING_2026-05-30_REPORT.md, but via
the official Gemini Batch API instead of OpenRouter sync.

Examples
--------
Dry-run (render + write request JSONL, no API call) for every family:
    .venv/bin/python -u src/runners/run_excel_batch_families.py \
        --families A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q \
        --dry_run --date 2026-07-22-excel-gemini-batch-dryrun

Wave 1 live run:
    set -a && source .env && set +a
    .venv/bin/python -u src/runners/run_excel_batch_families.py \
        --families B,K,L,M,N,O,P,Q \
        --date 2026-07-22-excel-gemini-batch-families
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from google import genai
from google.genai import types

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.core.prompt_runtime import (  # noqa: E402
    get_template_text,
    load_prompt_registry,
    parse_family_output,
)
from src.eval.excel_gold_scoring import score_run  # noqa: E402
from src.runners.dprose_batch_core import (  # noqa: E402
    BatchRunConfig,
    build_generation_config,
    iter_file_results,
    iter_inline_results,
    load_manifest,
    load_response_schema,
    log,
    map_chunk_result_to_label,
    poll_batch_job,
    prepare_chunk_requests,
    prepare_requests,
    process_results,
    response_text,
    response_text_from_dict,
    submit_batch_job,
    write_jsonl,
)

# Prompt family -> response schema file (relative to prompts dir).
# None means plain-text output (no JSON schema enforced).
SENTENCE_SCHEMA: dict[str, str | None] = {
    "A": "json_schema_label_only.json",
    "B": "json_schema_label_reason.json",
    "C": "json_schema_rubric_label.json",
    "D": "json_schema_label_reason.json",
    "E": "json_schema_label_reason.json",
    "F": "json_schema_rubric_label.json",
    "G": "json_schema_analysis_label.json",
    "J": "json_schema_changes_label.json",
    "K": "json_schema_label_reason.json",
    "L": "json_schema_label_reason.json",
    "M": "json_schema_label_reason.json",
    "N": "json_schema_label_reason.json",
    "O": "json_schema_label_reason.json",
    "P": "json_schema_label_reason.json",
    "Q": "json_schema_label_reason.json",
}
CHUNK_SCHEMA: dict[str, str | None] = {
    "H": None,  # text/plain: a sentence id or NONE
    "I": "json_schema_score_array.json",
}
CHUNK_FAMILIES = frozenset(CHUNK_SCHEMA)
WAVE1_FAMILIES = ["B", "K", "L", "M", "N", "O", "P", "Q"]


def _require_api_key() -> str:
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        log("ERROR: Set GEMINI_API_KEY (e.g. set -a && source .env && set +a)")
        sys.exit(1)
    return api_key


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--families", default=",".join(WAVE1_FAMILIES),
                   help="Comma-separated family ids (default: Wave 1 = B,K,L,M,N,O,P,Q).")
    p.add_argument("--manifest", type=Path, default=Path("data/manifests/excel_batch.json"))
    p.add_argument("--data_root", type=Path, default=Path("data"))
    p.add_argument("--prompts_dir", type=Path, default=Path("src/prompts"))
    p.add_argument("--model", default="gemini-2.5-pro")
    p.add_argument("--mode", choices=["inline", "file"], default="file")
    p.add_argument("--context_sentences", type=int, default=12)
    p.add_argument("--chunk_window", type=int, default=2, help="For H/I chunk families.")
    p.add_argument("--score_threshold", type=float, default=50.0, help="For family I.")
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--max_output_tokens", type=int, default=2048)
    p.add_argument("--thinking_budget", type=int, default=-1)
    p.add_argument("--poll_interval", type=int, default=30)
    p.add_argument("--max_sentences", type=int, default=None)
    p.add_argument("--verbose", action="store_true")
    p.add_argument("--dry_run", action="store_true",
                   help="Render + write request JSONL and a sample prompt; do not call the API.")
    p.add_argument("--resume", action="store_true",
                   help="Resume any family whose family_<ID>/job_meta.json already exists.")
    p.add_argument("--score_only", action="store_true",
                   help="Re-score existing predictions.jsonl without submitting jobs.")
    p.add_argument("--date", default=None, help="Run tag / output folder name.")
    p.add_argument("--output_root", type=Path, default=Path("outputs/runs/prompting"))
    return p.parse_args()


def schema_file_for(family: str, prompts_dir: Path) -> Path | None:
    family = family.upper()
    if family in CHUNK_FAMILIES:
        rel = CHUNK_SCHEMA[family]
    elif family in SENTENCE_SCHEMA:
        rel = SENTENCE_SCHEMA[family]
    else:
        raise ValueError(f"Unknown family: {family}")
    return (prompts_dir / rel) if rel else None


def write_predictions(pred_path: Path, predictions: list[dict[str, Any]]) -> None:
    with pred_path.open("w", encoding="utf-8") as handle:
        for row in predictions:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def process_chunk_results(
    result_rows: list[tuple[str | None, Any, Any | None]],
    chunk_meta_by_key: dict[str, dict[str, Any]],
    *,
    prompt_family: str,
    score_threshold: float,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Turn H/I chunk outputs into sentence-level predictions.jsonl rows."""
    predictions: list[dict[str, Any]] = []
    parse_ok = 0
    fail = 0
    for key, response, error in result_rows:
        meta = chunk_meta_by_key.get(key or "", {})
        entry: dict[str, Any] = {
            "key": key,
            "source_file": meta.get("source_file"),
            "sentence_index": meta.get("sentence_index"),
            "parse_ok": False,
            "prediction_label": None,
            "prediction_bool": None,
            "raw_model_response": None,
            "parse_error": None,
            "error": error,
        }
        if error:
            fail += 1
            entry["parse_error"] = str(error)
            predictions.append(entry)
            continue
        text = response_text_from_dict(response) if isinstance(response, dict) else response_text(response)
        entry["raw_model_response"] = text
        parsed = parse_family_output(prompt_family, text)
        label = map_chunk_result_to_label(
            prompt_family,
            parsed.payload,
            target_local_id=int(meta.get("target_local_id", -1)),
            score_threshold=score_threshold,
        )
        if label is not None:
            entry["parse_ok"] = True
            entry["prediction_label"] = label
            entry["prediction_bool"] = label == "BORDER"
            parse_ok += 1
        else:
            entry["parse_error"] = parsed.error or "chunk_map_failed"
            fail += 1
        predictions.append(entry)
    n = len(predictions) or 1
    summary = {
        "request_count": len(predictions),
        "parse_ok_count": parse_ok,
        "parse_ok_rate": parse_ok / n,
        "fail_count": fail,
    }
    return predictions, summary


def run_family(
    client: genai.Client | None,
    family: str,
    args: argparse.Namespace,
    manifest: dict[str, Any],
    registry: dict[str, Any],
) -> dict[str, Any]:
    family = family.upper()
    out_dir = args.output_root / args.date / f"family_{family}"
    out_dir.mkdir(parents=True, exist_ok=True)
    is_chunk = family in CHUNK_FAMILIES
    index_base = int(manifest.get("index_base", 0))

    template_text = get_template_text(args.prompts_dir, family, registry)
    schema_path = schema_file_for(family, args.prompts_dir)
    response_schema = load_response_schema(schema_path) if schema_path else None
    generation_config = build_generation_config(
        temperature=args.temperature,
        max_output_tokens=args.max_output_tokens,
        thinking_budget=args.thinking_budget,
        response_schema=response_schema,
    )

    run_config = BatchRunConfig(
        model=args.model,
        mode=args.mode,
        prompt_family=family,
        context_sentences=args.context_sentences,
        temperature=args.temperature,
        max_output_tokens=args.max_output_tokens,
        thinking_budget=args.thinking_budget,
        poll_interval=args.poll_interval,
    )

    pred_path = out_dir / "predictions.jsonl"
    summary_path = out_dir / "summary.json"
    score_path = out_dir / "score.json"
    job_meta_path = out_dir / "job_meta.json"

    # --- score-only: just re-score existing predictions ---
    if args.score_only:
        if not pred_path.is_file():
            log(f"[{family}] score_only: no predictions.jsonl, skipping")
            return {"family": family, "status": "missing_predictions"}
        score = score_run(pred_path, manifest, args.data_root)
        score_path.write_text(json.dumps(score, indent=2), encoding="utf-8")
        log(f"[{family}] re-scored -> {score_path}")
        return {"family": family, "status": "scored", "score": score}

    # --- build requests ---
    if is_chunk:
        chunk_meta, inline_requests = prepare_chunk_requests(
            manifest, args.data_root,
            prompt_family=family, template_text=template_text,
            chunk_window=args.chunk_window, generation_config=generation_config,
            index_base=index_base,
        )
        (out_dir / "chunk_meta.json").write_text(
            json.dumps(chunk_meta, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        records = None
        n_requests = len(inline_requests)
    else:
        records, inline_requests = prepare_requests(
            manifest, args.data_root,
            prompt_family=family, template_text=template_text,
            context_sentences=args.context_sentences,
            generation_config=generation_config,
            max_sentences=args.max_sentences, index_base=index_base,
        )
        n_requests = len(inline_requests)

    log(f"[{family}] prepared {n_requests} requests "
        f"(schema={schema_path.name if schema_path else 'text/plain'}, chunk={is_chunk})")

    # --- dry-run: write requests + a rendered sample, no API call ---
    if args.dry_run:
        req_lines = [
            {"key": r["metadata"]["key"], "prompt": r["contents"][0]["parts"][0]["text"]}
            for r in inline_requests
        ]
        write_jsonl(out_dir / "dry_run_requests.jsonl", req_lines)
        if req_lines:
            (out_dir / "dry_run_sample.txt").write_text(req_lines[0]["prompt"], encoding="utf-8")
        log(f"[{family}] dry-run wrote {len(req_lines)} rendered requests")
        return {"family": family, "status": "dry_run", "n_requests": n_requests}

    if client is None:
        raise RuntimeError("client required for live run")

    # --- submit / resume ---
    if args.resume and job_meta_path.is_file():
        meta = json.loads(job_meta_path.read_text(encoding="utf-8"))
        batch_job = poll_batch_job(client, meta["job_name"], args.poll_interval)
        job_mode = meta.get("mode", args.mode)
    elif is_chunk:
        batch_job, job_mode = _submit_chunk_job(client, out_dir, inline_requests, run_config, args.manifest)
    else:
        batch_job, _ = submit_batch_job(
            client, out_dir=out_dir, records=records, inline_requests=inline_requests,
            generation_config=generation_config, config=run_config, manifest_path=args.manifest,
        )
        batch_job = poll_batch_job(client, batch_job.name or "", args.poll_interval)
        job_mode = args.mode

    # --- extract ---
    result_rows = iter_file_results(client, batch_job) if job_mode == "file" else iter_inline_results(batch_job)
    if not result_rows:
        log(f"[{family}] ERROR: no batch results")
        return {"family": family, "status": "no_results"}

    # --- process ---
    if is_chunk:
        chunk_meta = json.loads((out_dir / "chunk_meta.json").read_text(encoding="utf-8"))
        chunk_meta_by_key = {m["key"]: m for m in chunk_meta}
        predictions, summary = process_chunk_results(
            result_rows, chunk_meta_by_key, prompt_family=family, score_threshold=args.score_threshold,
        )
    else:
        records_by_key = {r.key: r for r in records}
        predictions, summary = process_results(
            result_rows, records_by_key, prompt_family=family, verbose=args.verbose,
        )
    summary.update({
        "family": family, "model": args.model, "mode": job_mode,
        "job_name": batch_job.name, "job_state": batch_job.state.name if batch_job.state else None,
        "context_sentences": args.context_sentences, "thinking_budget": args.thinking_budget,
        "schema_file": schema_path.name if schema_path else None,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    })

    write_predictions(pred_path, predictions)
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # --- score vs gold ---
    score = score_run(pred_path, manifest, args.data_root)
    score_path.write_text(json.dumps(score, indent=2), encoding="utf-8")
    log(f"[{family}] parse_ok_rate={summary['parse_ok_rate']:.3f} "
        f"macroF1@0={score['macro_avg_tol_0']['f1']} macroF1@3={score['macro_avg_tol_3']['f1']}")
    return {"family": family, "status": "done", "summary": summary, "score": score}


def _submit_chunk_job(client, out_dir, inline_requests, config, manifest_path):
    """Minimal submit for chunk families (records are chunk_meta, handled separately)."""
    from src.runners.dprose_batch_core import build_file_request_line
    file_lines = [
        build_file_request_line(
            r["contents"][0]["parts"][0]["text"], key=r["metadata"]["key"],
            generation_config=r["config"],
        )
        for r in inline_requests
    ]
    batch_jsonl = out_dir / "batch_requests.jsonl"
    write_jsonl(batch_jsonl, file_lines)
    uploaded = client.files.upload(
        file=str(batch_jsonl),
        config=types.UploadFileConfig(display_name=batch_jsonl.name, mime_type="jsonl"),
    )
    batch_job = client.batches.create(
        model=config.model, src=uploaded.name, config={"display_name": out_dir.name},
    )
    (out_dir / "job_meta.json").write_text(json.dumps({
        "job_name": batch_job.name, "model": config.model, "mode": "file",
        "manifest": str(manifest_path), "request_count": len(inline_requests),
        "submitted_at": datetime.now(timezone.utc).isoformat(),
    }, indent=2), encoding="utf-8")
    batch_job = poll_batch_job(client, batch_job.name or "", config.poll_interval)
    return batch_job, "file"


def write_comparison(run_dir: Path, results: list[dict[str, Any]]) -> Path:
    """Write comparison.csv across families that produced scores."""
    rows = []
    for res in results:
        score = res.get("score")
        summary = res.get("summary", {})
        if not score:
            continue
        rows.append({
            "family": res["family"],
            "macro_f1_tol0": score["macro_avg_tol_0"]["f1"],
            "macro_p_tol0": score["macro_avg_tol_0"]["precision"],
            "macro_r_tol0": score["macro_avg_tol_0"]["recall"],
            "macro_f1_tol1": score["macro_avg_tol_1"]["f1"],
            "macro_f1_tol3": score["macro_avg_tol_3"]["f1"],
            "over_prediction_ratio": score.get("overall_over_prediction_ratio"),
            "total_pred_borders": score.get("total_pred_borders"),
            "total_gold_borders": score.get("total_gold_borders"),
            "parse_ok_rate": round(summary.get("parse_ok_rate", 0.0), 4) if summary else None,
            "estimated_batch_cost_usd": summary.get("estimated_batch_cost_usd") if summary else None,
        })
    rows.sort(key=lambda r: (r["macro_f1_tol3"] or 0, r["macro_f1_tol0"] or 0), reverse=True)
    out = run_dir / "comparison.csv"
    if rows:
        with out.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    (run_dir / "comparison.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    return out


def main() -> int:
    args = parse_args()
    if not args.date:
        args.date = datetime.now(timezone.utc).strftime("%Y-%m-%d-excel-gemini-batch-families")
    families = [f.strip().upper() for f in args.families.split(",") if f.strip()]

    client = None
    if not args.dry_run and not args.score_only:
        _require_api_key()
        client = genai.Client()

    manifest = load_manifest(args.manifest)
    registry = load_prompt_registry(args.prompts_dir)
    run_dir = args.output_root / args.date
    run_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    for family in families:
        log(f"===== family {family} =====")
        try:
            results.append(run_family(client, family, args, manifest, registry))
        except Exception as exc:  # noqa: BLE001 - keep sweeping other families
            log(f"[{family}] ERROR: {exc}")
            results.append({"family": family, "status": "error", "error": str(exc)})

    if not args.dry_run:
        comparison = write_comparison(run_dir, results)
        log(f"Wrote comparison: {comparison}")

    (run_dir / "sweep_results.json").write_text(
        json.dumps(
            [{k: v for k, v in r.items() if k != "summary"} for r in results],
            indent=2, ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    log("--- sweep done ---")
    for r in results:
        log(f"  {r['family']}: {r.get('status')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
