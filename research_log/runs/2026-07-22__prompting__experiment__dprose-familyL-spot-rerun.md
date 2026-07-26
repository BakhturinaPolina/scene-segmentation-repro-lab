---
note_type: run
run_id: run_20260722_dprose_familyL_spot_rerun
title: "dProse spot-check subset rerun with Family L (strict definition) vs production B"
date: 2026-07-22
track: prompting
run_type: experiment
status: success
goal: "On four contrasting dProse spot-check texts, measure how Family L (strict MAJOR-discontinuity) changes border rate / consecutive-BORDER runs relative to the production Family B labels."
entrypoint: "src/runners/run_dprose_batch_pilot.py"
command: "set -a && source .env && set +a; PYTHONUNBUFFERED=1 .venv/bin/python -u src/runners/run_dprose_batch_pilot.py --manifest data/manifests/dprose_family_L_spot_rerun.json --mode file --model gemini-2.5-pro --prompt_family L --schema_file src/prompts/json_schema_label_reason.json --context_sentences 12 --temperature 0 --max_output_tokens 2048 --thinking_budget -1 --poll_interval 30 --date 2026-07-22-dprose-familyL-spot-rerun --output_root outputs/runs/dprose_batch"
working_directory: "/home/polina/Documents/Cursor_Projects/scene-segmentation-research"
git_commit: "0bff9746e720d01885165b809a5ce04592e61910"
environment: ".venv (python 3.12), google-genai; GEMINI_API_KEY from .env"
os: "Linux"
hardware: "n/a (server-side batch)"
gpu: "n/a"
cuda_notes: ""
api_provider: "Google Gemini Batch API"
api_model: "gemini-2.5-pro"
api_cost_estimate: "$4.19 (941 sentences)"
dataset_assets:
  - "data/manifests/dprose_family_L_spot_rerun.json"
  - "data/processed/dprose/dprose_{52,100,119,137}/"
  - "outputs/runs/dprose_batch/dprose-full-corpus/books/dprose_{52,100,119,137}/ (production B baseline)"
label_schema: "prediction-only BORDER/NOBORDER (no gold labels)"
prompt_version: "L_zero_shot_json_strict.txt + json_schema_label_reason.json"
model_name: "gemini-2.5-pro"
varying_factor: "prompt family L vs production B (same texts, same decoding/context)"
fixed_conditions:
  - "gemini-2.5-pro, Gemini Batch API, mode=file"
  - "context_sentences=12, temperature=0, max_output_tokens=2048, thinking_budget=-1"
  - "json_schema_label_reason.json"
  - "same four processed dProse texts"
random_seed: "n/a"
output_dir: "outputs/runs/dprose_batch/2026-07-22-dprose-familyL-spot-rerun/"
artifacts_expected:
  - "predictions.jsonl"
  - "pilot_summary.json"
  - "B_vs_L_comparison.json"
artifacts_produced:
  - "outputs/runs/dprose_batch/2026-07-22-dprose-familyL-spot-rerun/predictions.jsonl"
  - "outputs/runs/dprose_batch/2026-07-22-dprose-familyL-spot-rerun/pilot_summary.json"
  - "outputs/runs/dprose_batch/2026-07-22-dprose-familyL-spot-rerun/B_vs_L_comparison.json"
main_metric_name: "BORDER rate delta (L - B) and L∩B F1"
main_metric_value: "Δ rate −7.0 to −11.4 pp; L∩B F1 0.63–0.77"
precision: ""
recall: ""
f1: ""
iou: ""
runtime: "~2.5 min wall (single batch job)"
failure_category: ""
related_experiment: "experiment__prompting__prompt-family__gemini-batch-excel-BKQ.md"
related_issue: ""
decision_relevance: false
notion_targets:
  roadmap: ""
  runs: true
  experiments: true
  artifacts: true
  issues: false
  decisions: false
---

## Objective

Test whether Family L's FP-reduction observed on the Excel gold texts
(F1@3 0.54→0.78, over-pred 4.1×→2.1×) also reduces over-segmentation on
real dProse production texts under identical batch settings.

## What was held constant

Same model/API/context/decoding/schema as the dProse full-corpus production
run. Only the prompt family changes (B → L).

## What changed

Prompt family: production **B** vs strict-definition **L**.

## Texts selected (from DPROSE_CORPUS_SPOT_CHECKS.md)

| Slug | Why interesting | Production B |
|------|-----------------|--------------|
| dprose_52 | Wave 1 highest BORDER (32.8%); fairy-tale travel montage idx 57–62 | 75 borders / 229 |
| dprose_119 | Worst consecutive BORDER run (7) at frame coda / Part 2 title | 62 / 220 |
| dprose_137 | Wave 1 lowest BORDER (14.5%); dialogue-heavy 54-sent gap | 48 / 331 |
| dprose_100 | Pilot book; mid-high rate; Roman-numeral header pattern | 49 / 161 |

Total: 941 sentences. Not a representative sample — deliberately contrasting outliers.

## Outcome

Overall L: 153 BORDER / 941 (16.3%), parse-ok 939/941 (99.8%), cost $4.19.
(Production B on same four texts: 234 BORDER / 941 = 24.9%.)

| slug | B rate | L rate | Δ | B bord | L bord | B maxRun | L maxRun | L∩B F1 | onlyB | onlyL |
|------|--------|--------|---|--------|--------|----------|----------|--------|-------|-------|
| dprose_52 | 32.8% | 23.6% | −9.2pp | 75 | 54 | 6 | 6 | 0.760 | 26 | 5 |
| dprose_119 | 28.2% | 16.8% | −11.4pp | 62 | 37 | 7 | 5 | 0.727 | 26 | 1 |
| dprose_137 | 14.5% | 7.6% | −7.0pp | 48 | 25 | 3 | 2 | 0.630 | 25 | 2 |
| dprose_100 | 30.4% | 23.0% | −7.4pp | 49 | 37 | 3 | 3 | 0.767 | 16 | 4 |

Flagged spots:

- **dprose_52 montage 57–62:** B=[57..62] (6×) → L=[57..61] (5×) — barely thinned.
- **dprose_119 frame/part 155–161:** B=[155..161] (7×) → L=[157..161] (5×) — dropped the first two of the run.
- **dprose_137 gap 40–94:** B borders at 40 and 94 → L only at 94 (even more conservative).

Two parse fails (`dprose_119:57`, `dprose_100:144`) — JSON missing; not retried (parse-ok still 99.8%).

## Interpretation

- **L systematically lowers BORDER rate (−7 to −11 pp) on every contrast type**, including the already-conservative dialogue text. Aggregate borders on these four texts: 234 → 153 (−35%).
- **L is mostly a subset of B:** only_L is tiny (1–5 per book); most removed borders are B-only. L∩B F1 0.63–0.77 means L keeps a large share of B's calls while dropping extras.
- **Dense montage/structural runs are only partially cleaned.** The infamous 6× and 7× consecutive clusters shrink by 1–2, not dissolve. Prompt L alone is not a full substitute for post-process merge rules on those patterns.
- **Risk on low-BORDER texts:** dprose_137 drops to 7.6% — plausible if the goal is film-level scenes, but may under-segment relative to event-level labels. Worth watching if L were considered for full-corpus re-label.

## Next step

Feed into Final Remarks as dProse evidence that a stricter definition cuts over-segmentation on production texts, with the caveat that consecutive-BORDER montages still need post-processing. No full-corpus L re-run recommended yet.
