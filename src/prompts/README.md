# Prompt Template Pack (A-J)

This folder contains reusable prompt templates for scene/event boundary
experiments. Templates are text-first modules intended for later integration
into `src/run_prompting_baseline.py` and `src/run_prompting_stratified.py`.

## Naming

- `A_...` through `J_...` map to the experiment families in `docs/PROJECT_PLAN.md`
- `registry.json` is the machine-readable index

## Shared placeholders

Most templates use:

- `{left_context}`
- `{target_sentence}`
- `{right_context}`

Chunk-oriented templates additionally use:

- `{chunk_sentences}` (numbered lines)

Few-shot templates include slots:

- `{few_shot_examples}` (already formatted examples block)

## Output contracts

- JSON templates must return valid JSON only
- classification label enum is always `BORDER` or `NOBORDER`
- chunk localization uses sentence id or `NONE`

## Decode defaults for sweeps

- `temperature=0`
- fixed `seed` when supported
- short `max_tokens`
- `response_format={"type":"json_object"}` where supported

