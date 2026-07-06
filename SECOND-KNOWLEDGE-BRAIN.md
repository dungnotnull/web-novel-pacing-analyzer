# SECOND-KNOWLEDGE-BRAIN.md — Web Novel Scriptwriting & Pacing Analyzer

> Self-improving domain knowledge base for the `web-novel-pacing-analyzer` skill. Grown continuously by `tools/knowledge_updater.py`.

## Core Concepts & Frameworks
- **Story structure models (Three-Act, Save the Cat beats, Hero's Journey)**
- **Scene-sequel & try/fail cycle pacing analysis**
- **Hook density, chapter cliffhanger, and 'page-turner' tension curves**
- **Kishōtenketsu and web-serial arc/chapter cadence**
- **Reader-retention psychology (curiosity gaps, variable reward)**
- **Genre-trope conventions and reader-expectation fulfillment**

## Key Research Papers
| Title | Authors | Year | Venue | DOI/Link | Relevance |
|-------|---------|------|-------|----------|-----------|
| _(seed — populate via knowledge_updater.py)_ | — | — | — | — | Foundational references for Design, Creative & Media. |

## State-of-the-Art Methods & Tools
- Apply the frameworks above as the scoring backbone.
- Prefer the highest available evidence tier (Systematic Review > Meta-Analysis > RCT/benchmark > Cohort/field study > Expert opinion > Blog).
- Triangulate multiple sources before asserting a numeric score.

## Authoritative Data Sources
- Narrative-theory references (Save the Cat, Story Grid)
- Web-fiction platform trend data (Royal Road, Wattpad, WebNovel public stats)
- Google Scholar for narrative-engagement research
- Reputable writing-craft resources
- Reader-retention analytics writeups from serialized-fiction authors

## Analytical Frameworks (Scoring Backbone)
The skill scores every deliverable against the named frameworks above; each scoring dimension cites the framework it derives from.

## Self-Update Protocol
- **Tool:** `tools/knowledge_updater.py`
- **ArXiv categories:** cs.CL
- **Search queries:**
  - `narrative pacing reader retention serialized fiction`
  - `story structure beat sheet analysis`
  - `web novel trope trends`
  - `cliffhanger curiosity gap engagement`
- **Domains:** storygrid.com
- **Frequency:** weekly cron.
- **Append format:** date-stamped row in *Key Research Papers* + a *Knowledge Update Log* line; deduplicate by URL/DOI hash.

## Knowledge Update Log
- 2026-06-18 — Brain initialized with core frameworks and seed sources for `web-novel-pacing-analyzer`.
- 2026-07-06 — Added deterministic Python implementation (	ools/pacing_analyzer/) and shared standardized scoring schema (	ools/pacing_analyzer/data/scoring_schema.json, v1.0.0) for cross-skill reuse in the design-creative-media cluster.
