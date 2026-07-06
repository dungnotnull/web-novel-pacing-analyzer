"""hook_density.py — hook density & cliffhanger coverage scoring.

Implements the hook-density framework: per-chapter hook strength, opening-hook
presence by the genre's mandatory-hook chapter, and cliffhanger coverage vs the
genre's expected cliffhanger density.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

from .genre_data import GENRE_PROFILES
from .schemas import Chapter
from .text_stats import cliffhanger_present, hook_strength, open_question_density


def per_chapter_hook(chapters: List[Chapter]) -> List[Dict[str, float]]:
    out = []
    for ch in chapters:
        out.append({
            "index": ch.index,
            "hook_strength": round(hook_strength(ch.text), 3),
            "open_question_density": round(open_question_density(ch.text), 3),
            "cliffhanger": 1.0 if cliffhanger_present(ch.text) else 0.0,
        })
    return out


def hook_density_score(chapters: List[Chapter], genre: str) -> Tuple[float, List[str], List[Dict[str, float]]]:
    """Score (0..100) + findings + per-chapter hook stats."""
    profile = GENRE_PROFILES[genre]
    stats = per_chapter_hook(chapters)
    findings: List[str] = []
    if not chapters:
        return 0.0, ["No chapters supplied."], stats

    avg_hook = sum(s["hook_strength"] for s in stats) / len(stats)
    cliff_rate = sum(s["cliffhanger"] for s in stats) / len(stats)
    expected_cd = float(profile["cliffhanger_density"])
    must_by = int(profile["hook_must_appear_by_chapter"])

    # Hook strength target: serialized fiction rewards strong opening hooks.
    hook_pts = min(100.0, avg_hook * 220.0)
    if avg_hook < 0.25:
        findings.append(
            "Average hook strength {:.2f} is low; raise opening-hook marker density "
            "(sudden shifts, open questions, withheld truths).".format(avg_hook)
        )

    # Cliffhanger coverage vs expected density.
    cliff_pts = 100.0 - abs(cliff_rate - expected_cd) * 200.0
    cliff_pts = max(0.0, cliff_pts)
    if cliff_rate < expected_cd - 0.1:
        findings.append(
            "Cliffhanger coverage {:.0%} below genre target {:.0%}; insert end-of-chapter hooks.".format(
                cliff_rate, expected_cd)
        )
    elif cliff_rate > expected_cd + 0.2:
        findings.append(
            "Cliffhanger coverage {:.0%} exceeds target {:.0%}; risk of fatigue, vary hook types.".format(
                cliff_rate, expected_cd)
        )
    else:
        findings.append("Cliffhanger coverage {:.0%} aligns with genre target.".format(cliff_rate))

    # Mandatory early hook.
    early_pts = 100.0
    if len(chapters) >= must_by:
        early = stats[must_by - 1] if 0 < must_by <= len(stats) else stats[0]
        if early["hook_strength"] < 0.15:
            early_pts = 50.0
            findings.append(
                "Chapter {} lacks a strong opening hook; genre expects a hook by chapter {}.".format(
                    chapters[must_by - 1].index, must_by)
            )
        else:
            findings.append("Early hook present at chapter {}.".format(chapters[must_by - 1].index))

    score = round(0.4 * hook_pts + 0.35 * cliff_pts + 0.25 * early_pts, 1)
    return score, findings, stats
