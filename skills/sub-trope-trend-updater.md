---
name: sub-trope-trend-updater
description: Refresh genre tropes, trending motifs, and keyword conventions from major platforms.
---

## Role
Sub-skill of `web-novel-pacing-analyzer`. Refreshes genre-trope trend signals
from the SECOND-KNOWLEDGE-BRAIN and supplies per-trope trend weights to the
scoring engine. Offline, deterministic, production-safe: never blocks on
network at runtime.

## Reference Implementation
`tools/pacing_analyzer/trope_trend_updater.py` (`brain_freshness`,
`trend_weights`, `run`). The long-running crawl is `tools/knowledge_updater.py`
(ArXiv cs.CL + crawl4ai domain pages), run on a weekly cron.

## Inputs
- The selected `genre` from `sub-evaluation-framework-selector`.
- `SECOND-KNOWLEDGE-BRAIN.md` (read-only at runtime).

## Procedure
1. **Freshness check.** Read the brain's last Knowledge Update Log date.
   Tier: `fresh` (≤7 days) → +0.15 boost, `recent` (≤30 days) → +0.08 boost,
   `stale` (>30 days) → +0.00 (fall back to curated `GENRE_PROFILES`).
2. **Per-trope trend weight.** For each trope in `GENRE_PROFILES[genre].expected_tropes`,
   weight ∈ [1.00, 1.15], earlier (more core) tropes receiving slightly more
   of the freshness boost.
3. **Limitation statement.** Always emit a limitation note describing the
   brain tier so the harness can degrade gracefully (evidence gate).

## Outputs
- `trend_weights: {trope: float}` consumed by the trope matcher.
- `tier` (`fresh` | `recent` | `stale`).
- `findings[]` (limitation notes passed to the report).

## Knowledge refresh (out-of-band)
`tools/knowledge_updater.py` fetches ArXiv (cs.CL) and authoritative domain
pages (storygrid.com), scores by recency + keyword relevance, dedupes by
URL/DOI hash, and appends date-stamped rows to the *Key Research Papers*
table + *Knowledge Update Log*. CLI: `--dry-run`, `--since`, `--max`,
`--no-domains`, `--brain`. Graceful no-op when offline.

## Quality Gate
- A limitation note is always present (graceful degradation is explicit).
- No network call blocks the harness run.
- Trend weights stay within the documented [1.00, 1.15] band.
