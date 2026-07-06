# CLAUDE.md — Web Novel Scriptwriting & Pacing Analyzer

**Skill slug:** `web-novel-pacing-analyzer`
**Source idea:** #184 (Vietnamese backlog `ideas.md`)
**Cluster:** design-creative-media — Design, Creative & Media
**Tagline:** Analyze web-novel structure and chapter pacing for retention in niche genres.
**Current phase:** Phase 5 — Integration & Cross-Skill Wiring (all phases complete)

## Problem This Skill Solves
Web-novel authors lose readers to slow chapters, weak hooks, and sagging mid-arcs because serialized fiction has different pacing demands than print. This skill analyzes a manuscript's structure and chapter pacing against narrative and reader-psychology models, scores retention risk, and continuously updates genre tropes and trending motifs.

## Harness Flow (Summary)
1. **Intake** → `sub-evaluation-framework-selector` gathers inputs and frames the problem.
2. **Screen / select** → `sub-scoring-engine` selects the governing framework and screens risk/scope.
3. **Score / analyze** → `sub-trope-trend-updater` produces a multi-dimensional score against named frameworks.
4. **Knowledge refresh** → optional `tools/knowledge_updater.py` run keeps SECOND-KNOWLEDGE-BRAIN.md current.
5. **Gate** → quality / evidence gates must pass.
6. **Synthesize** → main harness emits the scored deliverable + prioritized improvement roadmap.

## Sub-skills
- `skills/sub-evaluation-framework-selector.md` — Identify genre, length format, and the structural model to evaluate the manuscript against.
- `skills/sub-scoring-engine.md` — Score structure, chapter pacing, hook density, and tension curve; flag retention-risk chapters.
- `skills/sub-trope-trend-updater.md` — Refresh genre tropes, trending motifs, and keyword conventions from major platforms.
- `skills/sub-improvement-roadmap.md` — Recommend chapter-level pacing fixes, hook insertions, and arc restructuring with priority.

## Tools Required
WebSearch, WebFetch, Read, Write, Bash

## Knowledge Sources (for crawl + reasoning)
- Narrative-theory references (Save the Cat, Story Grid)
- Web-fiction platform trend data (Royal Road, Wattpad, WebNovel public stats)
- Google Scholar for narrative-engagement research
- Reputable writing-craft resources
- Reader-retention analytics writeups from serialized-fiction authors

## Supporting Python Tools
- `tools/knowledge_updater.py` — crawl4ai + WebSearch pipeline that fetches latest papers/reports from the domain sources above, scores by recency + relevance, deduplicates by URL/DOI hash, and appends to `SECOND-KNOWLEDGE-BRAIN.md`. Recommended schedule: weekly cron. CLI: `python tools/knowledge_updater.py --dry-run --no-domains`.

## Active Development Tasks
- [x] Scaffold all required deliverables
- [x] Define >=3 sub-skills with quality gates (4 sub-skills)
- [x] Ground scoring in named world-renowned frameworks
- [x] Wire knowledge_updater crawl sources (production CLI: --dry-run/--since/--max)
- [x] Implement deterministic production-grade Python package (`tools/pacing_analyzer/`)
- [x] Add regression fixtures + pytest suite for all 6 scenarios (18 tests passing)
- [x] Standardize scoring schema for cross-skill reuse (`scoring_schema.json` v1.0.0)
- [ ] Expand SECOND-KNOWLEDGE-BRAIN with first live crawl batch (pending scheduled cron run)

## Reference Docs (this folder)
- `PROJECT-detail.md` — full technical spec
- `PROJECT-DEVELOPMENT-PHASE-TRACKING.md` — phase roadmap
- `SECOND-KNOWLEDGE-BRAIN.md` — self-improving knowledge base
- `skills/main.md` — harness entry point
