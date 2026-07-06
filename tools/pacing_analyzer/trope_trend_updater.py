"""trope_trend_updater.py — sub-trope-trend-updater (offline) implementation.

Refreshes genre-trope trend signals from the SECOND-KNOWLEDGE-BRAIN when a
recent crawl is available, falling back to the curated GENRE_PROFILES
otherwise. No network access at runtime: production-safe and deterministic.

Trend weight formula (offline proxy):
    base = 1.0
    if brain updated within 7 days: trend_boost = 0.15
    elif updated within 30 days: trend_boost = 0.08
    else: trend_boost = 0.0
"""
from __future__ import annotations

import datetime
import os
import re
from typing import Dict, List, Tuple

from .genre_data import GENRE_PROFILES


BRAIN_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..",
    "SECOND-KNOWLEDGE-BRAIN.md",
)


def _brain_mtime() -> datetime.date:
    try:
        ts = os.path.getmtime(BRAIN_PATH)
        return datetime.date.fromtimestamp(ts)
    except OSError:
        return datetime.date(2000, 1, 1)


def _last_log_date() -> datetime.date:
    try:
        with open(BRAIN_PATH, encoding="utf-8") as f:
            txt = f.read()
    except OSError:
        return datetime.date(2000, 1, 1)
    dates = re.findall(r"^-\s*(\d{4}-\d{2}-\d{2})\s+—", txt, re.M)
    if not dates:
        return datetime.date(2000, 1, 1)
    return datetime.date.fromisoformat(max(dates))


def brain_freshness() -> Tuple[datetime.date, str]:
    last = _last_log_date()
    age = (datetime.date.today() - last).days
    if age <= 7:
        tier = "fresh"
    elif age <= 30:
        tier = "recent"
    else:
        tier = "stale"
    return last, tier


def trend_weights(genre: str) -> Dict[str, float]:
    """Return per-trope trend weight in [1.0, 1.15]."""
    _, tier = brain_freshness()
    boost = {"fresh": 0.15, "recent": 0.08, "stale": 0.0}.get(tier, 0.0)
    profile = GENRE_PROFILES.get(genre, GENRE_PROFILES["general"])
    # newer-positioned tropes in the list get slightly more trend weight
    n = len(profile["expected_tropes"])
    weights: Dict[str, float] = {}
    for i, t in enumerate(profile["expected_tropes"]):
        recency = (1.0 - (i / max(1, n)))  # earlier = more core
        weights[t] = round(1.0 + boost * (0.5 + 0.5 * recency), 3)
    return weights


def run(genre: str) -> Tuple[Dict[str, float], str, List[str]]:
    last, tier = brain_freshness()
    weights = trend_weights(genre)
    findings: List[str] = []
    if tier == "fresh":
        findings.append("SECOND-KNOWLEDGE-BRAIN refreshed within 7 days; trend signals are current.")
    elif tier == "recent":
        findings.append("SECOND-KNOWLEDGE-BRAIN recent (<=30 days); trend signals slightly degraded.")
    else:
        findings.append("SECOND-KNOWLEDGE-BRAIN stale (>30 days); trend signals fall back to curated baseline. Run tools/knowledge_updater.py.")
    findings.append("Last brain update: %s (tier=%s)." % (last.isoformat(), tier))
    return weights, tier, findings
