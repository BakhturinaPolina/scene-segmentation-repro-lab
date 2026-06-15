#!/usr/bin/env python3
"""Steps 2–4 of Excel OFAT improvement pipeline after prompt-O sweep.

2. Two-pass verify on Family Q caches (both top models)
3. If Nemotron O recall↑ and over-pred↑ vs Q → min_gap post-process Laguna XS Kleist
4. If best macro F3@3 < 0.76 → sentence-window 32/64 on best prompt (API runs)

Usage (after prompt O sweep completes):
    python scripts/evaluation/excel_ofat_improve_pipeline.py --step all
    python scripts/evaluation/excel_ofat_improve_pipeline.py --step verify
    python scripts/evaluation/excel_ofat_improve_pipeline.py --step postprocess
    python scripts/evaluation/excel_ofat_improve_pipeline.py --step context
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from postprocess.postprocess import evaluate_sampled, apply_min_scene_len

PY = _ROOT / ".venv/bin/python"
VERIFY = _ROOT / "src/runners/run_two_stage_verify.py"
RUNNER = _ROOT / "src/runners/run_prompting_stratified.py"
MANIFEST = _ROOT / "data/manifests/excel_prompting.json"
REVIEW = _ROOT / "review"
F3_GATE = 0.76

MODELS = {
    "nemotron": "nvidia/nemotron-3-super-120b-a12b:free",
    "laguna_xs": "poolside/laguna-xs.2:free",
}

DATE_Q = "2026-06-14-excel-ofat-s1-Q"
DATE_O = "2026-06-14-excel-ofat-O"
DATE_CTX = "2026-06-14-excel-ofat-context"


def _slug(model: str) -> str:
    return model.replace("/", "_").replace(":", "_")


def _run_dir(date: str, model: str, family: str) -> Path:
    return _ROOT / "outputs/runs/prompting" / date / f"full_{_slug(model)}_family{family}_reasoning-off"


def _load_summary(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _macro_f3(summary: Dict[str, Any]) -> float:
    return float(summary.get("macro_avg_tol_3", {}).get("f1", 0) or 0)


def _macro_recall(summary: Dict[str, Any]) -> float:
    return float(summary.get("macro_avg_tol_3", {}).get("recall", 0) or 0)


def _overpred(summary: Dict[str, Any]) -> float:
    return float(summary.get("overprediction_ratio", 0) or 0)


def _run(cmd: List[str], *, check: bool = True) -> int:
    print(f"[cmd] {' '.join(str(c) for c in cmd)}")
    proc = subprocess.run(cmd, cwd=_ROOT)
    if check and proc.returncode != 0:
        raise SystemExit(proc.returncode)
    return proc.returncode


def step_verify() -> Dict[str, Any]:
    """Step 2: verify predicted BORDERs on Q caches."""
    REVIEW.mkdir(parents=True, exist_ok=True)
    reports: Dict[str, Any] = {}
    for key, model in MODELS.items():
        run_dir = _run_dir(DATE_Q, model, "Q")
        out = REVIEW / f"verify_Q_{key}.json"
        if not run_dir.exists():
            print(f"SKIP verify {key}: missing {run_dir}")
            continue
        _run([
            str(PY), str(VERIFY),
            "--run_dir", str(run_dir),
            "--verifier_model", MODELS["nemotron"],
            "--verify_style", "yes_no",
            "--context_window", "3",
            "--request_delay", "0.5",
            "--out", str(out),
        ])
        reports[key] = json.loads(out.read_text(encoding="utf-8"))
    return reports


def _verify_macro_f3(report: Dict[str, Any]) -> Tuple[float, float]:
    """Average F3@3 after verify across documents in batch report."""
    f1s, recalls = [], []
    for doc in report.get("documents", {}).values():
        after = doc.get("metrics_after", {})
        m = after.get("tol_3")
        if m:
            f1s.append(m["f1"])
            recalls.append(m["recall"])
    if not f1s:
        return 0.0, 0.0
    return sum(f1s) / len(f1s), sum(recalls) / len(recalls)


def _gaensemagd_metrics(cache_path: Path) -> Optional[Dict[str, float]]:
    if not cache_path.exists():
        return None
    cache = json.loads(cache_path.read_text(encoding="utf-8"))
    indices = sorted(int(k) for k in cache.keys())
    preds = [str(cache[str(i)]["pred"]).upper() for i in indices]
    golds = [str(cache[str(i)]["gold"]).upper() for i in indices]
    size = max(indices) + 1
    full_gold = ["NOBORDER"] * size
    for i, g in zip(indices, golds):
        full_gold[i] = g
    m = evaluate_sampled(indices, preds, full_gold, 3)
    n_pred = sum(1 for p in preds if p == "BORDER")
    n_gold = sum(1 for g in golds if g == "BORDER")
    return {
        "f3": m["f1"],
        "recall": m["recall"],
        "overpred": n_pred / n_gold if n_gold else 0.0,
    }


def step_postprocess(nemotron_o: Dict[str, Any], nemotron_q: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Step 3: min_gap on Laguna XS Kleist if Nemotron O recall↑ and over-pred↑ vs Q."""
    if nemotron_o.get("run_complete"):
        o_rec, o_over = _macro_recall(nemotron_o), _overpred(nemotron_o)
        q_rec, q_over = _macro_recall(nemotron_q), _overpred(nemotron_q)
    else:
        o_g = _run_dir(DATE_O, MODELS["nemotron"], "O") / "cache_gaensemagd_sentence_level.json"
        q_g = _run_dir(DATE_Q, MODELS["nemotron"], "Q") / "cache_gaensemagd_sentence_level.json"
        o_m, q_m = _gaensemagd_metrics(o_g), _gaensemagd_metrics(q_g)
        if not o_m or not q_m:
            print("Step 3 SKIP: Nemotron O incomplete and no Gänsemagd caches to compare")
            return None
        o_rec, o_over = o_m["recall"], o_m["overpred"]
        q_rec, q_over = q_m["recall"], q_m["overpred"]
        print("Using Gänsemagd-only comparison (Nemotron O Kleist still in progress)")
    print(f"Nemotron O vs Q: recall {o_rec:.3f} vs {q_rec:.3f}, over-pred {o_over:.2f} vs {q_over:.2f}")

    if not (o_rec > q_rec and o_over > q_over):
        print("Step 3 SKIP: condition not met (need O recall↑ AND over-pred↑ vs Q)")
        return None

    kleist_o = _run_dir(DATE_O, MODELS["laguna_xs"], "O") / "cache_kleist_sentence_level.json"
    kleist_q = _run_dir(DATE_Q, MODELS["laguna_xs"], "Q") / "cache_kleist_sentence_level.json"
    cache_path = kleist_o if kleist_o.exists() else kleist_q
    if not cache_path.exists():
        print(f"Step 3 SKIP: no Kleist cache at {cache_path}")
        return None

    cache = json.loads(cache_path.read_text(encoding="utf-8"))
    indices = sorted(int(k) for k in cache.keys())
    preds = [str(cache[str(i)]["pred"]).upper() for i in indices]
    golds = [str(cache[str(i)]["gold"]).upper() for i in indices]
    size = max(indices) + 1
    full_gold = ["NOBORDER"] * size
    for i, g in zip(indices, golds):
        full_gold[i] = g

    best: Optional[Dict[str, Any]] = None
    for gap in (2, 3, 4):
        adj = apply_min_scene_len(preds, min_gap=gap)
        m = evaluate_sampled(indices, adj, full_gold, 3)
        n_pred = sum(1 for p in adj if p == "BORDER")
        n_gold = sum(1 for g in golds if g == "BORDER")
        row = {
            "gap": gap,
            "cache": str(cache_path),
            "f3": m["f1"],
            "precision": m["precision"],
            "recall": m["recall"],
            "pred_borders": n_pred,
            "gold_borders": n_gold,
            "overpred": n_pred / n_gold if n_gold else 0,
        }
        print(f"  min_gap={gap}: F3={m['f1']:.3f} P={m['precision']:.3f} R={m['recall']:.3f} pred={n_pred}")
        if best is None or row["f3"] > best["f3"]:
            best = row

    out = REVIEW / "postprocess_laguna_xs_kleist_min_gap.json"
    out.write_text(json.dumps(best, indent=2), encoding="utf-8")
    print(f"Wrote {out}")
    return best


def _candidates() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for date, family in [(DATE_Q, "Q"), (DATE_O, "O")]:
        for key, model in MODELS.items():
            s = _load_summary(_run_dir(date, model, family) / "summary.json")
            if s and s.get("run_complete"):
                rows.append({
                    "key": key,
                    "model": model,
                    "family": family,
                    "date": date,
                    "f3": _macro_f3(s),
                    "recall": _macro_recall(s),
                    "overpred": _overpred(s),
                    "summary_path": str(_run_dir(date, model, family) / "summary.json"),
                })
    # verify Q reports
    for key in MODELS:
        vp = REVIEW / f"verify_Q_{key}.json"
        if vp.exists():
            rep = json.loads(vp.read_text(encoding="utf-8"))
            f3, rec = _verify_macro_f3(rep)
            rows.append({
                "key": key,
                "model": MODELS[key],
                "family": "Q+verify",
                "date": DATE_Q,
                "f3": f3,
                "recall": rec,
                "overpred": None,
                "summary_path": str(vp),
            })
    pp = REVIEW / "postprocess_laguna_xs_kleist_min_gap.json"
    if pp.exists():
        p = json.loads(pp.read_text(encoding="utf-8"))
        rows.append({
            "key": "laguna_xs",
            "model": MODELS["laguna_xs"],
            "family": "Q/O+min_gap_kleist",
            "date": DATE_O,
            "f3": p["f3"],
            "recall": p["recall"],
            "overpred": p["overpred"],
            "summary_path": str(pp),
        })
    return sorted(rows, key=lambda r: r["f3"], reverse=True)


def step_context() -> None:
    """Step 4: run sentence windows 32 and 64 on best prompt if F3 < gate."""
    rows = _candidates()
    if not rows:
        print("Step 4 SKIP: no completed runs to pick best prompt from")
        return

    best = rows[0]
    print(f"Best so far: {best['model']} family={best['family']} F3={best['f3']:.3f}")
    REVIEW.mkdir(parents=True, exist_ok=True)
    (REVIEW / "excel_ofat_pipeline_candidates.json").write_text(
        json.dumps(rows, indent=2), encoding="utf-8"
    )

    if best["f3"] >= F3_GATE:
        print(f"Step 4 SKIP: F3 {best['f3']:.3f} >= gate {F3_GATE}")
        return

    family = best["family"].replace("+verify", "").replace("/O+min_gap_kleist", "")
    if family not in {"Q", "O", "B"}:
        family = "O" if _load_summary(_run_dir(DATE_O, best["model"], "O") / "summary.json") else "Q"

    model = best["model"]
    for window in (32, 64):
        tag = f"{DATE_CTX}-w{window}"
        log = _ROOT / "logs/excel_ofat" / f"context_w{window}_{_slug(model)}_family{family}.log"
        log.parent.mkdir(parents=True, exist_ok=True)
        summary = _run_dir(tag, model, family) / "summary.json"
        if summary.exists():
            s = _load_summary(summary)
            if s and s.get("run_complete"):
                print(f"skip complete context w={window} family={family}")
                continue
        cmd = [
            str(PY), str(RUNNER),
            "--excel_manifest", str(MANIFEST),
            "--model", model,
            "--prompt_family", family,
            "--full_eval",
            "--apply_model_profile",
            "--reasoning", "off",
            "--temperature", "0", "--top_p", "1.0", "--seed", "1337",
            "--max_tokens", "256",
            "--context_mode", "sentences",
            "--sentence_window", str(window),
            "--date", tag,
            "--request_delay", "0.5",
            "--rate_limit_cooldown", "180",
        ]
        with log.open("a", encoding="utf-8") as fh:
            subprocess.run(cmd, cwd=_ROOT, stdout=fh, stderr=subprocess.STDOUT, check=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--step",
        choices=["verify", "postprocess", "context", "all"],
        default="all",
    )
    args = parser.parse_args()

    nemotron_o = _load_summary(_run_dir(DATE_O, MODELS["nemotron"], "O") / "summary.json") or {}
    nemotron_q = _load_summary(_run_dir(DATE_Q, MODELS["nemotron"], "Q") / "summary.json") or {}

    if args.step in ("verify", "all"):
        print("=== Step 2: verify Q caches ===")
        step_verify()

    if args.step in ("postprocess", "all"):
        print("=== Step 3: conditional min_gap ===")
        if not nemotron_o.get("run_complete"):
            print("WARN: Nemotron O not complete; postprocess uses partial/missing O summary")
        step_postprocess(nemotron_o, nemotron_q)

    if args.step in ("context", "all"):
        print("=== Step 4: context windows if F3 < 0.76 ===")
        step_context()

    rows = _candidates()
    print("\n=== Pipeline candidates (by F3@3) ===")
    for r in rows[:8]:
        op = f"{r['overpred']:.2f}" if r.get("overpred") is not None else "n/a"
        print(f"  {r['model'][:40]:40} fam={r['family']:12} F3={r['f3']:.3f} R={r['recall']:.3f} over={op}")


if __name__ == "__main__":
    main()
