"""trope_matcher.py — genre-trope reader-expectation matching.

Checks the manuscript against the genre's expected trope set and reader-
expectation conventions. Produces a trope-fit score and per-trope coverage.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

from .genre_data import GENRE_PROFILES
from .schemas import Chapter
from .text_stats import lower_tokens


def _trope_token(trope: str) -> str:
    return trope.replace("_", " ")


def trope_coverage(chapters: List[Chapter], genre: str) -> Tuple[float, Dict[str, bool], List[str]]:
    """Return coverage ratio, per-trope presence, and missing tropes."""
    profile = GENRE_PROFILES[genre]
    tropes = list(profile["expected_tropes"])
    if not chapters:
        return 0.0, {t: False for t in tropes}, tropes
    corpus_tokens = set()
    for ch in chapters:
        corpus_tokens.update(lower_tokens(ch.text))
    # also check substring of joined text for multi-word tropes
    joined = " ".join(lower_tokens(" ".join(ch.text for ch in chapters)))
    presence = {}
    for t in tropes:
        token = _trope_token(t)
        if " " in token:
            presence[t] = token in joined
        else:
            presence[t] = token in corpus_tokens or token in joined
    missing = [t for t, present in presence.items() if not present]
    coverage = 1.0 - (len(missing) / max(1, len(tropes)))
    return coverage, presence, missing


def trope_fit_score(chapters: List[Chapter], genre: str) -> Tuple[float, List[str], Dict[str, bool], List[str]]:
    coverage, presence, missing = trope_coverage(chapters, genre)
    findings: List[str] = []
    profile = GENRE_PROFILES[genre]
    findings.append(
        "Genre '{g}' expects {n} reader-expectation tropes; "
        "tension driver: '{td}'.".format(g=genre, n=len(profile["expected_tropes"]),
                                         td=profile["tension_driver"])
    )
    if coverage >= 0.8:
        findings.append("Strong trope coverage ({:.0%}); reader expectations well fulfilled.".format(coverage))
    elif coverage >= 0.5:
        findings.append("Moderate trope coverage ({:.0%}); some reader expectations unmet.".format(coverage))
    else:
        findings.append("Low trope coverage ({:.0%}); risk of genre-misfit and reader drop-off.".format(coverage))
    if missing:
        findings.append("Missing tropes: {}.".format(", ".join(_trope_token(t) for t in missing[:6])))
    score = round(coverage * 100.0, 1)
    return score, findings, presence, missing
