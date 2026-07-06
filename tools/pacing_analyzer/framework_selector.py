"""framework_selector.py — sub-evaluation-framework-selector implementation.

Identifies genre, length format, and the structural model(s) to evaluate the
manuscript against. Produces a FrameworkSelection consumed by the scoring
engine.
"""
from __future__ import annotations

from typing import List

from .genre_data import GENRE_PROFILES
from .schemas import AnalysisRequest, FrameworkSelection, FRAMEWORKS, DIMENSION_FRAMEWORK


def normalize_genre(genre: str) -> str:
    g = (genre or "").strip().lower().replace("-", "_").replace(" ", "_")
    if g in GENRE_PROFILES:
        return g
    aliases = {
        "lit_rpg": "litrpg", "lit-rpg": "litrpg", "lit_rpg_adventure": "litrpg",
        "progression_fantasy": "litrpg", "cultivation": "xianxia",
        "wuxia": "xianxia", "love_story": "romance", "fantasy_epic": "fantasy",
        "science_fiction": "scifi", "sci_fi": "scifi", "sf": "scifi",
        "detective": "mystery", "cozy_mystery": "mystery",
        "slice_of_life": "slice_of_life", "sol": "slice_of_life",
    }
    return aliases.get(g, "general")


def select_frameworks(genre: str) -> List[str]:
    """Pick the governing framework ids for a genre.

    Every manuscript is scored against the core structural + pacing + retention
    frameworks; trope-driven genres add the trope-convention framework.
    """
    core = ["save_the_cat", "three_act", "scene_sequel", "hook_density",
            "tension_curve", "retention_psych"]
    if genre == "slice_of_life":
        # Kishōtenketsu cadence dominates slice-of-life serialized arcs.
        core = ["kishotenketsu", "scene_sequel", "hook_density", "retention_psych"]
    elif genre in ("litrpg", "xianxia", "romance", "fantasy", "scifi",
                   "thriller", "mystery", "horror"):
        core.append("trope_convention")
        core.append("kishotenketsu")
    else:
        if "kishotenketsu" not in core:
            core.append("kishotenketsu")
        core.append("trope_convention")
    # de-dup, preserve order
    seen, out = set(), []
    for f in core:
        if f in FRAMEWORKS and f not in seen:
            seen.add(f)
            out.append(f)
    return out


def _scope_in_out(genre: str, length_format: str) -> tuple:
    scope_in = [
        "Structural & chapter-level pacing analysis",
        "Hook density and cliffhanger coverage",
        "Tension-curve mapping across chapters",
        "Genre-trope reader-expectation fit",
        "Retention-risk flagging with prioritized fixes",
    ]
    scope_out = [
        "Line-editing, prose style, and copyediting",
        "Market pricing / monetization advice",
        "Plagiarism or copyright-legal review",
        "Translation quality assessment",
    ]
    if length_format == "print":
        scope_in.append("Print-length act structure (Three-Act)")
        scope_out.append("Serialized-release scheduling (print mode)")
    return scope_in, scope_out


def run(request: AnalysisRequest) -> FrameworkSelection:
    genre = normalize_genre(request.genre)
    profile = GENRE_PROFILES[genre]
    frameworks = select_frameworks(genre)
    scope_in, scope_out = _scope_in_out(genre, request.length_format)

    rationale = (
        "Genre '{g}' selected; scoring against {n} named frameworks. "
        "Length format '{lf}' controls cadence targets (target ~{wc} words/chapter, "
        "~{arc} chapters/arc, cliffhanger density {cd:.0%})."
    ).format(
        g=genre, n=len(frameworks), lf=request.length_format,
        wc=profile["target_word_count"], arc=profile["cadence_chapters_per_arc"],
        cd=profile["cliffhanger_density"],
    )

    assumptions = [
        "Manuscript language is English or translatable by shared markers.",
        "Chapters are supplied in reading order.",
        "Author intent aligns with genre reader expectations.",
        "Deterministic heuristics used; knowledge base may be stale.",
    ]
    evidence = [
        "GENRE_PROFILES[%s] (curated reader-expectation conventions)" % genre,
        "DIMENSION_FRAMEWORK mapping (each score cites a named framework)",
    ]

    return FrameworkSelection(
        genre=genre,
        length_format=request.length_format,
        frameworks=frameworks,
        rationale=rationale,
        assumptions=assumptions,
        scope_in=scope_in,
        scope_out=scope_out,
        evidence=evidence,
    )


def dimension_framework(dimension: str) -> tuple:
    """Return (framework_id, framework_name) for a scoring dimension."""
    fid = DIMENSION_FRAMEWORK.get(dimension, "tension_curve")
    return fid, FRAMEWORKS[fid]
