"""harness.py — main harness orchestrator for web-novel-pacing-analyzer.

Implements the end-to-end harness flow described in skills/main.md:
  intake -> framework selection & screening -> sub-skills in order ->
  knowledge refresh -> gates -> synthesize scored report + roadmap.

Refuses out-of-scope / unsafe input and degrades gracefully when the brain
is stale. Deterministic; no network; production-safe.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from .framework_selector import run as select_frameworks
from .gates import run_gates
from .improvement_roadmap import build_roadmap
from .scoring_engine import headline, score
from .schemas import AnalysisReport, AnalysisRequest
from .trope_trend_updater import run as trend_run

# Scope-out keywords that trigger a refusal/redirect.
REFUSAL_TRIGGERS = (
    "plagiar", "copyright infringe", "pirate", "steal this",
    "write the chapters for me", "ghostwrite the whole", "generate full novel",
)


def _is_out_of_scope(request: AnalysisRequest) -> Optional[str]:
    blob = " ".join([request.title, request.goal, request.context, " ".join(request.constraints)]).lower()
    for t in REFUSAL_TRIGGERS:
        if t in blob:
            return (
                "Request is out of scope: the analyzer critiques structure and pacing; "
                "it does not ghostwrite, plagiarize, or produce a full manuscript. "
                "Refusing per scope gate."
            )
    if not request.chapters:
        return "Insufficient input: no chapters supplied. Provide at least one chapter of prose."
    if any(not ch.text.strip() for ch in request.chapters):
        return "Insufficient input: one or more chapters have empty text."
    return None


def _inputs_summary(request: AnalysisRequest, selection) -> Dict[str, Any]:
    return {
        "title": request.title,
        "genre": selection.genre,
        "length_format": request.length_format,
        "goal": request.goal,
        "audience": request.audience,
        "chapter_count": len(request.chapters),
        "total_word_count": sum(ch.word_count for ch in request.chapters),
        "constraints": request.constraints,
        "assumptions": selection.assumptions,
        "scope_in": selection.scope_in,
        "scope_out": selection.scope_out,
    }


def _verdict(score_val: float) -> str:
    if score_val >= 80:
        return "Strong: pacing and structure support serialized retention."
    if score_val >= 65:
        return "Adequate: meets baseline but has fixable retention risks."
    if score_val >= 50:
        return "At risk: notable pacing/structure weaknesses harming retention."
    return "Weak: serious structural/pacing problems; prioritize roadmap."


def run(request: AnalysisRequest) -> AnalysisReport:
    # 1. Intake & screening — refuse/redirect on out-of-scope or insufficient input.
    refusal = _is_out_of_scope(request)
    if refusal:
        return AnalysisReport(
            title=request.title or "untitled",
            headline_score=0.0,
            verdict="Refused: " + refusal,
            gate_results={"all_passed": False, "refusal": refusal},
            limitations=["No analysis produced."],
        )

    # 2. Framework selection & screening.
    selection = select_frameworks(request)

    # 3. Knowledge refresh (offline trend signals).
    trend_weights, trend_tier, trend_findings = trend_run(selection.genre)

    # 4. Sub-skill: scoring engine (multi-dimensional).
    dimensions, curve, risks, findings = score(request, selection)

    # 5. Sub-skill: improvement roadmap.
    roadmap = build_roadmap(dimensions, risks, curve, selection.genre)

    # 6. Synthesize draft report.
    headline_score = headline(dimensions)
    inputs = _inputs_summary(request, selection)
    sources = sorted({s for d in dimensions for s in d.evidence})
    sources.append("SECOND-KNOWLEDGE-BRAIN.md (tier=%s)" % trend_tier)

    report = AnalysisReport(
        title=request.title or "untitled",
        headline_score=headline_score,
        verdict=_verdict(headline_score),
        inputs_summary=inputs,
        framework_selection=selection.to_dict(),
        tension_curve=[p.to_dict() for p in curve],
        dimension_scores=[d.to_dict() for d in dimensions],
        chapter_risks=[r.to_dict() for r in risks],
        findings=findings,
        roadmap=[it.to_dict() for it in roadmap],
        sources=sources,
        limitations=trend_findings,
        gate_results={},
        challenge_pass="",
    )

    # 7. Gates (evidence, framework, challenge).
    gate_results = run_gates(report)
    report.gate_results = gate_results
    report.challenge_pass = gate_results["challenge_gate"]["message"]

    return report

