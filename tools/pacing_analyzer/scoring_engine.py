"""scoring_engine.py — sub-scoring-engine implementation.

Orchestrates the multi-dimensional score against the named frameworks selected
by the framework selector. Each dimension cites its governing framework and an
evidence tier. Produces dimension scores, the per-chapter tension curve, and
per-chapter retention-risk flags.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

from .arc_cadence import cadence_score
from .chapter_pacing import act_pacing_score, pacing_rhythm_score
from .genre_data import GENRE_PROFILES
from .hook_density import hook_density_score
from .schemas import (
    AnalysisRequest,
    ChapterRisk,
    DimensionScore,
    FrameworkSelection,
    TensionPoint,
)
from .structure_scorer import structure_score
from .tension_curve import tension_curve_score
from .trope_matcher import trope_fit_score


def _retention_risk(chapters, profile, curve, hook_stats) -> List[ChapterRisk]:
    """Flag chapters where retention risk is elevated.

    Mid-arc sag is detected relative to each chapter's neighbours (a tension
    drop relative to surrounding chapters), which is the actual retention
    signal for serialized fiction rather than an absolute calm threshold.
    """
    risks = []
    expected_cd = float(profile["cliffhanger_density"])
    must_by = int(profile["hook_must_appear_by_chapter"])
    n = len(chapters)
    tensions = [pt.tension for pt in curve]
    for i, (ch, pt, hs) in enumerate(zip(chapters, curve, hook_stats)):
        reasons = []
        risk = "low"
        # absolute low-tension baseline
        if pt.tension < 0.28:
            reasons.append("low tension ({:.2f})".format(pt.tension))
            risk = "medium"
        # missing/weak opening hook
        if i == 0 and hs["hook_strength"] < 0.10:
            reasons.append("missing opening hook in chapter 1")
            risk = "high"
        if i + 1 == must_by and hs["hook_strength"] < 0.15:
            reasons.append("weak hook at mandatory-hook chapter %d" % must_by)
            risk = "high"
        # missing cliffhanger where genre expects one
        if not pt.cliffhanger and expected_cd > 0.5 and i < n - 1:
            reasons.append("no cliffhanger where genre expects one")
            if risk == "low":
                risk = "medium"
        # relative mid-arc sag (tension drop vs neighbours)
        if n >= 5 and (n // 3) <= i < (2 * n // 3):
            neighbours = []
            if i > 0:
                neighbours.append(tensions[i - 1])
            if i < n - 1:
                neighbours.append(tensions[i + 1])
            nb_avg = sum(neighbours) / len(neighbours) if neighbours else tensions[i]
            sag_drop = nb_avg - tensions[i]
            if sag_drop > 0.10 and tensions[i] < 0.45:
                reasons.append(
                    "mid-arc sag (tension {t:.2f} vs neighbours {n:.2f})".format(
                        t=tensions[i], n=nb_avg))
                risk = "high"
        fix = _suggest_fix(reasons, profile, pt.cliffhanger)
        if reasons:
            risks.append(ChapterRisk(chapter_index=ch.index, retention_risk=risk,
                                     reasons=reasons, suggested_fix=fix))
    return risks


def _suggest_fix(reasons, profile, has_cliff) -> str:
    if any("opening hook" in r or "weak hook" in r for r in reasons):
        return "Insert a strong opening hook (sudden shift / open question / withheld truth)."
    if any("cliffhanger" in r for r in reasons):
        return "Add a chapter-ending cliffhanger or open question to carry the reader forward."
    if any("mid-arc sag" in r for r in reasons):
        return "Inject a midpoint reversal or raise stakes to lift mid-arc tension."
    if any("low tension" in r for r in reasons):
        return "Raise scene stakes or add a tension-laden beat (threat, deadline, conflict)."
    return "Review chapter against genre reader-expectation conventions."


def score(request: AnalysisRequest, selection: FrameworkSelection) -> Tuple[
    List[DimensionScore], List[TensionPoint], List[ChapterRisk], Dict[str, List[str]]
]:
    chapters = request.chapters
    genre = selection.genre
    profile = GENRE_PROFILES[genre]
    findings: Dict[str, List[str]] = {
        "strengths": [], "risks": [], "gaps": [],
    }

    # --- structure (Save the Cat) ---
    s_score, s_findings, beat_map, beat_pos = structure_score(chapters, genre)
    struct_dim = DimensionScore(
        dimension="structure",
        framework_id="save_the_cat",
        framework_name="Save the Cat! Beat Sheet (Blake Snyder)",
        score=s_score, weight=0.20,
        findings=s_findings,
        evidence=["structure_scorer.beat_map", "GENRE_PROFILES[%s].inciting_incident_by_pct" % genre],
        evidence_tier="internal_heuristic",
    )

    # --- act pacing (Three-Act) ---
    a_score, a_findings = act_pacing_score(chapters, genre, beat_pos)
    act_dim = DimensionScore(
        dimension="act_pacing",
        framework_id="three_act",
        framework_name="Three-Act Structure (Syd Field / Aristotle)",
        score=a_score, weight=0.10,
        findings=a_findings,
        evidence=["chapter_pacing.act_pacing_score", "beat_positions"],
        evidence_tier="internal_heuristic",
    )

    # --- chapter pacing (Scene-Sequel) ---
    cp_score, cp_findings = pacing_rhythm_score(chapters)
    cp_dim = DimensionScore(
        dimension="chapter_pacing",
        framework_id="scene_sequel",
        framework_name="Scene-Sequel & Try/Fail Cycle (Dwight Swain)",
        score=cp_score, weight=0.15,
        findings=cp_findings,
        evidence=["chapter_pacing.pacing_rhythm_score"],
        evidence_tier="internal_heuristic",
    )

    # --- hook density ---
    h_score, h_findings, hook_stats = hook_density_score(chapters, genre)
    hook_dim = DimensionScore(
        dimension="hook_density",
        framework_id="hook_density",
        framework_name="Hook Density & Chapter Cliffhanger (serialized-fiction craft)",
        score=h_score, weight=0.20,
        findings=h_findings,
        evidence=["hook_density.per_chapter_hook", "GENRE_PROFILES[%s].cliffhanger_density" % genre],
        evidence_tier="internal_heuristic",
    )

    # --- tension curve ---
    t_score, t_findings, curve = tension_curve_score(chapters)
    tension_dim = DimensionScore(
        dimension="tension_curve",
        framework_id="tension_curve",
        framework_name="Page-Turner Tension Curve (reader-engagement models)",
        score=t_score, weight=0.15,
        findings=t_findings,
        evidence=["tension_curve.build_curve", "tension_lexicon"],
        evidence_tier="internal_heuristic",
    )

    # --- arc cadence (Kishōtenketsu) ---
    c_score, c_findings = cadence_score(chapters, genre)
    cad_dim = DimensionScore(
        dimension="arc_cadence",
        framework_id="kishotenketsu",
        framework_name="Kishōtenketsu & web-serial arc/chapter cadence",
        score=c_score, weight=0.10,
        findings=c_findings,
        evidence=["arc_cadence.cadence_score", "GENRE_PROFILES[%s].target_word_count" % genre],
        evidence_tier="internal_heuristic",
    )

    # --- trope fit (Genre-Trope Conventions) ---
    tf_score, tf_findings, presence, missing = trope_fit_score(chapters, genre)
    trope_dim = DimensionScore(
        dimension="trope_fit",
        framework_id="trope_convention",
        framework_name="Genre-Trope Conventions & reader-expectation fulfillment",
        score=tf_score, weight=0.10,
        findings=tf_findings,
        evidence=["trope_matcher.trope_coverage", "GENRE_PROFILES[%s].expected_tropes" % genre],
        evidence_tier="internal_heuristic",
    )

    # --- retention (Reader-Retention Psychology), composite of risk flags ---
    risks = _retention_risk(chapters, profile, curve, hook_stats)
    high = sum(1 for r in risks if r.retention_risk == "high")
    med = sum(1 for r in risks if r.retention_risk == "medium")
    base = 100.0 - (high * 12.0 + med * 5.0)
    retention_score = max(0.0, base)
    r_findings = []
    if high:
        r_findings.append("%d chapter(s) at high retention risk." % high)
    if med:
        r_findings.append("%d chapter(s) at medium retention risk." % med)
    if not risks:
        r_findings.append("No elevated retention-risk chapters detected.")
    retention_dim = DimensionScore(
        dimension="retention",
        framework_id="retention_psych",
        framework_name="Reader-Retention Psychology (curiosity gaps, variable reward)",
        score=round(retention_score, 1), weight=0.15,
        findings=r_findings,
        evidence=["scoring_engine._retention_risk", "hook_stats", "tension_curve"],
        evidence_tier="internal_heuristic",
    )

    dimensions = [struct_dim, act_dim, cp_dim, hook_dim, tension_dim,
                  cad_dim, trope_dim, retention_dim]

    # aggregate findings into strengths/risks/gaps
    all_f = []
    for d in dimensions:
        all_f.extend(d.findings)
    for f in all_f:
        if any(k in f.lower() for k in ("strong", "well", "aligns", "healthy", "appropriate", "no significant")):
            findings["strengths"].append(f)
        elif any(k in f.lower() for k in ("risk", "low", "missing", "sag", "slow", "declining", "weak", "monotonous", "erratic", "fatigue", "misfit")):
            findings["risks"].append(f)
        else:
            findings["gaps"].append(f)

    return dimensions, curve, risks, findings


def headline(dimensions: List[DimensionScore]) -> float:
    total_w = sum(d.weight for d in dimensions)
    if total_w == 0:
        return 0.0
    return round(sum(d.score * d.weight for d in dimensions) / total_w, 1)



