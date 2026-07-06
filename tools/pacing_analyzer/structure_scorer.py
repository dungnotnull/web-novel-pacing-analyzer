"""structure_scorer.py — Three-Act / Save-the-Cat beat structure scoring.

Maps detected beats onto the manuscript's normalized progress and scores how
well the structural spine matches the expected beat positions for the genre's
inciting-incident threshold. Pure heuristic, fully deterministic.
"""
from __future__ import annotations

from typing import Dict, List

from .genre_data import GENRE_PROFILES
from .schemas import Chapter
from .text_stats import (
    beat_map,
    inciting_chapter,
    midpoint_chapter,
    climax_chapter,
    resolution_chapter,
)


def beat_positions(chapters: List[Chapter]) -> Dict[str, float]:
    """Return normalized position (0..1) of each detected beat, or -1."""
    n = len(chapters)
    if n == 0:
        return {b: -1.0 for b in ("inciting", "midpoint", "climax", "resolution")}
    first = chapters[0].index
    span = max(1, (chapters[-1].index - first))
    out: Dict[str, float] = {}
    inc = inciting_chapter(chapters)
    mid = midpoint_chapter(chapters)
    cla = climax_chapter(chapters)
    res = resolution_chapter(chapters)

    def pos(idx: int) -> float:
        return -1.0 if idx < 0 else (idx - first) / span

    out["inciting"] = pos(inc)
    out["midpoint"] = pos(mid)
    out["climax"] = pos(cla)
    out["resolution"] = pos(res)
    return out


def structure_score(chapters: List[Chapter], genre: str) -> tuple:
    """Score structural spine alignment (0..100) + findings + beat map.

    Returns (score, findings_list, beat_map_dict, beat_positions_dict).
    """
    profile = GENRE_PROFILES[genre]
    n = len(chapters)
    bm = beat_map(chapters)
    bp = beat_positions(chapters)
    findings: List[str] = []

    expected_inc = float(profile["inciting_incident_by_pct"])
    inc_pts = 100.0
    if n >= 3:
        if bp["inciting"] < 0:
            inc_pts = 40.0
            findings.append(
                "No explicit inciting-incident beat detected; serialized hooks "
                "need a catalyst within the first {:.0%} of chapters.".format(expected_inc)
            )
        else:
            delta = abs(bp["inciting"] - expected_inc)
            inc_pts = max(0.0, 100.0 - delta * 300.0)
            if delta > 0.15:
                findings.append(
                    "Inciting incident lands at {:.0%} (expected ~{:.0%}); "
                    "consider front-loading the catalyst.".format(bp["inciting"], expected_inc)
                )
            else:
                findings.append(
                    "Inciting incident well-placed at {:.0%}.".format(bp["inciting"])
                )
    else:
        inc_pts = 70.0
        findings.append("Sample too small for full structural analysis; scoring on hook presence only.")

    mid_pts = 100.0
    if n >= 4 and bp["midpoint"] < 0:
        mid_pts = 55.0
        findings.append("No clear midpoint reversal beat detected; mid-arc sag risk.")
    elif bp["midpoint"] >= 0:
        ideal = 0.5
        delta = abs(bp["midpoint"] - ideal)
        mid_pts = max(0.0, 100.0 - delta * 250.0)
        findings.append("Midpoint reversal detected at {:.0%}.".format(bp["midpoint"]))

    cla_pts = 100.0
    if n >= 5 and bp["climax"] < 0:
        cla_pts = 60.0
        findings.append("No explicit climax beat detected; verify rising-action payoff.")
    elif bp["climax"] >= 0:
        if bp["climax"] < 0.6:
            cla_pts = 70.0
            findings.append("Climax appears early ({:.0%}); consider extending rising tension.".format(bp["climax"]))
        else:
            findings.append("Climax detected near the end ({:.0%}).".format(bp["climax"]))

    res_pts = 100.0
    if n >= 5 and bp["resolution"] < 0:
        res_pts = 70.0
        findings.append("No explicit resolution beat; serialized fiction may intentionally defer, but a payoff beat aids retention.")

    weights = {"inciting": 0.4, "midpoint": 0.3, "climax": 0.2, "resolution": 0.1}
    raw = (inc_pts * weights["inciting"] + mid_pts * weights["midpoint"]
           + cla_pts * weights["climax"] + res_pts * weights["resolution"])
    score = round(raw, 1)
    return score, findings, bm, bp
