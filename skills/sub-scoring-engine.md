---
name: sub-scoring-engine
description: Score structure, chapter pacing, hook density, and tension curve; flag retention-risk chapters.
---

## Role
Sub-skill of `web-novel-pacing-analyzer`. Produces the **multi-dimensional
score** against the framework(s) selected by `sub-evaluation-framework-selector`
and flags per-chapter retention risk. This is the analytical core of the harness.

## Reference Implementation
`tools/pacing_analyzer/scoring_engine.py` (`score`, `headline`) orchestrates
the per-dimension scorers: `structure_scorer.py`, `chapter_pacing.py`,
`hook_density.py`, `tension_curve.py`, `arc_cadence.py`, `trope_matcher.py`.
The shared contract is `DimensionScore`, `TensionPoint`, `ChapterRisk` in
`schemas.py`.

## Inputs
- `AnalysisRequest` and the `FrameworkSelection` from the previous stage.

## Procedure (per dimension → named framework)
1. **Structure → Save the Cat! Beat Sheet.** Detect beat markers (inciting,
   midpoint, climax, resolution) per chapter; score alignment to the genre's
   `inciting_incident_by_pct`. Weighted 0.40 inciting / 0.30 midpoint /
   0.20 climax / 0.10 resolution. (`structure_scorer.structure_score`)
2. **Act pacing → Three-Act Structure.** Score inciting-catalyst placement
   vs the genre target; flag slow/over-fast act one. (`chapter_pacing.act_pacing_score`)
3. **Chapter pacing → Scene-Sequel & Try/Fail Cycle.** Sentence-length rhythm
   variety, paragraph density, scene-density shifts as a try/fail proxy.
   (`chapter_pacing.pacing_rhythm_score`)
4. **Hook density → Hook Density & Chapter Cliffhanger.** Per-chapter hook
   strength (opening 300 chars: hook markers + open questions), cliffhanger
   coverage vs `cliffhanger_density`, mandatory early hook by
   `hook_must_appear_by_chapter`. (`hook_density.hook_density_score`)
5. **Tension curve → Page-Turner Tension Curve.** Lexicon-based per-chapter
   tension, regression slope, and mid-arc sag detection. (`tension_curve.*`)
6. **Arc cadence → Kishōtenketsu & web-serial cadence.** Chapter-length
   adherence to `target_word_count`, length consistency, arc-length fit to a
   multiple of `cadence_chapters_per_arc`. (`arc_cadence.cadence_score`)
7. **Trope fit → Genre-Trope Conventions.** Coverage of the genre's
   `expected_tropes` against the manuscript corpus. (`trope_matcher.trope_fit_score`)
8. **Retention → Reader-Retention Psychology.** Composite of per-chapter
   retention-risk flags (relative mid-arc sag, missing/weak hooks, missing
   cliffhangers where expected). (`scoring_engine._retention_risk`)

## Headline score
Weighted mean of dimension scores: `Σ(score·weight) / Σ(weight)` with weights
[0.20 structure, 0.10 act_pacing, 0.15 chapter_pacing, 0.20 hook_density,
0.15 tension_curve, 0.10 arc_cadence, 0.10 trope_fit, 0.15 retention].

## Outputs
- `DimensionScore[]` (each cites `framework_id`, `framework_name`, `evidence`,
  `evidence_tier`).
- `TensionPoint[]` per-chapter curve.
- `ChapterRisk[]` retention-risk flags (`low` | `medium` | `high`).
- `findings` grouped into `strengths` / `risks` / `gaps`.

## Quality Gate
- Schema-valid outputs; every dimension cites a named framework (framework gate).
- Every dimension has ≥1 evidence entry and a valid `evidence_tier` (evidence gate).
- Scores are in [0, 100]; tension/hook in [0, 1].
