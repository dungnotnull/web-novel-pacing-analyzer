"""schemas.py — typed data model for the pacing-analyzer pipeline.

Uses stdlib dataclasses only (no external dependency) so the package is
trivially installable and open-source friendly. Every object exposes
``to_dict`` / ``from_dict`` for JSON (de)serialization and is the contract
shared with the markdown skill harness and sibling cluster skills.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Named frameworks — single source of truth. Each scoring dimension MUST cite
# one of these; the gates enforce it.
# ---------------------------------------------------------------------------

FRAMEWORKS: Dict[str, str] = {
    "three_act": "Three-Act Structure (Syd Field / Aristotle)",
    "save_the_cat": "Save the Cat! Beat Sheet (Blake Snyder)",
    "heros_journey": "Hero's Journey / Monomyth (Joseph Campbell)",
    "scene_sequel": "Scene-Sequel & Try/Fail Cycle (Dwight Swain)",
    "hook_density": "Hook Density & Chapter Cliffhanger (serialized-fiction craft)",
    "tension_curve": "Page-Turner Tension Curve (reader-engagement models)",
    "kishotenketsu": "Kishōtenketsu & web-serial arc/chapter cadence",
    "retention_psych": "Reader-Retention Psychology (curiosity gaps, variable reward)",
    "trope_convention": "Genre-Trope Conventions & reader-expectation fulfillment",
}

# Mapping of scoring dimension -> governing framework id.
DIMENSION_FRAMEWORK: Dict[str, str] = {
    "structure": "save_the_cat",
    "act_pacing": "three_act",
    "chapter_pacing": "scene_sequel",
    "hook_density": "hook_density",
    "tension_curve": "tension_curve",
    "arc_cadence": "kishotenketsu",
    "trope_fit": "trope_convention",
    "retention": "retention_psych",
}

# Evidence tiers, ordered from strongest to weakest. Higher index = weaker.
EVIDENCE_TIERS = [
    "systematic_review",
    "meta_analysis",
    "benchmark",
    "field_study",
    "expert_opinion",
    "internal_heuristic",
]


@dataclass
class Chapter:
    """A single serialized chapter supplied by the author."""

    index: int
    title: str = ""
    text: str = ""
    word_count: int = 0
    notes: str = ""

    def __post_init__(self) -> None:
        if self.word_count == 0 and self.text:
            self.word_count = _count_words(self.text)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Chapter":
        return cls(
            index=int(d.get("index", 0)),
            title=str(d.get("title", "")),
            text=str(d.get("text", "")),
            word_count=int(d.get("word_count", 0)),
            notes=str(d.get("notes", "")),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FrameworkSelection:
    """Output of sub-evaluation-framework-selector."""

    genre: str
    length_format: str  # "web_serial" | "print" | "novella" | "short"
    frameworks: List[str] = field(default_factory=list)  # ids from FRAMEWORKS
    rationale: str = ""
    assumptions: List[str] = field(default_factory=list)
    scope_in: List[str] = field(default_factory=list)
    scope_out: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)

    def framework_names(self) -> List[str]:
        return [FRAMEWORKS[f] for f in self.frameworks if f in FRAMEWORKS]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "FrameworkSelection":
        return cls(**{k: d.get(k, [] if k in ("frameworks", "assumptions", "scope_in", "scope_out", "evidence") else "") for k in
                      ("genre", "length_format", "frameworks", "rationale", "assumptions", "scope_in", "scope_out", "evidence")})


@dataclass
class TensionPoint:
    """One point on the chapter-level tension curve."""

    chapter_index: int
    tension: float  # 0..1
    hook_strength: float  # 0..1
    cliffhanger: bool
    label: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "TensionPoint":
        return cls(
            chapter_index=int(d["chapter_index"]),
            tension=float(d["tension"]),
            hook_strength=float(d["hook_strength"]),
            cliffhanger=bool(d["cliffhanger"]),
            label=str(d.get("label", "")),
        )


@dataclass
class DimensionScore:
    """A single multi-dimensional score against a named framework."""

    dimension: str
    framework_id: str
    framework_name: str
    score: float  # 0..100
    weight: float  # 0..1
    findings: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    evidence_tier: str = "internal_heuristic"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "DimensionScore":
        return cls(
            dimension=str(d["dimension"]),
            framework_id=str(d["framework_id"]),
            framework_name=str(d["framework_name"]),
            score=float(d["score"]),
            weight=float(d.get("weight", 1.0)),
            findings=list(d.get("findings", [])),
            evidence=list(d.get("evidence", [])),
            evidence_tier=str(d.get("evidence_tier", "internal_heuristic")),
        )


@dataclass
class ChapterRisk:
    """Retention-risk flag for a single chapter."""

    chapter_index: int
    retention_risk: str  # "low" | "medium" | "high"
    reasons: List[str] = field(default_factory=list)
    suggested_fix: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ChapterRisk":
        return cls(
            chapter_index=int(d["chapter_index"]),
            retention_risk=str(d["retention_risk"]),
            reasons=list(d.get("reasons", [])),
            suggested_fix=str(d.get("suggested_fix", "")),
        )


@dataclass
class RoadmapItem:
    """A prioritized, effort/impact-ranked improvement action."""

    priority: int  # 1 = highest
    title: str
    chapter_scope: str  # "global" | "ch:N" | "ch:N-M" | "act:1"
    effort: str  # "low" | "medium" | "high"
    impact: str  # "low" | "medium" | "high"
    framework_id: str
    rationale: str
    expected_gain: float  # 0..100 expected score lift

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "RoadmapItem":
        return cls(
            priority=int(d["priority"]),
            title=str(d["title"]),
            chapter_scope=str(d["chapter_scope"]),
            effort=str(d["effort"]),
            impact=str(d["impact"]),
            framework_id=str(d["framework_id"]),
            rationale=str(d["rationale"]),
            expected_gain=float(d["expected_gain"]),
        )


@dataclass
class AnalysisRequest:
    """The harness intake object."""

    title: str
    genre: str
    chapters: List[Chapter] = field(default_factory=list)
    length_format: str = "web_serial"
    goal: str = ""
    audience: str = ""
    constraints: List[str] = field(default_factory=list)
    context: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AnalysisRequest":
        return cls(
            title=str(d.get("title", "")),
            genre=str(d.get("genre", "")),
            chapters=[Chapter.from_dict(c) for c in d.get("chapters", [])],
            length_format=str(d.get("length_format", "web_serial")),
            goal=str(d.get("goal", "")),
            audience=str(d.get("audience", "")),
            constraints=list(d.get("constraints", [])),
            context=str(d.get("context", "")),
        )


@dataclass
class AnalysisReport:
    """The final scored deliverable + roadmap artifact."""

    title: str
    headline_score: float
    verdict: str
    inputs_summary: Dict[str, Any] = field(default_factory=dict)
    framework_selection: Dict[str, Any] = field(default_factory=dict)
    tension_curve: List[Dict[str, Any]] = field(default_factory=list)
    dimension_scores: List[Dict[str, Any]] = field(default_factory=list)
    chapter_risks: List[Dict[str, Any]] = field(default_factory=list)
    findings: Dict[str, List[str]] = field(default_factory=dict)
    roadmap: List[Dict[str, Any]] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    gate_results: Dict[str, Any] = field(default_factory=dict)
    challenge_pass: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        import json
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


def _count_words(text: str) -> int:
    return len(text.split())
