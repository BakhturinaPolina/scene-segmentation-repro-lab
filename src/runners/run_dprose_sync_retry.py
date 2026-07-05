#!/usr/bin/env python3
"""Re-run parse-failed dProse sentence keys via Gemini sync API (non-batch).

Tier-2 remediation after batch ``--retry_failed`` (see run_dprose_batch_corpus.py).
Uses relaxed safety (BLOCK_NONE), ``thinking_budget=1024``, and records
``parse_error=blocked:...`` for PROHIBITED_CONTENT instead of failing the run.

Wrapper: ``scripts/sweeps/retry_dprose_sync_failed.sh``
Keys snapshot: ``data/manifests/dprose_sync_retry_keys.json``
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from google import genai
from google.genai import types

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.core.prompt_runtime import get_template_text, load_prompt_registry  # noqa: E402
from src.runners.dprose_batch_core import (  # noqa: E402
    build_generation_config,
    load_manifest,
    load_response_schema,
    log,
    manifest_for_book,
    prepare_requests,
    process_results,
)
from src.runners.run_dprose_batch_corpus import (  # noqa: E402
    DEFAULT_OUTPUT_ROOT,
    merge_predictions,
    predictions_path,
    run_book_review,
)

DEFAULT_FULL_MANIFEST = Path("data/manifests/dprose_full.json")


def discover_failed_by_book(output_root: Path) -> dict[str, set[str]]:
    by_book: dict[str, set[str]] = defaultdict(set)
    books_dir = output_root / "books"
    for review_path in books_dir.glob("*/book_review.json"):
        review = json.loads(review_path.read_text(encoding="utf-8"))
        for key in review.get("failed_keys") or []:
            slug = key.split(":")[0]
            by_book[slug].add(key)
    return dict(by_book)


def load_keys_file(path: Path) -> dict[str, set[str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    by_book: dict[str, set[str]] = defaultdict(set)
    for key in payload.get("keys", []):
        slug = str(key).split(":")[0]
        by_book[slug].add(str(key))
    return dict(by_book)


def build_sync_config(
    *,
    temperature: float,
    max_output_tokens: int,
    thinking_budget: int,
    response_schema: dict[str, Any],
) -> types.GenerateContentConfig:
    if thinking_budget <= 0:
        thinking_budget = 1024
    return types.GenerateContentConfig(
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        response_mime_type="application/json",
        response_schema=response_schema,
        thinking_config=types.ThinkingConfig(
            thinking_budget=thinking_budget,
            include_thoughts=True,
        ),
        safety_settings=_relaxed_safety_settings(),
    )


def _relaxed_safety_settings() -> list[types.SafetySetting]:
    categories = [
        types.HarmCategory.HARM_CATEGORY_HARASSMENT,
        types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
    ]
    return [
        types.SafetySetting(category=category, threshold=types.HarmBlockThreshold.BLOCK_NONE)
        for category in categories
    ]


def run_sync_request(
    client: genai.Client,
    *,
    model: str,
    contents: list[dict[str, Any]],
    config: types.GenerateContentConfig,
    max_retries: int,
) -> tuple[Any | None, str | None]:
    last_error: str | None = None
    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )
            block_reason = None
            feedback = getattr(response, "prompt_feedback", None)
            if feedback is not None:
                block_reason = getattr(feedback, "block_reason", None)
            if block_reason:
                return response, f"blocked:{block_reason}"
            return response, None
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)
            if "503" in last_error or "UNAVAILABLE" in last_error:
                time.sleep(min(30, 2**attempt))
                continue
            return None, last_error
    return None, last_error


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full_manifest", type=Path, default=DEFAULT_FULL_MANIFEST)
    parser.add_argument("--data_root", type=Path, default=Path("data"))
    parser.add_argument("--output_root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--keys_file", type=Path, default=None, help="JSON with {\"keys\": [...]}")
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
    parser.add_argument("--max_output_tokens", type=int, default=8192)
    parser.add_argument(
        "--thinking_budget",
        type=int,
        default=1024,
        help="Gemini 2.5 Pro requires thinking mode; 0 maps to 1024.",
    )
    parser.add_argument("--max_retries", type=int, default=3)
    parser.add_argument("--sleep_seconds", type=float, default=1.0)
    parser.add_argument("--dry_run", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def _require_api_key(dry_run: bool) -> None:
    if dry_run:
        return
    if not os.environ.get("GEMINI_API_KEY", "").strip():
        log("ERROR: Set GEMINI_API_KEY (e.g. set -a && source .env && set +a)")
        sys.exit(1)


def main() -> int:
    args = parse_args()
    _require_api_key(args.dry_run)

    if args.keys_file:
        failed_by_book = load_keys_file(args.keys_file)
    else:
        failed_by_book = discover_failed_by_book(args.output_root)

    if not failed_by_book:
        log("No failed keys found; nothing to do.")
        return 0

    total_keys = sum(len(v) for v in failed_by_book.values())
    log(f"=== dProse sync retry started {datetime.now(timezone.utc).isoformat()} ===")
    log(f"Books: {len(failed_by_book)}  Keys: {total_keys}")
    log(
        f"Model: {args.model}  max_output_tokens={args.max_output_tokens}  "
        f"thinking_budget={args.thinking_budget}"
    )

    if args.dry_run:
        for slug in sorted(failed_by_book, key=lambda s: int(s.split("_")[1])):
            keys = sorted(failed_by_book[slug], key=lambda k: int(k.split(":")[1]))
            log(f"  {slug}: {len(keys)} keys")
        log("--- DRY RUN ---")
        return 0

    full_manifest = load_manifest(args.full_manifest)
    registry = load_prompt_registry(args.prompts_dir)
    template_text = get_template_text(args.prompts_dir, args.prompt_family, registry)
    response_schema = load_response_schema(args.schema_file)
    thinking_budget = args.thinking_budget if args.thinking_budget > 0 else 1024
    generation_config = build_generation_config(
        temperature=args.temperature,
        max_output_tokens=args.max_output_tokens,
        thinking_budget=thinking_budget,
        response_schema=response_schema,
    )
    sync_config = build_sync_config(
        temperature=args.temperature,
        max_output_tokens=args.max_output_tokens,
        thinking_budget=thinking_budget,
        response_schema=response_schema,
    )
    client = genai.Client()

    ok_before = 0
    ok_after = 0
    blocked = 0
    books_touched = 0

    for slug in sorted(failed_by_book, key=lambda s: int(s.split("_")[1])):
        keys_filter = failed_by_book[slug]
        book_manifest = manifest_for_book(full_manifest, slug)
        source_file = book_manifest["files"][0]["source_file"]
        pred_path = predictions_path(args.output_root, slug)

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
            log(f"WARN: no requests prepared for {slug}")
            continue

        log(f"\n>>> {slug}: {len(records)} sync requests")
        records_by_key = {r.key: r for r in records}
        result_rows: list[tuple[str | None, Any, Any | None]] = []

        for i, (rec, req) in enumerate(zip(records, inline_requests), start=1):
            log(f"  [{i}/{len(records)}] {rec.key}")
            response, error = run_sync_request(
                client,
                model=args.model,
                contents=req["contents"],
                config=sync_config,
                max_retries=args.max_retries,
            )
            result_rows.append((rec.key, response, error))
            if args.sleep_seconds > 0 and i < len(records):
                time.sleep(args.sleep_seconds)

        new_predictions, summary = process_results(
            result_rows,
            records_by_key,
            prompt_family=args.prompt_family,
            verbose=args.verbose,
        )
        book_ok = sum(1 for r in new_predictions if r.get("parse_ok"))
        book_blocked = sum(
            1 for r in new_predictions if str(r.get("parse_error", "")).startswith("blocked:")
        )
        ok_before += len(new_predictions) - book_ok
        ok_after += book_ok
        blocked += book_blocked
        log(
            f"  sync parse: {book_ok}/{len(new_predictions)} ok "
            f"({summary.get('parse_ok_rate', 0):.1%})"
            + (f"  blocked={book_blocked}" if book_blocked else "")
        )

        merged = merge_predictions(pred_path, new_predictions)
        tmp = pred_path.with_suffix(pred_path.suffix + ".tmp")
        with tmp.open("w", encoding="utf-8") as handle:
            for row in merged:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        os.replace(tmp, pred_path)

        book_out = pred_path.parent
        rc = run_book_review(predictions=pred_path, book_out=book_out, source_file=source_file)
        if rc != 0:
            log(f"WARN: book review exited {rc} for {slug}")
        books_touched += 1

    log(
        f"\n=== Done: {books_touched} books, {total_keys} keys, "
        f"sync recovered {ok_after}/{total_keys}, blocked={blocked} ==="
    )
    return 0 if ok_after == total_keys else 1


if __name__ == "__main__":
    raise SystemExit(main())
