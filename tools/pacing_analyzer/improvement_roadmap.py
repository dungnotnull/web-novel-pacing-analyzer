"""improvement_roadmap.py — sub-improvement-roadmap implementation.

Builds a prioritized, effort/impact-ranked roadmap from the dimension scores,
chapter risks, tension curve, and trope gaps. Every item cites the governing
framework id. Ranking: impact/effort ratio with high-impact-low-effort first.
"""
from __future__ import annotations

from typing import List, Tuple

from .schemas import DimensionScore, ChapterRisk, RoadmapItem, TensionPoint

EFFORT_RANK = {"low": 1, "medium": 2, "high": 3}
IMPACT_RANK = {"low": 1, "medium": 2, "high": 3}


def _expected_gain(dimension: DimensionScore, potential: float = 100.0) -> float:
    """Score lift available if the dimension reaches its potential."""
    return round(max(0.0, potential - dimension.score) * dimension.weight, 2)


def build_roadmap(
    dimensions: List[DimensionScore],
    risks: List[ChapterRisk],
    curve: List[TensionPoint],
    genre: str,
) -> List[RoadmapItem]:
    items: List[RoadmapItem] = []

    # Dimension-driven structural/pacing fixes.
    by_dim = {d.dimension: d for d in dimensions}

    d = by_dim.get("structure")
    if d and d.score < 80:
        items.append(RoadmapItem(
            priority=0, title="Front-load the inciting incident / beat-sheet audit",
            chapter_scope="act:1", effort="medium", impact="high",
            framework_id="save_the_cat",
            rationale=d.findings[0] if d.findings else "Restructure beats to hit expected positions.",
            expected_gain=_expected_gain(d),
        ))

    d = by_dim.get("act_pacing")
    if d and d.score < 75:
        items.append(RoadmapItem(
            priority=0, title="Restructure act-one beats to hit the catalyst sooner",
            chapter_scope="act:1", effort="medium", impact="high",
            framework_id="three_act",
            rationale=d.findings[0] if d.findings else "Tighten act-one pacing.",
            expected_gain=_expected_gain(d),
        ))

    d = by_dim.get("hook_density")
    if d and d.score < 80:
        items.append(RoadmapItem(
            priority=0, title="Raise hook density and cliffhanger coverage",
            chapter_scope="global", effort="low", impact="high",
            framework_id="hook_density",
            rationale=d.findings[0] if d.findings else "Add hooks and cliffhangers.",
            expected_gain=_expected_gain(d),
        ))

    d = by_dim.get("tension_curve")
    if d and d.score < 75:
        items.append(RoadmapItem(
            priority=0, title="Repair mid-arc sag / lift tension-curve slope",
            chapter_scope="act:2", effort="medium", impact="high",
            framework_id="tension_curve",
            rationale=d.findings[0] if d.findings else "Inject a midpoint reversal.",
            expected_gain=_expected_gain(d),
        ))

    d = by_dim.get("chapter_pacing")
    if d and d.score < 75:
        items.append(RoadmapItem(
            priority=0, title="Vary scene/sequel rhythm across chapters",
            chapter_scope="global", effort="medium", impact="medium",
            framework_id="scene_sequel",
            rationale=d.findings[0] if d.findings else "Even out pacing extremes.",
            expected_gain=_expected_gain(d),
        ))

    d = by_dim.get("arc_cadence")
    if d and d.score < 75:
        items.append(RoadmapItem(
            priority=0, title="Standardize chapter-length cadence to genre target",
            chapter_scope="global", effort="low", impact="medium",
            framework_id="kishotenketsu",
            rationale=d.findings[0] if d.findings else "Match serialized cadence.",
            expected_gain=_expected_gain(d),
        ))

    d = by_dim.get("trope_fit")
    if d and d.score < 70:
        items.append(RoadmapItem(
            priority=0, title="Add missing genre-trope reader expectations",
            chapter_scope="global", effort="medium", impact="medium",
            framework_id="trope_convention",
            rationale=d.findings[0] if d.findings else "Fulfill reader expectations.",
            expected_gain=_expected_gain(d),
        ))

    # Chapter-risk-driven micro-fixes (one per high-risk chapter).
    for r in risks:
        if r.retention_risk == "high":
            items.append(RoadmapItem(
                priority=0, title=r.suggested_fix or "Fix high-risk chapter",
                chapter_scope="ch:%d" % r.chapter_index, effort="low", impact="high",
                framework_id="retention_psych",
                rationale="; ".join(r.reasons),
                expected_gain=round(12.0 * 0.15, 2),
            ))

    if not items:
        items.append(RoadmapItem(
            priority=0, title="Maintain current pacing; no urgent fixes",
            chapter_scope="global", effort="low", impact="low",
            framework_id="tension_curve",
            rationale="All dimensions above threshold; continue monitoring.",
            expected_gain=0.0,
        ))

    # rank: expected_gain * impact / effort, then impact desc, then effort asc.
    def rank_key(it: RoadmapItem) -> Tuple[float, int, int]:
        e = EFFORT_RANK[it.effort] or 2
        i = IMPACT_RANK[it.impact] or 2
        ratio = (it.expected_gain + 0.01) * i / e
        return (-ratio, -i, e)

    items.sort(key=rank_key)
    ranked = []
    for idx, it in enumerate(items, 1):
        ranked.append(RoadmapItem(
            priority=idx, title=it.title, chapter_scope=it.chapter_scope,
            effort=it.effort, impact=it.impact, framework_id=it.framework_id,
            rationale=it.rationale, expected_gain=it.expected_gain,
        ))
    return ranked
