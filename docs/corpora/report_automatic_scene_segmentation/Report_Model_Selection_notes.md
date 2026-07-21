# Model Selection and Evaluation — Research Notes (collection)

**Purpose:** raw evidence dump for expanding §Model Selection and Evaluation (lines 50–78) of [`Report_Automatic Scene Segmentation_draft.md`](Report_Automatic%20Scene%20Segmentation_draft.md). This is a notes drop, not finished prose — verbatim quotes, exact numbers, and sources are preserved so the section author can lift what they need. Scope is strictly the Model Selection and Evaluation section; Task Definition, dProse application, and Final Remarks are out of scope (though a few bridges are flagged).

Every claim is followed by its source. Numbers were re-checked against the run artefacts on disk, not just the summary reports.

---

## 1. Prompt comparison — verbatim texts side by side

This is the most important content for the two open TODO prompts in the draft (lines 60–62: *"Quickly explain what is different to Zehe et al and why"* and *"Add one note to the context sizes, temperature and whatever is important here"*).

### 1a. Zehe et al. zero-shot prompt ("No-CoT")

This is the **only** prompt Zehe et al. used for zero-shot prompting. Source: paper Appendix A.2, [`docs/reference/2025.naacl-long.500.md`](../../reference/2025.naacl-long.500.md) lines 378–392, and the shipped upstream code at [`upstream/scene-segmentation/prompting/classify.py`](../../../upstream/scene-segmentation/prompting/classify.py) lines 34–39.

Verbatim (paper Appendix A.2 formatting):

```
Does the sentence in <sentence>...</sentence> introduce the beginning
of a new scene and a significant break in time, location or characters?
Answer 'True' or 'False' and provide a reason for your decision.

A scene is defined as a segment of text with a coherent structure across
the dimensions 'characters' (which characters are present in the narration),
'location' (where does the narration take place), and 'time' (continuous
time in the narration). A significant break in any of these dimensions
corresponds to a scenes change.

→ [True/False], because there is [a/no] significant change in [narrative
action, location, time or characters].
```

Note: the upstream code string (`prompt_classify`, lines 34–39) is identical in wording but drops the `→ [True/False], because…` answer-template line; that arrow line only appears in the paper appendix.

### 1b. Zehe et al. "CoT-List" prompt (context only — NOT used zero-shot)

The paper's second template. **Important caveat:** it was used only for *fine-tuning* the Llama models, never for zero-shot prompting (paper §4.2, [`2025.naacl-long.500.md`](../../reference/2025.naacl-long.500.md) lines 122–127; and [`docs/prompting/PROMPTING_RESULTS_REPORT.md`](../../prompting/PROMPTING_RESULTS_REPORT.md) §1). Included here so the report author doesn't accidentally attribute it to Zehe's prompting setup. Source: paper Appendix A.2 lines 395–414; upstream `prompt_classify_cot`, [`classify.py`](../../../upstream/scene-segmentation/prompting/classify.py) lines 41–51.

```
A scene is defined as a segment of text with a coherent structure across
the dimensions 'characters' (which characters are present in the narration),
'location' (where does the narration take place), and 'time' (continuous
time in the narration). A significant break in any of these dimensions
corresponds to a scenes change. Does the sentence in <sentence>...</sentence>
introduce the beginning of a new scene? Think step by step:
a) Does the sentence introduce a significant change in narrative action?
b) Does the sentence introduce a significant change in location?
c) Does the sentence introduce a significant change in time?
d) Does the sentence introduce a significant change in characters?
e) Does the sentence therefore start a new scene?

→ a) There is [a/no] significant change in narrative action,
b) there is [a/no] significant change in location,
c) there is [a/no] significant change in time,
d) there is [a/no] significant change in characters,
e) therefore, the sentence [starts/does not start] a new scene.
```

Additional Zehe detail worth knowing: the gold annotations partially contain a *reason* (location, characters, …) for each scene change; Zehe used that to fill in the answer templates when building fine-tuning targets (paper Appendix A.2, line 376). Label extraction was by string matching — No-CoT: "check whether the response starts with 'True'/'False'"; CoT-List: regex on the a)–e) groups (Appendix A.2 lines 421–432). The upstream zero-shot loop retries up to 10× on unparseable output ([`classify.py`](../../../upstream/scene-segmentation/prompting/classify.py) lines 141–159).

### 1c. Our production prompt ("Family B", zero-shot JSON)

This is the prompt shown as the image in the draft ([`image_1.png`](Report_Automatic_Scene_Segmentation_assets/image_1.png)). Source of truth: [`src/prompts/B_zero_shot_json.txt`](../../../src/prompts/B_zero_shot_json.txt).

```
Task: Decide whether the marked sentence starts a new event/scene segment.

Definition:
A new segment starts when there is a significant change in time, location,
participating characters, or ongoing action.

Context before:
{left_context}

Target sentence:
<sentence>{target_sentence}</sentence>

Context after:
{right_context}

Return JSON only:
{
  "label": "BORDER" or "NOBORDER",
  "confidence": 0.0 to 1.0
}
```

Placeholders `{left_context}` / `{target_sentence}` / `{right_context}` are filled by the runtime context builder (see §3). The registry entry: family `B`, schema `json_label_confidence`, [`src/prompts/registry.json`](../../../src/prompts/registry.json) lines 17–22.

### 1d. Concrete differences (Family B vs Zehe No-CoT)

Ready-to-use bullets for the draft's line 60 TODO:

- **Output format.** Zehe: free-text answer starting with `'True'`/`'False'` followed by a prose reason, parsed by string matching with up to 10 retries. Ours: strict **JSON** enforced by a provider-side schema (`response_format=json_schema`), which yielded **0 parse failures** on Gemini across both gold texts (see §4).
- **Label vocabulary.** Zehe: `True`/`False`. Ours: `BORDER`/`NOBORDER` (the task's own label names; equivalent to IOB2 `B`/`I`, per paper §2, [`2025.naacl-long.500.md`](../../reference/2025.naacl-long.500.md) line 53).
- **Dimensions named in the definition.** Zehe No-CoT names **three**: characters, location, time. Ours names **four**: time, location, participating characters, **and ongoing action**. (Note: Zehe's *underlying* scene definition is four-dimensional — time, space, action, character, paper §2 line 37 — and the CoT-List prompt does enumerate action; but the No-CoT prompt text itself omits action. Our Family B restores "ongoing action" into the zero-shot definition.)
- **Explicit context slots.** Ours labels the surrounding text as explicit "Context before:" / "Context after:" blocks around the marked target. Zehe wraps the target in `<sentence>...</sentence>` and surrounds it with context but does not label the two sides separately. Both use the same `<sentence>...</sentence>` marker.
- **Template length / style.** Ours is deliberately short (a one-line task, a two-line definition, the three context slots, and the JSON contract). Zehe's is a single prose paragraph with an answer template.
- **Confidence field.** Ours asks for a `confidence` (0.0–1.0); Zehe asks only for a reason.
- **No chain-of-thought.** Neither zero-shot prompt asks for step-by-step reasoning (that is Zehe's fine-tuning-only CoT-List). Our Phase A sweep found that adding rubrics/CoT/examples *hurt* zero-shot quality (see §2).

### 1e. Known inconsistency to be aware of

The Family B **prompt text** asks for `{"label", "confidence"}`, but the **enforced JSON schema** used in production ([`src/prompts/json_schema_label_reason.json`](../../../src/prompts/json_schema_label_reason.json)) requires `{"label", "reason"}` (label enum `BORDER`/`NOBORDER`, `reason` minLength 1, `additionalProperties: false`):

```json
{
  "name": "scene_boundary_label_reason",
  "strict": true,
  "schema": {
    "type": "object",
    "properties": {
      "label":  { "type": "string", "enum": ["BORDER", "NOBORDER"] },
      "reason": { "type": "string", "minLength": 1 }
    },
    "required": ["label", "reason"],
    "additionalProperties": false
  }
}
```

So the model actually returns `label` + `reason`, not `label` + `confidence`, whenever `--response_format json_schema --schema_file json_schema_label_reason.json` is used (which is the production config for Gemini/Excel/dProse). The `confidence` line in the prompt is effectively vestigial under schema enforcement. Only worth mentioning if the report quotes the JSON contract precisely; the image in the draft shows the `confidence` version.

---

## 2. Why Family B specifically (Phase A evidence)

The draft implies "we used the following prompt" without saying why *this* shape. The justification is the Phase A family sweep.

**Setup:** 10 prompt families (A–J) on `nvidia/nemotron-3-super-120b-a12b:free`, pilot stratified scope (~60 sentences), STSS-Test-2 (the two high-literature novels *Aus guter Familie* + *Effi Briest*), locked decoding (temperature 0, top_p 1.0, seed 1337, max_tokens 256, context 409, reasoning low). Source: [`research_log/runs/2026-05-15__prompting__experiment__stss2-phase-a-family-sweep-nemotron.md`](../../../research_log/runs/2026-05-15__prompting__experiment__stss2-phase-a-family-sweep-nemotron.md); narrative in [`docs/prompting/PROMPTING_RESULTS_REPORT.md`](../../prompting/PROMPTING_RESULTS_REPORT.md) §5.1.

Full ranking (macro F1 at tolerance 0, pilot scope):

| Rank | Family | Style | F1@0 | P@0 | R@0 | F1@1 | F1@3 | parse_fail |
|------|--------|-------|------|-----|-----|------|------|------------|
| 1 | **B** | zero-shot JSON | **0.862** | 0.864 | 0.867 | 0.877 | 0.891 | 0.000 |
| 2 | E | few-shot contrastive pairs | 0.821 | 0.887 | 0.767 | 0.852 | 0.868 | 0.000 |
| 3 | D | few-shot balanced | 0.747 | 0.677 | 0.833 | 0.772 | 0.794 | 0.000 |
| 4 | G | visible CoT rubric | 0.729 | 0.804 | 0.667 | 0.792 | 0.808 | 0.000 |
| 5 | C | zero-shot rubric JSON | 0.712 | 0.896 | 0.600 | 0.727 | 0.741 | 0.000 |
| 6 | A | label only (no JSON) | 0.692 | 0.562 | 0.900 | 0.733 | 0.771 | 0.000 |
| 7 | I | scoring over short chunk | 0.621 | 0.643 | 0.600 | 0.655 | 0.691 | 0.000 |
| 8 | F | hidden-rationale rubric | 0.586 | 0.917 | 0.433 | 0.586 | 0.598 | 0.000 |
| 9 | J | two-stage classify-after-analysis | 0.548 | 0.900 | 0.400 | 0.548 | 0.558 | 0.000 |
| 10 | H | localization over short chunk | 0.111 | 0.333 | 0.067 | 0.111 | 0.118 | 0.000 |

**Headline finding (quotable):** *prompt shape matters more than prompt cleverness.* The plain short JSON prompt (B) beat every more elaborate variant — rubrics (C, F), visible chain-of-thought (G), few-shot examples (D, E), and two-stage analysis (J). B also had the most balanced precision/recall (P=0.864, R=0.867). This is the direct counterpoint to Zehe's fine-tuning finding that "Chain of Thought reasoning is very beneficial" (paper §7.2) — that benefit did not transfer to zero-shot prompting in our setting ([`PROMPTING_RESULTS_REPORT.md`](../../prompting/PROMPTING_RESULTS_REPORT.md) §5.1).

The full family grid A–J is described in [`src/prompts/README.md`](../../../src/prompts/README.md) and [`src/prompts/registry.json`](../../../src/prompts/registry.json). Families K–Q are later precision-focused variants of B (negatives, strict definition, FP guard, rarity prior, German fairy few-shot, anti-example, precision-fixed) — not part of the original selection but relevant if the report discusses over-segmentation mitigation.

**Caveat on the numbers above:** these are *pilot* scope. A later decision established that pilot F1 overstates full-data F1 — for the same combo the pilot read 0.862 F1@0 vs 0.763 at full stratified scope (a 0.099 gap). Pilot numbers are valid for *ranking* families, not as headline figures. Source: [`decision__pilot-vs-full-and-reasoning-off-candidate.md`](../../../research_log/decisions/decision__pilot-vs-full-and-reasoning-off-candidate.md).

---

## 3. Decoding controls and context construction

For the draft's line 62 TODO (*"Add one note to the context sizes, temperature and whatever is important here"*).

### 3a. Decoding controls (Excel gold-standard evaluation runs)

From the actual run config [`outputs/runs/prompting/2026-05-31-excel-gemini-reasoning-on/full_google_gemini-2.5-pro_familyB_reasoning-on/config.json`](../../../outputs/runs/prompting/2026-05-31-excel-gemini-reasoning-on/full_google_gemini-2.5-pro_familyB_reasoning-on/config.json) and `command.txt`:

| Setting | Value |
|---------|-------|
| Model | `google/gemini-2.5-pro` (via OpenRouter) |
| Prompt family | B |
| Reasoning | `on` (high effort) |
| Temperature | 0.0 |
| top_p | 1.0 |
| seed | 1337 |
| max_tokens | 256 |
| response_format | `json_schema` (`json_schema_label_reason.json`) |
| context_size | 409 tokens |
| full_eval | true (all sentences, natural class balance) |

Exact command:

```
src/run_prompting_stratified.py --excel_manifest data/processed/manifest_excel_prompting.json \
  --model google/gemini-2.5-pro --prompt_family B --full_eval --reasoning on \
  --temperature 0 --top_p 1.0 --seed 1337 --max_tokens 256 \
  --response_format json_schema --schema_file src/prompts/json_schema_label_reason.json \
  --date 2026-05-31-excel-gemini-reasoning-on
```

### 3b. Context window construction

- Default mode is **token budget**: `context_size = 409` tokens = `512 × 0.8`. This is inherited directly from Zehe's upstream code (`INPUT_PERCENTAGE = 0.8`, applied to a 512-token window), [`upstream/scene-segmentation/prompting/classify.py`](../../../upstream/scene-segmentation/prompting/classify.py) line 25. Zehe kept the context at 512 tokens specifically "to allow a fair comparison to the BERT-based models" (paper §6.3, [`2025.naacl-long.500.md`](../../reference/2025.naacl-long.500.md) line 205).
- The context grows **symmetrically** around the target sentence, alternately adding a previous then a next sentence until the token budget is reached. Upstream: [`classify.py`](../../../upstream/scene-segmentation/prompting/classify.py) lines 93–111 (`build_sentence_sample`). Our mirror + a sentence-count alternative: [`src/core/context_builder.py`](../../../src/core/context_builder.py).
- An alternative **sentence-count** mode exists (`--context_mode sentences --sentence_window N`), used for dProse (see §3c).

### 3c. dProse production config (different from the Excel eval runs)

The dProse full-corpus run used the direct Gemini Batch API, not OpenRouter, with a wider **sentence-count** context. Source: [`docs/corpora/DPROSE_CORPUS_SPOT_CHECKS.md`](../DPROSE_CORPUS_SPOT_CHECKS.md) header and [`research_log/runs/2026-06-20__prompting__experiment__dprose-batch-pilot-2048.md`](../../../research_log/runs/2026-06-20__prompting__experiment__dprose-batch-pilot-2048.md); code in [`src/runners/dprose_batch_core.py`](../../../src/runners/dprose_batch_core.py) (`BatchRunConfig`, lines 43–53).

| Setting | Value |
|---------|-------|
| Model | `gemini-2.5-pro` (Gemini Batch API) |
| Prompt family | B + `json_schema_label_reason.json` |
| Context | **12 sentences each side** (`context_sentences=12`) |
| Temperature | 0 |
| max_output_tokens | 2048 |
| thinking_budget | -1 (dynamic) |

(Only relevant to §Model Selection if the report notes that the evaluated config and the production config differ in context sizing and API path. Detailed dProse application belongs to the out-of-scope dProse section.)

### 3d. Reasoning-mode mechanics and the Gemini caveat

- Reasoning "on" maps to OpenRouter `reasoning: {effort: "high"}`; "off" → `{effort: "none"}`; "low" → `{effort: "low"}`. For the direct Gemini Batch API it is `thinking_budget=-1` (dynamic). Source: [`docs/prompting/NEMOTRON_MEMO.md`](../../prompting/NEMOTRON_MEMO.md) §"Reasoning Modes"; code path [`run_prompting_stratified.py`](../../../src/runners/run_prompting_stratified.py) `--reasoning`.
- **Gemini 2.5 Pro cannot run with `reasoning=off`.** When forced, every request failed to produce parseable output (100% parse failure, avg latency ~31s, all metrics 0.0). Evidence: [`outputs/runs/prompting/2026-05-30-excel-3model-sweep/full_google_gemini-2.5-pro_familyB_reasoning-off/summary.json`](../../../outputs/runs/prompting/2026-05-30-excel-3model-sweep/full_google_gemini-2.5-pro_familyB_reasoning-off/summary.json) (`avg_parse_failure_rate: 1.0`). Documented conclusion: "`google/gemini-2.5-pro` does not accept `reasoning=off`; minimum working setting is `reasoning=low`" ([`EXCEL_PROMPTING_2026-05-30_REPORT.md`](../../prompting/EXCEL_PROMPTING_2026-05-30_REPORT.md) §H, line 224).

---

## 4. Model comparison — full numbers

The draft's ranking table (lines 70–76) reproduced with its provenance and the underlying per-document detail.

### 4a. The 5-model ranking table (as in the report)

Source: [`docs/prompting/EXCEL_EXPERIMENTS_COMPARISON_REPORT.md`](../../prompting/EXCEL_EXPERIMENTS_COMPARISON_REPORT.md) §2, macro-averaged over Gaensemagd + Kleist, Prompt B, full evaluation.

| Rank | Model | Reasoning mode | Exact F1 (tol0) | Relaxed F1 (tol3) |
|------|-------|----------------|-----------------|-------------------|
| 1 | Gemini 2.5 Pro | On | **0.50** | **0.76** |
| 2 | Gemini 2.5 Pro | Low | 0.49 | 0.72 |
| 3 | Claude Opus 4 | Off | 0.44 | 0.61 |
| 4 | GPT-4.1 | Off | 0.42 | 0.62 |
| 5 | Claude Sonnet 4 | Off | 0.35 | 0.50 |

Source run folders (each with its own `summary.json`): `2026-05-31-excel-gemini-reasoning-on/` (Gemini on), `2026-05-30-excel-3model-sweep/` (Gemini low, GPT-4.1, Sonnet 4), `2026-05-30-excel-opus4/` (Opus 4).

### 4b. Exact underlying macro numbers (re-read from the summary.json files)

More precise than the rounded table above:

| Model | Reasoning | macro P@0 | macro R@0 | macro F1@0 | macro F1@1 | macro F1@3 | parse-fail | avg latency (s) |
|-------|-----------|-----------|-----------|------------|------------|------------|------------|-----------------|
| Gemini 2.5 Pro | on  | 0.3579 | 0.8215 | **0.4981** | 0.6779 | **0.7617** | 0.0 | 3.434 |
| Gemini 2.5 Pro | low | 0.3479 | 0.8571 | 0.4949 | 0.6357 | 0.7184 | 0.0 | 3.505 |
| Claude Opus 4 | off | 0.2822 | 0.9643 | 0.4365 | 0.5214 | 0.6134 | 0.0 | 4.095 |
| GPT-4.1 | off | — | — | 0.4190 | — | 0.6160 | — | 2.005 |
| Claude Sonnet 4 | off | — | — | 0.3506 | — | 0.4965 | — | 1.383 |

Sources: [`.../2026-05-31-excel-gemini-reasoning-on/.../summary.json`](../../../outputs/runs/prompting/2026-05-31-excel-gemini-reasoning-on/full_google_gemini-2.5-pro_familyB_reasoning-on/summary.json), [`.../2026-05-30-excel-3model-sweep/full_google_gemini-2.5-pro_familyB_reasoning-low/summary.json`](../../../outputs/runs/prompting/2026-05-30-excel-3model-sweep/full_google_gemini-2.5-pro_familyB_reasoning-low/summary.json), [`.../2026-05-30-excel-opus4/full_anthropic_claude-opus-4_familyB_reasoning-off/summary.json`](../../../outputs/runs/prompting/2026-05-30-excel-opus4/full_anthropic_claude-opus-4_familyB_reasoning-off/summary.json), and [`comparison_4model_with_opus.csv`](../../../outputs/runs/prompting/2026-05-30-excel-3model-sweep/comparison_4model_with_opus.csv) (GPT-4.1 and Sonnet 4 rows).

### 4c. Per-document detail for the winner (Gemini 2.5 Pro, reasoning on)

From [`.../2026-05-31-excel-gemini-reasoning-on/.../summary.json`](../../../outputs/runs/prompting/2026-05-31-excel-gemini-reasoning-on/full_google_gemini-2.5-pro_familyB_reasoning-on/summary.json):

| Text | n sents | gold borders | tol0 P/R/F1 | tol3 P/R/F1 | accuracy | parse-fail |
|------|--------:|-------------:|-------------|-------------|----------|------------|
| Gaensemagd | 71 | 7 | 0.333 / 0.714 / 0.455 | 0.700 / 1.000 / 0.824 | 0.831 | 0 |
| Kleist | 245 | 14 | 0.382 / 0.929 / 0.542 | 0.538 / 1.000 / 0.700 | 0.910 | 0 |

Notable: **recall reaches 1.00 at tol=3 on both texts** — the model never misses a true scene border once a 3-sentence tolerance is allowed. The precision cost (many extra borders) is the over-segmentation signal (see §7).

### 4d. Reasoning `on` vs `low` delta (Gemini)

Source: [`EXCEL_PROMPTING_2026-05-30_REPORT.md`](../../prompting/EXCEL_PROMPTING_2026-05-30_REPORT.md) §H.

- macro F1@0: **+0.0032** (0.4981 vs 0.4949)
- macro F1@1: **+0.0422** (0.6779 vs 0.6357)
- macro F1@3: **+0.0433** (0.7617 vs 0.7184)
- avg latency: slightly lower for `on` (3.434s vs 3.505s)
- parse failures: 0 for both

Interpretation (quotable): turning reasoning from "low" to "on" barely moves exact F1 but clearly helps near-match quality (tol3 +0.043), and does not cost latency. Combined with the fact that Gemini cannot run at all with reasoning off (§3d), reasoning **on** is the natural production choice.

### 4e. Reproducibility / stability check

A rerun on the same two texts with identical controls (Family B, reasoning on, seed 1337) on 2026-06-16 gave macro F1@0 = **0.5063** and F1@3 = **0.7707** — within ±0.02 of the May baseline (0.4981 / 0.7617). Over-prediction ~2.24× gold, 0 parse failures. Source: [`docs/planning/EXCEL_FP_REDUCTION_OFAT_PLAN.md`](../../planning/EXCEL_FP_REDUCTION_OFAT_PLAN.md) §"Gemini B stability rerun"; the ±0.02 recompute note is in [`EXCEL_EXPERIMENTS_COMPARISON_REPORT.md`](../../prompting/EXCEL_EXPERIMENTS_COMPARISON_REPORT.md) line 69.

### 4f. Note on models not chosen for reasons other than F1

GPT-4.1 (0.42 tol0) and Claude Sonnet 4 (0.35) trail Gemini clearly. Opus 4 (0.44) is close on exact F1 but weaker on relaxed F1 (0.61). All non-Gemini models were run reasoning `off`. Gemini's edge is largest on the relaxed (tol3) metric, which is the one Zehe treats as the headline metric.

---

## 5. Evaluation metrics — precise definitions

For the draft's line 66 TODO (*"Quickly explain the used metrics: exact and relaxed F1-Score (in line with Zehe et al.)"*).

### 5a. Exact F1 (tolerance 0)

Standard sentence-level F1 on the minority `BORDER` class: each sentence is labelled BORDER/NOBORDER and F1 is computed against gold. It is strict — a border predicted one sentence off counts as a complete miss (one FP + one FN). Paper's own words: "moving the boundary by one sentence in either direction would be counted as a complete miss" (paper §6.1, [`2025.naacl-long.500.md`](../../reference/2025.naacl-long.500.md) line 163). The paper argues the exact F1 *underestimates* real performance (contribution #3, line 29).

### 5b. Relaxed F1 (tolerance 3) — the headline metric

Verbatim definition (paper §6.1, [`2025.naacl-long.500.md`](../../reference/2025.naacl-long.500.md) line 171):

> "We propose to use a variant of the F1-score, which we call **relaxed**. For this score, we apply a tolerance *t* to the predictions made by the model: We add a post-processing step to the predicted labels, where, if a predicted scene border is within *t* sentences of a gold annotated scene border, we move the predicted scene border to the correct position. After that, we calculate the sentence-level F1-score as usual. We use the relaxed F1-score for evaluation and set the tolerance to **t = 3** … All reported scores are for the minority class `BORDER`. We compute the dataset-level score as the unweighted average of the scores for all texts in the dataset."

Key points to carry into the report:

- Tolerance `t = 3` is Zehe's chosen value; `t = 0` is identical to exact F1.
- Scores are for the **BORDER** (minority) class only.
- Dataset-level = **unweighted (macro) mean** across texts — this is why our tables report "macro" averages over Gaensemagd + Kleist.
- Zehe reports **only** t=3 as "relaxed"; our runs additionally compute t=1 as an internal intermediate (not part of Zehe's protocol).

### 5c. Our implementation matches Zehe's definition

The scorer applies the same "predicted border counts if a gold border is within the tolerance window" logic on both precision and recall sides: [`src/runners/run_prompting_stratified.py`](../../../src/runners/run_prompting_stratified.py) `evaluate_sampled`, lines 705–742 (window = `range(idx - tolerance, idx + tolerance + 1)`).

### 5d. Metrics Zehe considered and dropped (context)

Zehe also discussed Mathet's γ (dropped — hyperparameter-sensitive and implementation-inconsistent, §6.1 / Appendix A.1) and Intersection-over-Union (Appendix A.3, Table 4 — same model ranking as F1). Only relevant if the report wants to justify why we, like Zehe, settle on exact + relaxed F1 and ignore γ/IoU.

---

## 6. Zehe reference numbers used in the draft's closing sentence

The draft (line 78) claims our best combination "exceeds not only Zehe et al.'s reported relaxed F1-score of 0.45 (with gpt-4o) for their LLM-approach, but also the relaxed F1-score of 0.68 for the ML-approach". Provenance and caveats:

- **0.45 (LLM approach, gpt-4o).** Paper Table 2, relaxed F1 (t=3) on **Test-Full**, zero-shot No-CoT prompt, model `gpt-4o-2024-08-06`. It was the paper's *best* zero-shot prompting result; the others were llama3:8b 0.13, llama3:70b 0.34, llama3.1:405b 0.34, gpt-4o-mini 0.14. Source: [`2025.naacl-long.500.md`](../../reference/2025.naacl-long.500.md) lines 248–258. Paper's verdict on zero-shot: "does not perform well overall" (§7.2).
- **0.68 (ML / BERT approach).** Paper's best supervised model overall: **GBERT-Large + Half-Stride**, relaxed F1 (t=3) = 0.68 on **Test-Full** (Table 1 / Table 4; abstract & conclusion, [`2025.naacl-long.500.md`](../../reference/2025.naacl-long.500.md) line 307). This is a *fine-tuned BERT*, not "traditional ML" — worth wording carefully; the draft calls it "ML-approach", but Zehe's number is a BERT SSC model.

**Comparability caveats (important — these numbers are not a clean head-to-head):**

- Zehe's 0.45 and 0.68 are on **Test-Full** (STSS-Test-1 dime novels + STSS-Test-2 high literature + OOD-Test Harry Potter / Hänsel und Gretel). Our 0.76 is on our **two Excel gold texts** (Gaensemagd + Kleist), which are *not* the same corpus. Different test sets → the comparison is directional, not exact. See [`PROMPTING_RESULTS_REPORT.md`](../../prompting/PROMPTING_RESULTS_REPORT.md) §4 for the full list of five differences (test set, models, prompt template, output enforcement, sampling scope).
- Same-slice anchors that are fairer to cite alongside: on **STSS-Test-2 only**, Zehe's best BERT (GBERT-Large + Half-Stride) is **0.66** (Table 1), and Zehe's *fine-tuned* Llama3:8b with CoT-List reaches **0.62** on Test-Full (Table 3). Our own STSS-Test-2 zero-shot result with a free 120B model was F1@3 = **0.830** (full stratified, 892 sentences), per [`PROMPTING_RESULTS_REPORT.md`](../../prompting/PROMPTING_RESULTS_REPORT.md) §3.2 — a different (free, non-Gemini) model line than the Gemini production choice, but useful supporting evidence that modern LLM zero-shot has moved well past the paper's 2024 gpt-4o ceiling.

---

## 7. Error profile and the "sufficient" verdict — supporting evidence

Supports the draft's judgement that results are "sufficient" and bridges to the Final Remarks over-segmentation point (out of scope, but flagged).

- **Recall is effectively perfect at tolerance 3.** Gemini + B reaches R@3 = 1.00 on both Excel texts (§4c). The model finds every real scene boundary; the failure mode is *extra* borders, not missed ones.
- **Over-prediction is the dominant error.** Raw Gemini predicts ~**2.24×** as many borders as gold on the Excel texts; weaker models over-predict far more (3–15× gold). Sources: [`EXCEL_EXPERIMENTS_COMPARISON_REPORT.md`](../../prompting/EXCEL_EXPERIMENTS_COMPARISON_REPORT.md) §1 ("~2.2× gold on the stability rerun"), [`EXCEL_FP_REDUCTION_OFAT_PLAN.md`](../../planning/EXCEL_FP_REDUCTION_OFAT_PLAN.md) Stage-1 table.
- **Many false positives are near-misses, not nonsense.** In the STSS Phase-A error tagging, every one of the winner's errors was tagged `near_correct_boundary` (off by 1–3 sentences). Source: [`PROMPTING_RESULTS_REPORT.md`](../../prompting/PROMPTING_RESULTS_REPORT.md) §6.
- **Zehe observed the same pattern (nice back-reference).** Paper §7.1, [`2025.naacl-long.500.md`](../../reference/2025.naacl-long.500.md) line 240: "the better models seem to benefit more from the tolerance. This suggests that these models frequently make good predictions that are off by some sentences, while the worse models just make completely wrong predictions." And on false positives (§7.1 / Appendix A.6): in almost all cases "there was a clear reason visible for why the model predicted a scene border … valid markers for scene changes that have been judged by the annotators as not significant enough" — i.e. the model is arguably more fine-grained, which matches the draft's Final-Remarks point B.
- **Post-processing can trade recall for precision** (bridge to Final Remarks, not for §Model Selection): `min_scene_len_3` and confidence thresholding raise precision/F1@3 without the recall loss that `min_scene_len_5` forces on texts with 1-sentence gold gaps (Kleist min gap = 1). Decision: default post-processing = confidence threshold + `min_scene_len_3`, *not* `min_scene_len_5`. Source: [`decision__postprocess-min-scene-len-3.md`](../../../research_log/decisions/decision__postprocess-min-scene-len-3.md); numbers in [`EXCEL_EXPERIMENTS_COMPARISON_REPORT.md`](../../prompting/EXCEL_EXPERIMENTS_COMPARISON_REPORT.md) §3.

---

## Appendix: quick source index

| Topic | Primary source |
|-------|----------------|
| Zehe No-CoT & CoT-List prompts | [`2025.naacl-long.500.md`](../../reference/2025.naacl-long.500.md) A.2 (lines 374–432); [`classify.py`](../../../upstream/scene-segmentation/prompting/classify.py) lines 34–51 |
| Our Family B prompt | [`src/prompts/B_zero_shot_json.txt`](../../../src/prompts/B_zero_shot_json.txt); image [`image_1.png`](Report_Automatic_Scene_Segmentation_assets/image_1.png) |
| JSON schema enforced | [`src/prompts/json_schema_label_reason.json`](../../../src/prompts/json_schema_label_reason.json) |
| Phase A family sweep | [`2026-05-15__…__stss2-phase-a-family-sweep-nemotron.md`](../../../research_log/runs/2026-05-15__prompting__experiment__stss2-phase-a-family-sweep-nemotron.md); [`PROMPTING_RESULTS_REPORT.md`](../../prompting/PROMPTING_RESULTS_REPORT.md) |
| Model comparison + reasoning delta | [`EXCEL_EXPERIMENTS_COMPARISON_REPORT.md`](../../prompting/EXCEL_EXPERIMENTS_COMPARISON_REPORT.md); [`EXCEL_PROMPTING_2026-05-30_REPORT.md`](../../prompting/EXCEL_PROMPTING_2026-05-30_REPORT.md) |
| Run artefacts (summary/config/command) | `outputs/runs/prompting/2026-05-31-excel-gemini-reasoning-on/`, `…/2026-05-30-excel-3model-sweep/`, `…/2026-05-30-excel-opus4/` |
| Metric definitions | [`2025.naacl-long.500.md`](../../reference/2025.naacl-long.500.md) §6.1 (lines 157–171); scorer [`run_prompting_stratified.py`](../../../src/runners/run_prompting_stratified.py) lines 705–742 |
| Zehe reference numbers (0.45, 0.68) | [`2025.naacl-long.500.md`](../../reference/2025.naacl-long.500.md) Table 1 / Table 2 / conclusion |
| Reasoning-mode mechanics | [`NEMOTRON_MEMO.md`](../../prompting/NEMOTRON_MEMO.md); [`EXCEL_PROMPTING_2026-05-30_REPORT.md`](../../prompting/EXCEL_PROMPTING_2026-05-30_REPORT.md) §H |
| Context construction | [`context_builder.py`](../../../src/core/context_builder.py); [`classify.py`](../../../upstream/scene-segmentation/prompting/classify.py) lines 93–111 & 25 |
| Pilot-vs-full + reasoning-off decision | [`decision__pilot-vs-full-and-reasoning-off-candidate.md`](../../../research_log/decisions/decision__pilot-vs-full-and-reasoning-off-candidate.md) |
| Over-segmentation / post-processing | [`decision__postprocess-min-scene-len-3.md`](../../../research_log/decisions/decision__postprocess-min-scene-len-3.md) |
