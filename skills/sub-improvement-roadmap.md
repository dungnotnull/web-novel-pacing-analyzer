---
name: sub-improvement-roadmap
description: Recommend chapter-level pacing fixes, hook insertions, and arc restructuring with priority.
---

## Role
Sub-skill of `web-novel-pacing-analyzer`. Converts the dimension scores,
chapter-risk flags, tension curve, and trope gaps into a **prioritized,
effort × impact-ranked roadmap**. Every item cites the governing framework.

## Reference Implementation
`tools/pacing_analyzer/improvement_roadmap.py` (`build_roadmap`). The shared
contract is `RoadmapItem` in `schemas.py`.

## Inputs
- `DimensionScore[]`, `ChapterRisk[]`, `TensionPoint[]`, selected `genre`.

## Procedure
1. **Dimension-driven fixes.** For each dimension below threshold, propose a
   scoped action (chapter_scope ∈ `global` | `act:1` | `act:2` | `ch:N` |
   `ch:N-M`), assign `effort`/`impact`, and compute `expected_gain` =
   `(100 − score) × weight`.
   - structure < 80 → Save the Cat beat audit (`act:1`).
   - act_pacing < 75 → tighten act one (`act:1`).
   - hook_density < 80 → raise hooks/cliffhangers (`global`).
   - tension_curve < 75 → repair mid-arc sag (`act:2`).
   - chapter_pacing < 75 → vary scene/sequel rhythm (`global`).
   - arc_cadence < 75 → standardize chapter length (`global`).
   - trope_fit < 70 → add missing reader-expectation tropes (`global`).
2. **Chapter-risk micro-fixes.** One targeted item per `high`-risk chapter,
   scoped to `ch:N`, citing `retention_psych`.
3. **Ranking.** Sort by `expected_gain × impact_rank / effort_rank` desc,
   then impact desc, then effort asc; assign sequential `priority` from 1.
4. **Default.** If all dimensions are healthy, emit a single maintenance item.

## Outputs
- `RoadmapItem[]`: `{priority, title, chapter_scope, effort, impact,
  framework_id, rationale, expected_gain}`.

## Quality Gate
- Strictly priority-ordered from 1.
- Every item cites a named framework (framework gate).
- High-risk chapters are covered by a targeted or global roadmap item
  (challenge gate checks uncovered high-risk chapters).
- `effort`/`impact` ∈ {low, medium, high}; `expected_gain ≥ 0`.
