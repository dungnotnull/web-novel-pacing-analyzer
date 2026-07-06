"""chapter_pacing.py — scene-sequel & try/fail cycle pacing scoring.

Approximates scene-sequel rhythm by measuring paragraph-level pacing variety
and detecting try/fail cycle beats (action chapters vs reflection chapters).
Grounded in the scene-sequel & try/fail cycle pacing-analysis framework.
"""
from __future__ import annotations

from typing import List, Tuple

from .schemas import Chapter
from .text_stats import paragraph_count, sentence_count, avg_sentence_length


def pacing_rhythm_score(chapters: List[Chapter]) -> Tuple[float, List[str]]:
    findings: List[str] = []
    if not chapters:
        return 0.0, ["No chapters supplied."]
    n = len(chapters)
    # variety of avg sentence length across chapters -> scene/sequel rhythm
    asls = [avg_sentence_length(ch.text) for ch in chapters]
    mean = sum(asls) / n
    var = sum((a - mean) ** 2 for a in asls) / n
    cv = (var ** 0.5) / mean if mean else 0.0
    # a healthy rhythm has moderate variety (not monotonous, not chaotic)
    if cv < 0.08:
        rhythm_pts = 55.0
        findings.append("Sentence-length rhythm is monotonous across chapters; vary scene/sequel pacing.")
    elif cv > 0.6:
        rhythm_pts = 65.0
        findings.append("Sentence-length rhythm is erratic across chapters; even out pacing extremes.")
    else:
        rhythm_pts = 90.0
        findings.append("Sentence-length rhythm shows healthy scene/sequel variety.")

    # paragraph density: serialized chapters favor shorter, scannable paragraphs.
    pdens = []
    for ch in chapters:
        pp = paragraph_count(ch.text)
        pdens.append(pp / max(1, ch.word_count / 100.0))
    mean_pd = sum(pdens) / n
    para_pts = max(0.0, 100.0 - abs(mean_pd - 1.5) * 60.0)
    if mean_pd < 0.8:
        findings.append("Low paragraph density (long blocks); web readers prefer scannable paragraphs.")

    # try/fail cycle proxy: alternation between high and low action tension
    # chapters is detected by tension-curve module; here we proxy via
    # sentence count variance as a substitute for scene density shifts.
    scs = [sentence_count(ch.text) for ch in chapters]
    if n >= 2:
        smean = sum(scs) / n
        svar = sum((s - smean) ** 2 for s in scs) / n
        scv = (svar ** 0.5) / smean if smean else 0.0
        sc_pts = max(0.0, 100.0 - abs(scv - 0.25) * 200.0)
    else:
        sc_pts = 80.0

    score = round(0.4 * rhythm_pts + 0.3 * para_pts + 0.3 * sc_pts, 1)
    return score, findings


def act_pacing_score(chapters: List[Chapter], genre: str, beat_positions: dict) -> Tuple[float, List[str]]:
    """Three-Act pacing: inciting catalyst placement + act-1 length vs genre."""
    from .genre_data import GENRE_PROFILES
    profile = GENRE_PROFILES[genre]
    findings: List[str] = []
    inc = beat_positions.get("inciting", -1.0)
    if inc < 0:
        pts = 50.0
        findings.append("No inciting incident detected; act-1 pacing cannot be validated.")
    else:
        target = float(profile["inciting_incident_by_pct"])
        delta = abs(inc - target)
        pts = max(0.0, 100.0 - delta * 300.0)
        if inc > target + 0.10:
            findings.append("Act 1 is slow; inciting incident delayed to {:.0%}.".format(inc))
        elif inc < target - 0.10:
            findings.append("Act 1 is very fast; inciting incident at {:.0%} may shortchange setup.".format(inc))
        else:
            findings.append("Act-1 pacing appropriate; inciting incident at {:.0%}.".format(inc))
    return round(pts, 1), findings
