"""pacing_analyzer — production-grade deterministic web-novel pacing analyzer.

This package implements the `web-novel-pacing-analyzer` Claude skill as a
runnable, testable Python library. All scoring is grounded in named, citable
narrative frameworks (Three-Act, Save the Cat, Hero's Journey, scene-sequel,
Kishōtenketsu, hook-density / tension-curve, reader-retention psychology,
genre-trope conventions). The package uses deterministic heuristics so it can
run in production with no ML model and zero network dependency; it degrades
gracefully when the SECOND-KNOWLEDGE-BRAIN is stale.

Public entry points:
    - harness.run(request: AnalysisRequest) -> AnalysisReport
    - cli.main(argv) for the command-line interface
"""
from .schemas import (
    AnalysisRequest,
    Chapter,
    FrameworkSelection,
    DimensionScore,
    ChapterRisk,
    RoadmapItem,
    AnalysisReport,
    TensionPoint,
)
from .harness import run
from .cli import main

__all__ = [
    "AnalysisRequest",
    "Chapter",
    "FrameworkSelection",
    "DimensionScore",
    "ChapterRisk",
    "RoadmapItem",
    "TensionPoint",
    "AnalysisReport",
    "run",
    "main",
]

__version__ = "1.0.0"
