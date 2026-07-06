# Web Novel Scriptwriting & Pacing Analyzer

Analyze web-novel structure and chapter pacing for reader retention in niche
genres. A **research-first, framework-grounded** analyzer: every scoring
dimension cites a named, citable narrative framework, the pipeline is fully
**deterministic** (no ML model, no network required at runtime), and the
deliverable is a professional scored report + prioritized improvement roadmap.

Part of the `design-creative-media` Claude skill cluster.

## Why
Serialized fiction has different pacing demands than print. Readers churn on
slow chapters, weak hooks, and sagging mid-arcs. This skill scores structure,
chapter pacing, hook density, tension curve, arc cadence, trope fit, and
retention risk — then returns effort/impact-ranked fixes.

## Governing Frameworks (every score cites one)
1. Three-Act Structure (Syd Field / Aristotle)
2. Save the Cat! Beat Sheet (Blake Snyder)
3. Hero's Journey / Monomyth (Joseph Campbell)
4. Scene-Sequel & Try/Fail Cycle (Dwight Swain)
5. Hook Density & Chapter Cliffhanger (serialized-fiction craft)
6. Page-Turner Tension Curve (reader-engagement models)
7. Kishōtenketsu & web-serial arc/chapter cadence
8. Reader-Retention Psychology (curiosity gaps, variable reward)
9. Genre-Trope Conventions & reader-expectation fulfillment

## Install (production stage)
```bash
pip install -e .[dev]      # editable, with test deps
# or production:
pip install .
```

## Use
```bash
# Analyze a manuscript (JSON request matching AnalysisRequest)
pacing_analyzer analyze manuscript.json --genre litrpg --pretty

# List governing frameworks
pacing_analyzer frameworks

# As a library
from pacing_analyzer import AnalysisRequest, run
report = run(AnalysisRequest.from_dict(request_dict))
print(report.to_json())
```

### Input schema (abbreviated)
```json
{
  "title": "The System Awakens",
  "genre": "litrpg",
  "length_format": "web_serial",
  "goal": "Maximize chapter-end retention",
  "chapters": [
    {"index": 1, "title": "Awakening", "text": "Suddenly everything changed..."}
  ]
}
```

## Output (scored deliverable)
- Executive summary (headline score + verdict)
- Inputs & assumptions
- Framework selection
- Per-chapter tension curve
- Multi-dimensional score (each dimension cites its framework + evidence tier)
- Per-chapter retention-risk flags
- Findings (strengths / risks / gaps)
- Prioritized improvement roadmap (effort × impact)
- Sources & limitations
- Quality-gate results (evidence / framework / challenge)

## Knowledge pipeline
`tools/knowledge_updater.py` crawls ArXiv + authoritative domain sources, scores
by recency + relevance, deduplicates by URL/DOI hash, and appends date-stamped
entries to `SECOND-KNOWLEDGE-BRAIN.md`. Schedule: weekly cron. Graceful no-op
when offline.

## Tests
```bash
pytest -q
```

## License
MIT
