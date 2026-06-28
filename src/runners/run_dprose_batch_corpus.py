#!/usr/bin/env python3
"""Run dProse full-corpus prompting one book at a time via Gemini Batch API."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from google import genai

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.core.prompt_runtime import get_template_text, load_prompt_registry  # noqa: E402
from src.core.workflow_runtime import write_json_atomic  # noqa: E402
from src.runners.dprose_batch_core import (  # noqa: E402
    BatchRunConfig,
    SentenceRecord,
    build_generation_config,
    estimate_cost_usd,
    iter_file_results,
    iter_inline_results,
    load_manifest,
    load_response_schema,
    log,
    manifest_for_book,
    poll_batch_job,
    prepare_requests,
    process_results,
    submit_batch_job,
)

DEFAULT_OUTPUT_ROOT = Path("outputs/runs/dprose_batch/dprose-full-corpus")
DEFAULT_FULL_MANIFEST = Path("data/manifests/dprose_full.json")
PILOT_RUN_DIR = Path("outputs/runs/dprose_batch/2026-06-20-dprose-batch-pilot-2048")
PILOT_SLUGS = ("dprose_100", "dprose_806", "dprose_2158")
PARSE_OK_GATE = 0.95
REVIEW_SCRIPT = Path("scripts/evaluation/review_dprose_book.py")


def config_hash(args: argparse.Namespace) -> str:
    payload = {
        "model": args.model,
        "prompt_family": args.prompt_family,
        "schema_file": str(args.schema_file),
        "context_sentences": args.context_sentences,
        "temperature": args.temperature,
        "max_output_tokens": args.max_output_tokens,
        "thinking_budget": args.thinking_budget,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]


def load_wave_manifest(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_progress(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def book_dir(output_root: Path, slug: str) -> Path:
    return output_root / "books" / slug


def predictions_path(output_root: Path, slug: str) -> Path:
    return book_dir(output_root, slug) / "predictions.jsonl"


def job_meta_path(output_root: Path, slug: str) -> Path:
    return book_dir(output_root, slug) / "job_meta.json"


def spent_usd_for_cap(progress: dict[str, Any]) -> float:
    """API spend counted against --max_cost_usd (excludes seeded pilot books)."""
    return round(
        sum(
            float(b.get("estimated_cost_usd", 0))
            for b in progress.get("books", {}).values()
            if b.get("status") == "complete" and not b.get("seeded_from_pilot")
        ),
        4,
    )


def recompute_totals(
    progress: dict[str, Any],
    *,
    full_manifest: dict[str, Any],
) -> None:
    books = progress.get("books", {})
    complete = [b for b in books.values() if b.get("status") == "complete"]
    progress["totals"] = {
        "books_complete": len(complete),
        "books_total": len(full_manifest.get("files", [])),
        "sentences_complete": sum(int(b.get("sentence_count", 0)) for b in complete),
        "sentences_total": int(full_manifest.get("total_sentences", 0)),
        "cost_usd": round(sum(float(b.get("estimated_cost_usd", 0)) for b in complete), 4),
    }


def update_progress_book(
    progress: dict[str, Any],
    slug: str,
    entry: dict[str, Any],
    *,
    full_manifest: dict[str, Any],
) -> None:
    progress.setdefault("books", {})[slug] = entry
    recompute_totals(progress, full_manifest=full_manifest)
    progress["updated_at"] = datetime.now(timezone.utc).isoformat()


def seed_pilot_books(output_root: Path, full_manifest: dict[str, Any]) -> dict[str, Any]:
    progress_path = output_root / "corpus_progress.json"
    progress = load_progress(progress_path)
    progress.setdefault("books", {})

    manifest_by_slug = {entry["slug"]: entry for entry in full_manifest.get("files", [])}

    for slug in PILOT_SLUGS:
        if progress["books"].get(slug, {}).get("status") == "complete":
            continue
        src_pred = PILOT_RUN_DIR / "predictions.jsonl"
        if not src_pred.is_file():
            log(f"WARN: pilot predictions missing at {src_pred}; skip seed for {slug}")
            continue

        rows = []
        with src_pred.open(encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    row = json.loads(line)
                    if row.get("key", "").startswith(f"{slug}:"):
                        rows.append(row)
        if not rows:
            log(f"WARN: no pilot rows for {slug}")
            continue

        dest = book_dir(output_root, slug)
        dest.mkdir(parents=True, exist_ok=True)
        pred_path = dest / "predictions.jsonl"
        with pred_path.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")

        manifest_entry = manifest_by_slug.get(slug, {})
        sentence_count = int(manifest_entry.get("sentence_count", len(rows)))
        parse_ok = sum(1 for r in rows if r.get("parse_ok"))
        border_count = sum(
            1 for r in rows if r.get("parse_ok") and r.get("prediction_label") == "BORDER"
        )
        book_cost = round(
            sum(
                (int((r.get("usage") or {}).get("prompt_tokens", 0)) / 1_000_000) * 0.625
                + (
                    int((r.get("usage") or {}).get("output_tokens", 0))
                    + int((r.get("usage") or {}).get("thought_tokens", 0))
                )
                / 1_000_000
                * 5.0
                for r in rows
            ),
            4,
        )
        if book_cost == 0:
            book_cost = estimate_cost_usd(len(rows))

        summary = {
            "slug": slug,
            "source_file": manifest_entry.get("source_file", f"{slug}.csv"),
            "request_count": len(rows),
            "parse_ok_count": parse_ok,
            "parse_ok_rate": parse_ok / len(rows) if rows else 0,
            "estimated_batch_cost_usd": book_cost,
            "seeded_from_pilot": True,
            "pilot_run_dir": str(PILOT_RUN_DIR),
        }
        (dest / "book_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

        progress["books"][slug] = {
            "status": "complete",
            "source_file": summary["source_file"],
            "sentence_count": sentence_count,
            "parse_ok_rate": summary["parse_ok_rate"],
            "border_rate": border_count / len(rows) if rows else 0,
            "estimated_cost_usd": book_cost,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "seeded_from_pilot": True,
        }
        log(f"Seeded pilot book: {slug} ({len(rows)} predictions)")

    recompute_totals(progress, full_manifest=full_manifest)
    progress["run_tag"] = output_root.name
    return progress


def run_book_review(
    *,
    predictions: Path,
    book_out: Path,
    source_file: str,
) -> int:
    cmd = [
        sys.executable,
        str(_ROOT / REVIEW_SCRIPT),
        "--predictions",
        str(predictions),
        "--source_file",
        source_file,
        "--write_txt",
        str(book_out / "book_review.txt"),
        "--write_json",
        str(book_out / "book_review.json"),
    ]
    return subprocess.run(cmd, cwd=_ROOT, check=False).returncode


def load_failed_keys(predictions: Path) -> set[str]:
    if not predictions.is_file():
        return set()
    keys: set[str] = set()
    with predictions.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            if not row.get("parse_ok"):
                key = row.get("key")
                if key:
                    keys.add(str(key))
    return keys


def merge_predictions(existing: Path, new_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key: dict[str, dict[str, Any]] = {}
    if existing.is_file():
        with existing.open(encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    row = json.loads(line)
                    key = row.get("key")
                    if key:
                        by_key[str(key)] = row
    for row in new_rows:
        key = row.get("key")
        if key:
            by_key[str(key)] = row
    return [by_key[k] for k in sorted(by_key.keys(), key=lambda x: (x.split(":")[0], int(x.split(":")[1])))]


def run_one_book(
    *,
    client: genai.Client,
    slug: str,
    source_file: str,
    sentence_count: int,
    full_manifest: dict[str, Any],
    args: argparse.Namespace,
    run_config: BatchRunConfig,
    template_text: str,
    generation_config: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    out = book_dir(args.output_root, slug)
    out.mkdir(parents=True, exist_ok=True)
    book_manifest = manifest_for_book(full_manifest, slug)
    manifest_slice_path = out / "manifest_slice.json"
    manifest_slice_path.write_text(json.dumps(book_manifest, indent=2) + "\n", encoding="utf-8")

    meta_path = job_meta_path(args.output_root, slug)
    pred_path = predictions_path(args.output_root, slug)

    keys_filter = None
    if args.retry_failed and pred_path.is_file():
        keys_filter = load_failed_keys(pred_path)
        if not keys_filter:
            log(f"No failed keys to retry for {slug}; loading existing predictions")
            rows = []
            with pred_path.open(encoding="utf-8") as handle:
                for line in handle:
                    if line.strip():
                        rows.append(json.loads(line))
            summary_path = out / "book_summary.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.is_file() else {}
            return rows, summary

    if meta_path.is_file() and not pred_path.is_file():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        records = [SentenceRecord(**r) for r in meta["records"]]
        records_by_key = {r.key: r for r in records}
        log(f"Resuming in-flight job for {slug}")
        batch_job = poll_batch_job(client, meta["job_name"], args.poll_interval)
        job_mode = meta.get("mode", args.mode)
        if job_mode == "file":
            result_rows = iter_file_results(client, batch_job)
        else:
            result_rows = iter_inline_results(batch_job)
        if not result_rows:
            raise RuntimeError(f"No batch results for resumed job: {slug}")
        new_predictions, summary = process_results(
            result_rows,
            records_by_key,
            prompt_family=args.prompt_family,
            verbose=args.verbose,
        )
    else:
        records, inline_requests = prepare_requests(
            book_manifest,
            args.data_root,
            prompt_family=args.prompt_family,
            template_text=template_text,
            context_sentences=args.context_sentences,
            generation_config=generation_config,
            keys_filter=keys_filter,
        )
        if not records:
            raise RuntimeError(f"No requests prepared for {slug}")

        batch_job, meta_path = submit_batch_job(
            client,
            out_dir=out,
            records=records,
            inline_requests=inline_requests,
            generation_config=generation_config,
            config=run_config,
            manifest_path=manifest_slice_path,
        )
        batch_job = poll_batch_job(client, batch_job.name or "", args.poll_interval)
        records_by_key = {r.key: r for r in records}
        job_mode = args.mode
        if job_mode == "file":
            result_rows = iter_file_results(client, batch_job)
        else:
            result_rows = iter_inline_results(batch_job)
        if not result_rows:
            raise RuntimeError(f"No batch results for {slug}")
        new_predictions, summary = process_results(
            result_rows,
            records_by_key,
            prompt_family=args.prompt_family,
            verbose=args.verbose,
        )

    if args.retry_failed and pred_path.is_file():
        predictions = merge_predictions(pred_path, new_predictions)
    else:
        predictions = new_predictions

    summary.update(
        {
            "slug": slug,
            "source_file": source_file,
            "model": args.model,
            "job_name": summary.get("job_name") or json.loads(meta_path.read_text())["job_name"],
            "manifest": str(manifest_slice_path),
            "prompt_family": args.prompt_family,
            "context_sentences": args.context_sentences,
            "thinking_budget": args.thinking_budget,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
    )

    with pred_path.open("w", encoding="utf-8") as handle:
        for row in predictions:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    (out / "book_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return predictions, summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wave_manifest", type=Path, required=True)
    parser.add_argument("--full_manifest", type=Path, default=DEFAULT_FULL_MANIFEST)
    parser.add_argument("--data_root", type=Path, default=Path("data"))
    parser.add_argument("--output_root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--mode", choices=["inline", "file"], default="file")
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
    parser.add_argument("--poll_interval", type=int, default=30)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--max_cost_usd", type=float, default=None)
    parser.add_argument("--max_books", type=int, default=None)
    parser.add_argument("--dry_run", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--seed_pilot", action="store_true")
    parser.add_argument("--retry_failed", action="store_true")
    parser.add_argument(
        "--books",
        default=None,
        help="Comma-separated slugs override (e.g. dprose_51,dprose_52).",
    )
    return parser.parse_args()


def _require_api_key(dry_run: bool) -> None:
    if dry_run:
        return
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        log("ERROR: Set GEMINI_API_KEY (e.g. set -a && source .env && set +a)")
        sys.exit(1)


def main() -> int:
    args = parse_args()
    _require_api_key(args.dry_run)

    args.output_root.mkdir(parents=True, exist_ok=True)
    full_manifest = load_manifest(args.full_manifest)
    wave = load_wave_manifest(args.wave_manifest)
    progress_path = args.output_root / "corpus_progress.json"

    progress = load_progress(progress_path)
    if args.seed_pilot or not progress.get("books"):
        progress = seed_pilot_books(args.output_root, full_manifest)
        progress["config_hash"] = config_hash(args)
        progress["run_tag"] = args.output_root.name
        write_json_atomic(progress_path, progress)

    if args.books:
        slugs = [s.strip() for s in args.books.split(",") if s.strip()]
        wave_books = [{"slug": s} for s in slugs]
    else:
        wave_books = wave.get("books", [])

    spent_usd = spent_usd_for_cap(progress)
    log(f"Wave: {wave.get('wave_id', args.wave_manifest.stem)}")
    log(f"Books in wave: {len(wave_books)}  Session API spend (excl. pilot seed): ${spent_usd:.2f}")

    planned: list[dict[str, Any]] = []
    planned_cost = 0.0
    for book in wave_books:
        slug = book["slug"]
        if args.resume and progress.get("books", {}).get(slug, {}).get("status") == "complete":
            log(f"Skip complete: {slug}")
            continue
        meta = next((f for f in full_manifest.get("files", []) if f.get("slug") == slug), book)
        sentence_count = int(meta.get("sentence_count", book.get("sentence_count", 0)))
        est = estimate_cost_usd(sentence_count)
        planned.append(
            {
                "slug": slug,
                "source_file": meta.get("source_file", book.get("source_file")),
                "sentence_count": sentence_count,
                "estimated_cost_usd": est,
            }
        )
        planned_cost += est
        if args.max_books is not None and len(planned) >= args.max_books:
            break

    log(f"Planned books: {len(planned)}  Planned incremental cost: ${planned_cost:.2f}")
    if args.max_cost_usd is not None:
        headroom = args.max_cost_usd - spent_usd
        log(f"Budget cap: ${args.max_cost_usd:.2f}  Headroom: ${headroom:.2f}")
        trimmed: list[dict[str, Any]] = []
        running = 0.0
        for item in planned:
            if running + item["estimated_cost_usd"] > headroom and trimmed:
                break
            if running + item["estimated_cost_usd"] > headroom and not trimmed:
                trimmed.append(item)
                running += item["estimated_cost_usd"]
                break
            trimmed.append(item)
            running += item["estimated_cost_usd"]
        if len(trimmed) < len(planned):
            log(f"Budget trim: {len(planned)} -> {len(trimmed)} books (${running:.2f})")
        planned = trimmed

    if args.dry_run:
        log("--- DRY RUN ---")
        for item in planned:
            log(
                f"  {item['slug']} ({item['source_file']}): "
                f"{item['sentence_count']} sentences, est ${item['estimated_cost_usd']:.2f}"
            )
        log(f"Total planned cost: ${sum(i['estimated_cost_usd'] for i in planned):.2f}")
        return 0

    client = genai.Client()
    registry = load_prompt_registry(args.prompts_dir)
    template_text = get_template_text(args.prompts_dir, args.prompt_family, registry)
    response_schema = load_response_schema(args.schema_file)
    generation_config = build_generation_config(
        temperature=args.temperature,
        max_output_tokens=args.max_output_tokens,
        thinking_budget=args.thinking_budget,
        response_schema=response_schema,
    )
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

    books_run = 0
    for item in planned:
        slug = item["slug"]
        source_file = item["source_file"]
        sentence_count = item["sentence_count"]

        current_spent = spent_usd_for_cap(load_progress(progress_path))
        if args.max_cost_usd is not None and current_spent >= args.max_cost_usd:
            log(f"Budget cap reached (${current_spent:.2f}); stopping before {slug}")
            break

        log(f"\n>>> Book {books_run + 1}/{len(planned)}: {slug} ({sentence_count} sentences)")
        predictions, summary = run_one_book(
            client=client,
            slug=slug,
            source_file=source_file,
            sentence_count=sentence_count,
            full_manifest=full_manifest,
            args=args,
            run_config=run_config,
            template_text=template_text,
            generation_config=generation_config,
        )

        pred_path = predictions_path(args.output_root, slug)
        run_book_review(
            predictions=pred_path,
            book_out=book_dir(args.output_root, slug),
            source_file=source_file,
        )

        parse_ok_rate = float(summary.get("parse_ok_rate", 0))
        border_count = int(summary.get("label_counts", {}).get("BORDER", 0))
        border_rate = border_count / len(predictions) if predictions else 0.0
        book_cost = float(summary.get("estimated_batch_cost_usd", 0))

        progress = load_progress(progress_path)
        status = "complete" if parse_ok_rate >= PARSE_OK_GATE else "blocked"
        update_progress_book(
            progress,
            slug,
            {
                "status": status,
                "source_file": source_file,
                "sentence_count": sentence_count,
                "parse_ok_rate": parse_ok_rate,
                "border_rate": border_rate,
                "estimated_cost_usd": book_cost,
                "completed_at": datetime.now(timezone.utc).isoformat(),
            },
            full_manifest=full_manifest,
        )
        progress["config_hash"] = config_hash(args)
        write_json_atomic(progress_path, progress)
        books_run += 1

        if status == "blocked":
            log(f"BLOCKED: {slug} parse_ok_rate={parse_ok_rate:.1%} < {PARSE_OK_GATE:.0%}")
            return 1

        current_spent = spent_usd_for_cap(progress)
        if args.max_cost_usd is not None and current_spent >= args.max_cost_usd:
            log(f"Budget cap reached after {slug} (${current_spent:.2f})")
            break

    log(f"\nDone. Books processed this session: {books_run}")
    final = load_progress(progress_path)
    totals = final.get("totals", {})
    log(
        f"Corpus progress: {totals.get('books_complete', 0)}/{totals.get('books_total', 0)} books, "
        f"{totals.get('sentences_complete', 0)}/{totals.get('sentences_total', 0)} sentences, "
        f"${totals.get('cost_usd', 0):.2f} spent"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
