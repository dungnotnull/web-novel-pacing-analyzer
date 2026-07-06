---
name: sub-evaluation-framework-selector
description: Identify genre, length format, and the structural model to evaluate the manuscript against.
---

## Role
Sub-skill of `web-novel-pacing-analyzer`. Determines the genre, length format,
and the named structural model(s) the manuscript will be scored against. It is
the **intake & framing** stage and owns scope screening (refuse / redirect).

## Reference Implementation
Deterministic logic lives in `tools/pacing_analyzer/framework_selector.py`
(`normalize_genre`, `select_frameworks`, `run`). The shared typed contract is
`FrameworkSelection` in `tools/pacing_analyzer/schemas.py` and the JSON
schema in `tools/pacing_analyzer/data/scoring_schema.json`.

## Inputs
- `AnalysisRequest` (`tools/pacing_analyzer/schemas.py`):
  - `title`, `genre`, `length_format` (`web_serial` | `print` | `novella` | `short`)
  - `chapters: Chapter[]` (each `{index, title, text, word_count?}`)
  - `goal`, `audience`, `constraints[]`, `context`
- Prior stage outputs (none — this is the first stage).

## Procedure
1. **Validate & screen.** If chapters are empty or any chapter has no text,
   return `Refused: insufficient input`. If the request contains scope-out
   triggers (ghostwriting a full manuscript, plagiarism, copyright
   infringement), return `Refused: out of scope`.
2. **Normalize genre.** Map free-text genre to a canonical id via the
   `GENRE_PROFILES` keys in `genre_data.py` (`litrpg`, `xianxia`, `romance`,
   `fantasy`, `scifi`, `thriller`, `mystery`, `horror`, `slice_of_life`,
   `general`) using known aliases.
3. **Select governing frameworks.** Every manuscript is scored against the
   core set: `save_the_cat`, `three_act`, `scene_sequel`, `hook_density`,
   `tension_curve`, `retention_psych`. Trope-driven genres add
   `trope_convention` + `kishotenketsu`; slice-of-life uses `kishotenketsu`
   as the spine. See `select_frameworks`.
4. **Derive cadence targets** from `GENRE_PROFILES[genre]`:
   `target_word_count`, `cadence_chapters_per_arc`, `cliffhanger_density`,
   `hook_must_appear_by_chapter`, `inciting_incident_by_pct`.
5. **State assumptions & scope.** Document language/order assumptions and the
   explicit `scope_in` / `scope_out` lists.

## Outputs
A `FrameworkSelection` object:
```
genre, length_format, frameworks[], rationale,
assumptions[], scope_in[], scope_out[], evidence[]
```
Every `frameworks` id MUST exist in `FRAMEWORKS` (framework gate enforces this).

## Quality Gate
- Schema-valid `FrameworkSelection`.
- All selected frameworks are named entries in `FRAMEWORKS`.
- Scope explicitly stated (in/out).
- Refusals are returned (not silently bypassed) when input is insufficient or
  out of scope.
