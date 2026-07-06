# SHARED-SCORING-SCHEMA.md — cross-skill scoring standard (design-creative-media cluster)

> Standardized, versioned scoring schema and reusable sub-skills shared across
> the `design-creative-media` skill cluster so sibling skills reuse — not
> duplicate — the analytical backbone.

## Canonical schema
The machine-readable contract lives at
`tools/pacing_analyzer/data/scoring_schema.json` (JSON Schema, `version: 1.0.0`).
All cluster skills that produce a scored deliverable MUST conform to it.

## Report shape (version 1.0.0)
```
title, headline_score (0-100), verdict,
inputs_summary, framework_selection { genre, length_format, frameworks[] },
tension_curve[{ chapter_index, tension(0-1), hook_strength(0-1), cliffhanger, label }],
dimension_scores[{ dimension, framework_id, framework_name, score(0-100),
                   weight(0-1), findings[], evidence[], evidence_tier }],
chapter_risks[{ chapter_index, retention_risk(low|medium|high), reasons[], suggested_fix }],
roadmap[{ priority, title, chapter_scope, effort, impact, framework_id,
          rationale, expected_gain }],
sources[], limitations[], gate_results{ evidence_gate, framework_gate,
                                        challenge_gate, all_passed },
challenge_pass
```

## Reusable sub-skills (call, don't reimplement)
| Sub-skill | Module | Sibling reuse |
|-----------|--------|---------------|
| `sub-evaluation-framework-selector` | `pacing_analyzer.framework_selector` | Genre/format selection for any narrative-structure skill |
| `sub-scoring-engine` | `pacing_analyzer.scoring_engine` | Multi-dimensional framework-grounded scoring |
| `sub-trope-trend-updater` | `pacing_analyzer.trope_trend_updater` | Offline trend-signal refresh from a brain |
| `sub-improvement-roadmap` | `pacing_analyzer.improvement_roadmap` | Effort/impact-ranked roadmap from any scored dimensions |

Sibling skills import these modules (`from pacing_analyzer import …`) and add
their own domain-specific `dimension` ids + framework mappings, extending
`DIMENSION_FRAMEWORK` and `FRAMEWORKS` rather than forking the engine.

## Standardization rules
1. **No ad-hoc criteria.** Every score cites a named framework id from
   `FRAMEWORKS`; the framework gate enforces this.
2. **Evidence tiers.** Use the shared tier ladder:
   `systematic_review > meta_analysis > benchmark > field_study >
    expert_opinion > internal_heuristic`.
3. **Weights sum meaningfully.** Dimension weights are explicit; the headline
   score is the weighted mean over `Σ(weight)`.
4. **Roadmap ranking.** Always priority-ordered from 1, ranked by
   `expected_gain × impact / effort`.
5. **Versioning.** Schema changes bump `scoring_schema.json` `version`;
   consumers pin to a major version.

## Evidence gate / framework gate / challenge gate
All three gates are implemented in `pacing_analyzer.gates` and shared across the
cluster; siblings reuse `run_gates(report)` rather than re-implementing.
