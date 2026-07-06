# PROJECT-detail.md — Web Novel Scriptwriting & Pacing Analyzer

## Executive Summary
This skill is a full Claude harness that turns analyze web-novel structure and chapter pacing for retention in niche genres. It operates research-first: every material judgment is grounded in a named, citable framework and, where possible, a freshly retrieved source. It produces a professional-grade deliverable: a multi-dimensional score against the chosen framework plus a prioritized, effort/impact-ranked improvement roadmap.

## Problem Statement
Web-novel authors lose readers to slow chapters, weak hooks, and sagging mid-arcs because serialized fiction has different pacing demands than print. This skill analyzes a manuscript's structure and chapter pacing against narrative and reader-psychology models, scores retention risk, and continuously updates genre tropes and trending motifs.

## Target Users & Use Cases
Primary users are practitioners and decision-makers in the **Design, Creative & Media** domain. Trigger examples:
1. Author pastes 10 chapters; skill plots a tension curve and flags a sagging mid-arc.
2. Chapters end flat; skill scores hook density and proposes cliffhanger insertions.
3. A LitRPG novel needs genre fit; trope-updater checks reader-expectation conventions.
4. Pacing is too slow in act one; skill restructures beats to hit the inciting incident sooner.
5. Author wants chapter-length cadence advice; skill recommends serialized cadence for the genre.
6. Skill outputs a chapter-by-chapter retention-risk heatmap with prioritized fixes.

## Harness Architecture
```
/web-novel-pacing-analyzer (main.md harness)
  -> sub-evaluation-framework-selector              [intake / framing]
  -> sub-scoring-engine              [framework selection / risk-scope screen]
  -> knowledge refresh   [SECOND-KNOWLEDGE-BRAIN via knowledge_updater.py]
  -> sub-trope-trend-updater              [multi-dimensional scoring]
  -> evidence + challenge gate
  -> improvement roadmap [prioritized, effort/impact]
  -> SYNTHESIZE          [final scored deliverable]
```

## Full Sub-Skill Catalog
### sub-evaluation-framework-selector
- **Purpose:** Identify genre, length format, and the structural model to evaluate the manuscript against.
- **Inputs:** outputs of the prior stage + user-provided context.
- **Outputs:** structured findings passed to the next stage.
- **Tools:** WebSearch, WebFetch, Read, Write, Bash
- **Quality gate:** output is schema-valid, evidence-linked, and framework-grounded before the harness proceeds.
### sub-scoring-engine
- **Purpose:** Score structure, chapter pacing, hook density, and tension curve; flag retention-risk chapters.
- **Inputs:** outputs of the prior stage + user-provided context.
- **Outputs:** structured findings passed to the next stage.
- **Tools:** WebSearch, WebFetch, Read, Write, Bash
- **Quality gate:** output is schema-valid, evidence-linked, and framework-grounded before the harness proceeds.
### sub-trope-trend-updater
- **Purpose:** Refresh genre tropes, trending motifs, and keyword conventions from major platforms.
- **Inputs:** outputs of the prior stage + user-provided context.
- **Outputs:** structured findings passed to the next stage.
- **Tools:** WebSearch, WebFetch, Read, Write, Bash
- **Quality gate:** output is schema-valid, evidence-linked, and framework-grounded before the harness proceeds.
### sub-improvement-roadmap
- **Purpose:** Recommend chapter-level pacing fixes, hook insertions, and arc restructuring with priority.
- **Inputs:** outputs of the prior stage + user-provided context.
- **Outputs:** structured findings passed to the next stage.
- **Tools:** WebSearch, WebFetch, Read, Write, Bash
- **Quality gate:** output is schema-valid, evidence-linked, and framework-grounded before the harness proceeds.

## Skill File Format Specification
Every skill file uses YAML frontmatter (`name`, `description`) followed by the required sections: Role & Persona, Workflow (Harness Flow), Sub-skills Available, Tools, Output Format, Quality Gates. The main harness invokes sub-skills via the Skill tool in the order shown above.

## E2E Execution Flow
1. Parse the user request; if inputs are insufficient, `sub-evaluation-framework-selector` asks targeted intake questions.
2. `sub-scoring-engine` selects the governing framework(s) and screens scope/risk; branch to a refusal or disclaimer if out of scope.
3. Refresh knowledge if the brain is stale (>7 days) and WebSearch/WebFetch are available; otherwise degrade gracefully to internal knowledge with a stated limitation.
4. `sub-trope-trend-updater` scores each dimension, citing evidence per claim.
5. Run the evidence/quality gate(s) and a devil's-advocate challenge pass.
6. Emit the scored report + roadmap in the Output Format below.

## SECOND-KNOWLEDGE-BRAIN Integration
- **Sources:** Narrative-theory references (Save the Cat, Story Grid); Web-fiction platform trend data (Royal Road, Wattpad, WebNovel public stats); Google Scholar for narrative-engagement research; Reputable writing-craft resources; Reader-retention analytics writeups from serialized-fiction authors
- **Crawl config:** see `tools/knowledge_updater.py` (ArXiv categories cs.CL; domain queries seeded from the idea).
- **Append format:** date-stamped entries with Title, Authors, Year, Venue, DOI/URL, key finding, relevance note; deduplicated by URL/DOI hash.

## Supporting Tools Spec — knowledge_updater.py
- **Inputs:** search queries + source list (in-file config), optional `--since` date.
- **Outputs:** appended entries in `SECOND-KNOWLEDGE-BRAIN.md` + a run log.
- **Schedule:** weekly cron (graceful no-op when offline).

## Quality Gates
- **Evidence gate:** every material claim is traceable to a cited source or a prior step; prefer the highest evidence tier available.
- **Framework gate:** all scoring is grounded in the named frameworks below — never ad-hoc criteria.
- **Challenge gate:** a devil's-advocate pass has stress-tested the recommendation before it is shown.

## Test Scenarios
See `tests/test-scenarios.md` (>=5 concrete scenarios with expected harness behavior).

## Key Design Decisions
1. Framework-grounded scoring only — no ad-hoc rubrics.
2. Research-first with graceful degradation when offline.
3. Composable sub-skills (>=3) so cluster siblings can reuse them.
4. Deliverable is an artifact (scored report + roadmap), not a chat reply.
5. Evidence/quality gate enforced before any sensitive/regulated output.
