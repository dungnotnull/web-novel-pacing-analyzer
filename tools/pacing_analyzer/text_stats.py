"""text_stats.py — deterministic, language-agnostic text statistics.

Pure functions over a chapter's text. No model, no network. Used by the
hook-density, tension-curve and structure-scorer modules.
"""
from __future__ import annotations

import re
from typing import Dict, List

from .schemas import Chapter
from .genre_data import (
    BEAT_MARKERS,
    CLIFFHANGER_MARKERS,
    HOOK_MARKERS,
    OPEN_QUESTION_MARKERS,
    TENSION_LEXICON,
    INCITING_MARKERS,
    MIDPOINT_MARKERS,
    CLIMAX_MARKERS,
    RESOLUTION_MARKERS,
)

_SENTENCE_SPLIT = re.compile(r"[.!?。！？]+")
_PARAGRAPH_SPLIT = re.compile(r"\n{2,}")


def word_count(text: str) -> int:
    return len(text.split())


def char_count(text: str) -> int:
    return len(text)


def sentence_count(text: str) -> int:
    parts = [p for p in _SENTENCE_SPLIT.split(text) if p.strip()]
    return max(1, len(parts))


def paragraph_count(text: str) -> int:
    parts = [p for p in _PARAGRAPH_SPLIT.split(text) if p.strip()]
    return max(1, len(parts))


def avg_sentence_length(text: str) -> float:
    wc = word_count(text)
    sc = sentence_count(text)
    return wc / sc


def chapter_stats(ch: Chapter) -> Dict[str, float]:
    """Aggregate per-chapter statistics used downstream."""
    text = ch.text or ""
    return {
        "index": ch.index,
        "title": ch.title,
        "word_count": float(ch.word_count or word_count(text)),
        "char_count": float(char_count(text)),
        "sentence_count": float(sentence_count(text)),
        "paragraph_count": float(paragraph_count(text)),
        "avg_sentence_length": float(avg_sentence_length(text)),
    }


def lower_tokens(text: str) -> List[str]:
    return re.findall(r"[a-z0-9']+", text.lower()) or text.lower().split()


def marker_hits(text: str, markers: List[str]) -> List[str]:
    low = text.lower()
    return [m for m in markers if m in low]


def marker_count(text: str, markers: List[str]) -> int:
    low = text.lower()
    return sum(1 for m in markers if m in low)


def tension_score(text: str) -> float:
    """Lexicon-based tension in 0..1.

    Derived from the page-turner tension-curve framework: density of
    tension-laden words minus calm-laden words, normalized and clamped.
    """
    tokens = lower_tokens(text)
    if not tokens:
        return 0.0
    score = 0.0
    hits = 0
    for tok in tokens:
        if tok in TENSION_LEXICON:
            score += TENSION_LEXICON[tok]
            hits += 1
    # normalize by square root of length to avoid long-chapter bias
    norm = score / (len(tokens) ** 0.5) if tokens else 0.0
    # map to 0..1 with a saturating transform; mild baseline so non-tense
    # prose still produces a readable curve rather than flat zero.
    mapped = 0.25 + 1.6 * norm
    return max(0.0, min(1.0, mapped))


def hook_strength(text: str) -> float:
    """Hook strength in 0..1 from opening hook markers + open questions."""
    low = text.lower()
    opening = low[:300]
    head_hits = sum(1 for m in HOOK_MARKERS if m in opening)
    q_hits = sum(1 for m in OPEN_QUESTION_MARKERS if m in opening)
    body_q = low.count("?")
    score = 0.15 * head_hits + 0.05 * q_hits + 0.02 * body_q
    return max(0.0, min(1.0, score))


def cliffhanger_present(text: str) -> bool:
    tail = text[-400:].lower()
    return any(m in tail for m in CLIFFHANGER_MARKERS)


def open_question_density(text: str) -> float:
    low = text.lower()
    hits = sum(1 for m in OPEN_QUESTION_MARKERS if m in low)
    qs = low.count("?")
    wc = max(1, word_count(text))
    return min(1.0, (hits * 0.05) + (qs / wc) * 50.0)


def beat_map(chapters: List[Chapter]) -> Dict[str, List[int]]:
    """Map each Save-the-Cat beat to the chapters where its markers appear."""
    out: Dict[str, List[int]] = {b: [] for b in BEAT_MARKERS}
    for ch in chapters:
        low = ch.text.lower()
        for beat, markers in BEAT_MARKERS.items():
            if any(m in low for m in markers):
                out[beat].append(ch.index)
    return out


def first_marker_chapter(chapters: List[Chapter], markers: List[str]) -> int:
    for ch in chapters:
        low = ch.text.lower()
        if any(m in low for m in markers):
            return ch.index
    return -1


def inciting_chapter(chapters: List[Chapter]) -> int:
    return first_marker_chapter(chapters, INCITING_MARKERS)


def midpoint_chapter(chapters: List[Chapter]) -> int:
    return first_marker_chapter(chapters, MIDPOINT_MARKERS)


def climax_chapter(chapters: List[Chapter]) -> int:
    return first_marker_chapter(chapters, CLIMAX_MARKERS)


def resolution_chapter(chapters: List[Chapter]) -> int:
    return first_marker_chapter(chapters, RESOLUTION_MARKERS)
