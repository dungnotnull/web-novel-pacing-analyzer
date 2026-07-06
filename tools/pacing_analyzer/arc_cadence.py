"""arc_cadence.py — Kishōtenketsu & web-serial cadence scoring.

Scores whether chapter-length cadence and arc length match the genre's
serialized cadence targets (chapter word count, chapters-per-arc, cliffhanger
density). Implements the kishōtenketsu & web-serial arc/chapter cadence
framework.
"""
from __future__ import annotations

from typing import List, Tuple

from .genre_data import GENRE_PROFILES
from .schemas import Chapter


def cadence_score(chapters: List[Chapter], genre: str) -> Tuple[float, List[str]]:
    profile = GENRE_PROFILES[genre]
    target_wc = float(profile["target_word_count"])
    target_arc = float(profile["cadence_chapters_per_arc"])
    findings: List[str] = []
    if not chapters:
        return 0.0, ["No chapters supplied."]

    wcs = [ch.word_count for ch in chapters]
    mean_wc = sum(wcs) / len(wcs)
    # word-count adherence: penalize deviation from target.
    if mean_wc <= 0:
        wc_pts = 0.0
    else:
        dev = abs(mean_wc - target_wc) / target_wc
        wc_pts = max(0.0, 100.0 - dev * 120.0)
    if abs(mean_wc - target_wc) > target_wc * 0.25:
        findings.append(
            "Mean chapter length {wc:.0f} words deviates from genre target {t:.0f}; "
            "consistent cadence aids serialized retention.".format(wc=mean_wc, t=target_wc)
        )
    else:
        findings.append("Chapter-length cadence (~{:.0f} words) matches genre target.".format(mean_wc))

    # consistency of chapter length (low variance is better for serials).
    if len(wcs) > 1:
        mean = sum(wcs) / len(wcs) or 1.0
        var = sum((w - mean) ** 2 for w in wcs) / len(wcs)
        cv = (var ** 0.5) / mean
        cons_pts = max(0.0, 100.0 - cv * 150.0)
        if cv > 0.4:
            findings.append("Chapter-length variance is high (CV {:.2f}); uneven cadence can cause drop-off.".format(cv))
    else:
        cons_pts = 80.0

    # arc-length fit: distance from chapter count to a multiple of target_arc.
    arc_multiple = max(1, round(len(chapters) / target_arc)) if target_arc else 1
    ideal_len = arc_multiple * target_arc
    arc_pts = 100.0 - abs(len(chapters) - ideal_len) / max(1, ideal_len) * 80.0
    arc_pts = max(0.0, arc_pts)
    findings.append(
        "Sample of {n} chapters vs ideal arc-length {ideal} (genre target {t:.0f} ch/arc).".format(
            n=len(chapters), ideal=ideal_len, t=target_arc)
    )

    score = round(0.45 * wc_pts + 0.25 * cons_pts + 0.30 * arc_pts, 1)
    return score, findings
