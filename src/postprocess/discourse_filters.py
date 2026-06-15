"""Discourse-cue heuristics for border post-processing (German prose)."""

from __future__ import annotations

import re
from typing import List, Sequence

# Sentence starts that often signal a genuine scene shift
KEEP_PREFIXES = (
    r"am\s+n[aä]chsten\s+(?:tag|morgen|abend|mittag)",
    r"unterdessen",
    r"inzwischen",
    r"meanwhile",
    r"sp[aä]ter",
    r"einige\s+(?:tage|wochen|monate|jahre)\s+(?:sp[aä]ter|danach)",
    r"darauf",
    r"als\s+(?:es\s+)?(?:morgen|abend|nacht)\s+wurde",
)

# Pronouns / connectives suggesting continuation of same scene
CONTINUATION_PREFIXES = (
    r"^(?:er|sie|es|ihm|ihr|ihnen|sein|ihr|der|die|das|dem|den|des)\b",
    r"^(?:und|aber|doch|denn|also|deshalb|darum|daher|dann|noch|auch|nur)\b",
)

TEMPORAL_MARKERS = (
    r"\b(?:dann|darauf|sp[aä]ter|pl[oö]tzlich|bald|nun|jetzt|sofort|w[aä]hrend)\b",
    r"\b(?:am\s+(?:morgen|abend|tag|nachmittag|abend))\b",
    r"\b(?:des\s+(?:andern|n[aä]chsten)\s+(?:tages|morgens))\b",
)

_keep_re = re.compile("|".join(f"(?:{p})" for p in KEEP_PREFIXES), re.IGNORECASE)
_cont_re = re.compile("|".join(CONTINUATION_PREFIXES), re.IGNORECASE)
_temporal_re = re.compile("|".join(TEMPORAL_MARKERS), re.IGNORECASE)


def _sentence_starts_with(text: str, pattern: re.Pattern[str]) -> bool:
    stripped = text.strip()
    if not stripped:
        return False
    return bool(pattern.match(stripped))


def apply_discourse_filter(
    pred_labels: Sequence[str],
    sentences: Sequence[str],
) -> List[str]:
    """Drop BORDER candidates that look like within-scene continuations.

    Keeps borders when the candidate sentence has a strong scene-shift marker.
    Drops when the following sentence starts with a continuation pronoun and
    neither the candidate nor the next sentence has a temporal/place shift marker.
    """
    out = list(pred_labels)
    n = len(out)
    for i, label in enumerate(out):
        if label != "BORDER":
            continue
        sent = sentences[i] if i < len(sentences) else ""
        if _sentence_starts_with(sent, _keep_re):
            continue
        next_sent = sentences[i + 1] if i + 1 < len(sentences) else ""
        if not next_sent:
            continue
        has_temporal = bool(_temporal_re.search(sent)) or bool(_temporal_re.search(next_sent))
        if has_temporal:
            continue
        if _sentence_starts_with(next_sent, _cont_re):
            out[i] = "NOBORDER"
    return out
