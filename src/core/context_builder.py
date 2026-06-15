"""Build sentence context blocks for prompting (token-budget or fixed window)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wuenlp.impl.UIMANLPStructs import UIMASentence
    from prompting.classify import Model


def build_sentence_sample_fixed_window(
    sentence: "UIMASentence",
    *,
    max_context_sentences: int,
) -> str:
    """Build context with at most ``max_context_sentences`` neighbours (excluding target).

    Expands alternately left/right like the upstream token-budget builder, but counts
    sentences instead of tokens.
    """
    context = ["<sentence>" + sentence.text + "</sentence>"]
    prev_sentence = sentence.previous
    next_sentence = sentence.next
    added = 0
    while added < max_context_sentences and (prev_sentence is not None or next_sentence is not None):
        progressed = False
        if prev_sentence is not None:
            context.insert(0, prev_sentence.text)
            prev_sentence = prev_sentence.previous
            added += 1
            progressed = True
        if added >= max_context_sentences:
            break
        if next_sentence is not None:
            context.append(next_sentence.text)
            next_sentence = next_sentence.next
            added += 1
            progressed = True
        if not progressed:
            break
    return " ".join(context)


def build_sentence_sample_for_mode(
    sentence: "UIMASentence",
    model: "Model",
    *,
    context_mode: str = "tokens",
    sentence_window: int = 32,
) -> str:
    """Dispatch to token-budget or fixed sentence-window context builder."""
    from prompting.classify import build_sentence_sample

    if context_mode == "sentences":
        # ``sentence_window`` is total neighbour cap (excluding target).
        return build_sentence_sample_fixed_window(
            sentence, max_context_sentences=max(sentence_window - 1, 0)
        )
    return build_sentence_sample(sentence, model)
