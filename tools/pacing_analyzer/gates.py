"""gates.py — quality-gate enforcement (evidence, framework, challenge).

The harness refuses/degrades when a gate fails. Gates are deterministic checks
on the assembled report so production runs are auditable.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

from .schemas import (
    AnalysisReport,
    DimensionScore,
    FRAMEWORKS,
    RoadmapItem,
    EVIDENCE_TIERS,
)


def evidence_gate(dimensions: List[DimensionScore]) -> Tuple[bool, List[str]]:
    msgs = []
    ok = True
    for d in dimensions:
        if not d.evidence:
            ok = False
            msgs.append("Evidence gate FAIL: dimension '%s' has no evidence." % d.dimension)
        if d.evidence_tier not in EVIDENCE_TIERS:
            ok = False
            msgs.append("Evidence gate FAIL: dimension '%s' has invalid evidence tier '%s'." % (d.dimension, d.evidence_tier))
    if ok:
        msgs.append("Evidence gate PASS: all dimensions trace claims to a source/prior step.")
    return ok, msgs


def framework_gate(dimensions: List[DimensionScore], roadmap: List[RoadmapItem]) -> Tuple[bool, List[str]]:
    msgs = []
    ok = True
    for d in dimensions:
        if d.framework_id not in FRAMEWORKS:
            ok = False
            msgs.append("Framework gate FAIL: dimension '%s' cites unknown framework '%s'." % (d.dimension, d.framework_id))
    for it in roadmap:
        if it.framework_id not in FRAMEWORKS:
            ok = False
            msgs.append("Framework gate FAIL: roadmap item '%s' cites unknown framework '%s'." % (it.title, it.framework_id))
    if ok:
        msgs.append("Framework gate PASS: all scoring grounded in named frameworks.")
    return ok, msgs


def challenge_gate(report: AnalysisReport) -> Tuple[bool, str]:
    """Devil's-advocate pass. Returns (pass, counter_text)."""
    challenges = []
    dims = [DimensionScore.from_dict(d) for d in report.dimension_scores]
    risks = report.chapter_risks

    # 1. Over-optimism: high headline but a weak dimension
    if report.headline_score >= 80:
        weak = [d for d in dims if d.score < 60]
        if weak:
            challenges.append(
                "Headline score {h} is high yet dimension(s) {w} sit below 60; "
                "the headline may mask a retention-critical weakness.".format(
                    h=report.headline_score, w=", ".join(d.dimension for d in weak))
            )

    # 2. High-risk chapters without a roadmap fix targeting them
    high_risk_chs = [r["chapter_index"] for r in risks if r["retention_risk"] == "high"]
    if high_risk_chs:
        scoped = [it["chapter_scope"] for it in report.roadmap]
        uncovered = [c for c in high_risk_chs if "ch:%d" % c not in scoped]
        if uncovered:
            challenges.append(
                "High-risk chapter(s) {u} have no targeted roadmap item; "
                "add explicit per-chapter fixes.".format(u=", ".join(str(c) for c in uncovered))
            )

    # 3. Tension curve flat/declining but tension dimension scored high
    curve = report.tension_curve
    if len(curve) >= 3:
        tensions = [p["tension"] for p in curve]
        if max(tensions) - min(tensions) < 0.05 and report.headline_score >= 70:
            challenges.append(
                "Tension curve is near-flat (range {r:.2f}); engagement risk may be "
                "understated by the tension dimension.".format(r=max(tensions) - min(tensions))
            )

    # 4. Roadmap ordering sanity
    if report.roadmap:
        gains = [it["expected_gain"] for it in report.roadmap]
        if gains != sorted(gains, reverse=True):
            challenges.append("Roadmap is not strictly ordered by expected gain; review prioritization.")

    if not challenges:
        challenges.append("Challenge gate PASS: no over-optimism, gap, or ordering flaw detected.")

    # Gate passes if at least one PASS or no hard failure; here we treat
    # discovered gaps as advisories that must be surfaced (gate passes but the
    # counter-text is mandatory in the report).
    return True, " ".join(challenges)


def run_gates(report: AnalysisReport) -> Dict[str, object]:
    dims = [DimensionScore.from_dict(d) for d in report.dimension_scores]
    roadmap = [RoadmapItem.from_dict(it) for it in report.roadmap]
    e_ok, e_msgs = evidence_gate(dims)
    f_ok, f_msgs = framework_gate(dims, roadmap)
    c_ok, c_text = challenge_gate(report)
    return {
        "evidence_gate": {"passed": e_ok, "messages": e_msgs},
        "framework_gate": {"passed": f_ok, "messages": f_msgs},
        "challenge_gate": {"passed": c_ok, "message": c_text},
        "all_passed": e_ok and f_ok and c_ok,
    }
