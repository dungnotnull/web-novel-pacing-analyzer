# tests/test-scenarios.md — Web Novel Scriptwriting & Pacing Analyzer

Scenario-based tests for the `web-novel-pacing-analyzer` harness. Each scenario
asserts the harness flow, framework-grounded scoring, gate enforcement, and
deliverable shape. Fixtures live in `tests/fixtures/`; the executable
regression suite is `tests/test_scenarios.py` (`pytest -q` → 17 passed).

## Shared assertions (every scenario)
- Gates pass: evidence, framework, challenge (`gate_results.all_passed == true`).
- Every dimension cites a named framework matching `DIMENSION_FRAMEWORK`.
- Roadmap is priority-ordered from 1; items cite a named framework.
- Output has all required sections (determinism of structure).

### Scenario 1 — sagging mid-arc
- **Given (fixture):** `scenario_1_request.json` — 10 LitRPG chapters; calm
  chapters 5–7 create a mid-arc sag.
- **Expected harness behavior:** intake ok → framework selected →
  `sub-scoring-engine` flags a tension-curve mid-arc sag + ≥1 high-risk
  chapter → roadmap includes a tension-curve fix → gates pass.
- **Pass criteria:** gates pass; tension-curve finding contains "sag"; ≥1
  high-risk chapter; tension-curve roadmap item present.
- **Captured (expected_manifest.json):** headline 62.8; high-risk [5]; gates pass.

### Scenario 2 — flat endings
- **Given:** `scenario_2_request.json` — 5 calm chapters ending flat, no hooks/cliffhangers.
- **Expected:** hook-density score < 70; cliffhanger coverage < 0.2; hook-density roadmap item.
- **Captured:** headline 42.9; high-risk [1].

### Scenario 3 — LitRPG genre fit
- **Given:** `scenario_3_request.json` — full LitRPG trope coverage, strong structure.
- **Expected:** genre normalized to `litrpg`; `trope_convention` framework selected; trope-fit ≥ 70.
- **Captured:** headline 64.1; high-risk [3].

### Scenario 4 — slow act one
- **Given:** `scenario_4_request.json` — inciting incident delayed to chapter 5.
- **Expected:** act_pacing < 70; finding mentions slow/delayed; three-act roadmap item.
- **Captured:** headline 43.2; high-risk [1,2,4,5].

### Scenario 5 — cadence advice
- **Given:** `scenario_5_request.json` — alternating very-long and very-short chapters.
- **Expected:** arc_cadence < 70; kishōtenketsu roadmap item.
- **Captured:** headline 57.0; high-risk [4].

### Scenario 6 — retention heatmap
- **Given:** `scenario_6_request.json` — thriller with a calm slump mid-arc.
- **Expected:** per-chapter retention-risk heatmap present; ≥1 high-risk; high-risk chapter covered by a targeted or global roadmap item.
- **Captured:** headline 69.2; high-risk [4].

## Cross-cutting checks
- **Refusal/scope:** `refusal_request.json` (ghostwrite) → `verdict` starts with `Refused:`, headline 0, gates fail; `empty_request.json` → refused.
- **Graceful degradation:** with no network at runtime, the report still emits and states a brain/trend limitation.
- **Determinism of structure:** every run yields all output-format sections.
- **Regression manifest:** `test_regression_manifest_matches` locks headline scores, high-risk chapters, dimension scores, and selected frameworks against `tests/fixtures/expected_manifest.json`.

## Running
```bash
pip install -e .[dev]
pytest -q          # 17 passed
pacing_analyzer frameworks
python tools/knowledge_updater.py --dry-run --no-domains
```

To regenerate fixtures/manifest after a deliberate behavior change:
```bash
python tests/fixtures/build_fixtures.py
# then re-run the manifest generator (see tests/test_scenarios.py header)
```
