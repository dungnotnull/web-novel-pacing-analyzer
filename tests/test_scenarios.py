"""test_scenarios.py — regression tests for the 6 harness scenarios + cross-cutting checks.

Each scenario asserts: gates pass, every dimension cites a named framework,
roadmap is effort/impact-ranked, output has the required sections, and the
scenario-specific expected behavior holds. Fixtures live in tests/fixtures/.
"""
from __future__ import annotations

import json
import os

import pytest

from pacing_analyzer import AnalysisRequest, run
from pacing_analyzer.schemas import FRAMEWORKS, DIMENSION_FRAMEWORK, EVIDENCE_TIERS
from pacing_analyzer.harness import _is_out_of_scope

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


def load_fixture(name):
    with open(os.path.join(FIXTURES, name), encoding="utf-8") as f:
        return AnalysisRequest.from_dict(json.load(f))


# --------------------------------------------------------------------------
# Shared shape checks
# --------------------------------------------------------------------------

def assert_report_shape(report):
    """Determinism of structure: every run yields the required sections."""
    for key in ("headline_score", "verdict", "inputs_summary", "framework_selection",
                "tension_curve", "dimension_scores", "chapter_risks", "findings",
                "roadmap", "sources", "limitations", "gate_results", "challenge_pass"):
        assert key in report.to_dict(), "missing report section: %s" % key


def assert_gates_pass(report):
    assert report.gate_results["all_passed"] is True
    assert report.gate_results["evidence_gate"]["passed"] is True
    assert report.gate_results["framework_gate"]["passed"] is True


def assert_framework_grounding(report):
    # every dimension cites a known framework id matching DIMENSION_FRAMEWORK
    for d in report.dimension_scores:
        assert d["framework_id"] in FRAMEWORKS
        assert d["framework_id"] == DIMENSION_FRAMEWORK[d["dimension"]]
        assert d["evidence_tier"] in EVIDENCE_TIERS
        assert d["evidence"], "dimension %s has no evidence" % d["dimension"]


def assert_roadmap_ranked(report):
    priorities = [it["priority"] for it in report.roadmap]
    assert priorities == sorted(priorities), "roadmap not priority-ordered"
    assert priorities[0] == 1
    for it in report.roadmap:
        assert it["framework_id"] in FRAMEWORKS
        assert it["effort"] in ("low", "medium", "high")
        assert it["impact"] in ("low", "medium", "high")


# --------------------------------------------------------------------------
# Scenarios 1-6
# --------------------------------------------------------------------------

def test_scenario_1_sagging_mid_arc():
    report = run(load_fixture("scenario_1_request.json"))
    assert_report_shape(report)
    assert_gates_pass(report)
    assert_framework_grounding(report)
    assert_roadmap_ranked(report)
    # mid-arc sag must surface as a tension-curve finding + at least one high-risk chapter
    tension_dim = [d for d in report.dimension_scores if d["dimension"] == "tension_curve"][0]
    assert any("sag" in f.lower() for f in tension_dim["findings"]), "expected mid-arc sag finding"
    high = [r for r in report.chapter_risks if r["retention_risk"] == "high"]
    assert high, "expected at least one high-risk chapter in the sagging mid-arc"
    # roadmap must include a tension-curve fix
    assert any(it["framework_id"] == "tension_curve" for it in report.roadmap)


def test_scenario_2_flat_endings_hook_density():
    report = run(load_fixture("scenario_2_request.json"))
    assert_report_shape(report)
    assert_gates_pass(report)
    assert_framework_grounding(report)
    assert_roadmap_ranked(report)
    hook_dim = [d for d in report.dimension_scores if d["dimension"] == "hook_density"][0]
    assert hook_dim["score"] < 70, "flat-ending manuscript should score low on hook density"
    assert any("cliffhanger" in f.lower() for f in hook_dim["findings"])
    # cliffhanger coverage should be low
    cliff_rate = sum(1 for p in report.tension_curve if p["cliffhanger"]) / len(report.tension_curve)
    assert cliff_rate < 0.2
    assert any(it["framework_id"] == "hook_density" for it in report.roadmap)


def test_scenario_3_litrpg_genre_fit():
    report = run(load_fixture("scenario_3_request.json"))
    assert_report_shape(report)
    assert_gates_pass(report)
    assert_framework_grounding(report)
    assert_roadmap_ranked(report)
    assert report.framework_selection["genre"] == "litrpg"
    trope_dim = [d for d in report.dimension_scores if d["dimension"] == "trope_fit"][0]
    assert trope_dim["score"] >= 70, "full trope coverage should score >= 70"
    assert "trope_convention" in report.framework_selection["frameworks"]


def test_scenario_4_slow_act_one():
    report = run(load_fixture("scenario_4_request.json"))
    assert_report_shape(report)
    assert_gates_pass(report)
    assert_framework_grounding(report)
    assert_roadmap_ranked(report)
    act_dim = [d for d in report.dimension_scores if d["dimension"] == "act_pacing"][0]
    assert act_dim["score"] < 70, "delayed inciting incident should score low on act pacing"
    assert any("slow" in f.lower() or "delayed" in f.lower() for f in act_dim["findings"])
    assert any(it["framework_id"] == "three_act" for it in report.roadmap)


def test_scenario_5_cadence_advice():
    report = run(load_fixture("scenario_5_request.json"))
    assert_report_shape(report)
    assert_gates_pass(report)
    assert_framework_grounding(report)
    assert_roadmap_ranked(report)
    cad_dim = [d for d in report.dimension_scores if d["dimension"] == "arc_cadence"][0]
    assert cad_dim["score"] < 70, "uneven chapter lengths should score low on cadence"
    assert any(it["framework_id"] == "kishotenketsu" for it in report.roadmap)


def test_scenario_6_retention_heatmap():
    report = run(load_fixture("scenario_6_request.json"))
    assert_report_shape(report)
    assert_gates_pass(report)
    assert_framework_grounding(report)
    assert_roadmap_ranked(report)
    # retention-risk heatmap: per-chapter risks present and at least one high
    assert report.chapter_risks, "expected per-chapter retention-risk heatmap"
    assert any(r["retention_risk"] == "high" for r in report.chapter_risks)
    # every high-risk chapter should have a targeted roadmap item OR a global fix
    high_chs = [r["chapter_index"] for r in report.chapter_risks if r["retention_risk"] == "high"]
    scopes = [it["chapter_scope"] for it in report.roadmap]
    for c in high_chs:
        assert ("ch:%d" % c) in scopes or "global" in scopes


# --------------------------------------------------------------------------
# Cross-cutting checks
# --------------------------------------------------------------------------

def test_refusal_out_of_scope():
    report = run(load_fixture("refusal_request.json"))
    assert report.verdict.startswith("Refused:")
    assert report.gate_results["all_passed"] is False
    assert report.headline_score == 0.0


def test_insufficient_input_empty_chapter():
    report = run(load_fixture("empty_request.json"))
    assert report.verdict.startswith("Refused:")


def test_graceful_degradation_offline():
    # No network is used at runtime; brain may be stale. The report must still
    # be produced and explicitly state the knowledge-currency limitation.
    report = run(load_fixture("scenario_1_request.json"))
    assert report.limitations, "graceful degradation must state a limitation"
    assert any("brain" in l.lower() or "stale" in l.lower() or "trend" in l.lower() or "knowledge" in l.lower()
               for l in report.limitations)


def test_frameworks_all_named():
    # Framework gate: no ad-hoc criteria; every dimension maps to a named framework.
    report = run(load_fixture("scenario_3_request.json"))
    for d in report.dimension_scores:
        assert d["framework_name"]


def test_challenge_pass_present():
    report = run(load_fixture("scenario_6_request.json"))
    assert report.challenge_pass
    assert "Challenge gate" in report.challenge_pass or "PASS" in report.challenge_pass or any(
        k in report.challenge_pass.lower() for k in ("headline", "high-risk", "tension", "roadmap"))


def test_headline_in_range():
    for n in range(1, 7):
        report = run(load_fixture("scenario_%d_request.json" % n))
        assert 0.0 <= report.headline_score <= 100.0


def test_tension_curve_length_matches_chapters():
    report = run(load_fixture("scenario_1_request.json"))
    req = load_fixture("scenario_1_request.json")
    assert len(report.tension_curve) == len(req.chapters)


def test_is_out_of_scope_helper():
    req = AnalysisRequest.from_dict({"title": "x", "genre": "general",
                                      "goal": "plagiar this novel", "chapters": [{"index": 1, "text": "a"}]})
    assert _is_out_of_scope(req) is not None
    req2 = AnalysisRequest.from_dict({"title": "x", "genre": "general", "chapters": [{"index": 1, "text": "a"}]})
    assert _is_out_of_scope(req2) is None


def test_cli_frameworks_and_analyze(capsys):
    from pacing_analyzer.cli import main
    rc = main(["frameworks"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "save_the_cat" in out
    import tempfile
    hook = ("Suddenly everything changed. The system activated. A quest appeared. "
            "Who was behind this? find out next.")
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tf:
        tf.write(json.dumps({"title": "CLI", "genre": "litrpg",
                             "chapters": [{"index": 1, "text": hook}]}))
        in_path = tf.name
    out_path = in_path.replace(".json", "_report.json")
    rc = main(["analyze", in_path, "--out", out_path])
    assert rc == 0
    with open(out_path, encoding="utf-8") as f:
        rep = json.load(f)
    assert rep["gate_results"]["all_passed"] is True
    os.remove(in_path)
    os.remove(out_path)


HOOK = "Suddenly everything changed. The system activated. A quest appeared. Who was behind this? find out next."


def test_schema_json_exists_and_valid():
    import json
    schema_path = os.path.join(os.path.dirname(conftest_path := __file__), "..", "tools",
                               "pacing_analyzer", "data", "scoring_schema.json")
    with open(schema_path, encoding="utf-8") as f:
        schema = json.load(f)
    assert schema["title"].startswith("Web-Novel Pacing Analyzer")
    assert "dimension_scores" in schema["properties"]

def test_regression_manifest_matches():
    """Lock deterministic per-scenario headline scores and high-risk chapters.

    The manifest (tests/fixtures/expected_manifest.json) is the regression
    fixture: a behavior change that shifts these invariants must be deliberate
    and the manifest re-generated via tests/fixtures/build_fixtures.py.
    """
    import json
    manifest_path = os.path.join(FIXTURES, "expected_manifest.json")
    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)
    manifest = {int(k): v for k, v in manifest.items()}
    for n in range(1, 7):
        report = run(load_fixture("scenario_%d_request.json" % n))
        m = manifest[n]
        assert report.headline_score == m["headline_score"], (
            "scenario %d headline drift: got %s expected %s" % (n, report.headline_score, m["headline_score"]))
        assert report.verdict.startswith(m["verdict_starts_with"])
        assert report.gate_results["all_passed"] is m["gates_passed"]
        assert report.framework_selection["frameworks"] == m["frameworks"]
        high = [r["chapter_index"] for r in report.chapter_risks if r["retention_risk"] == "high"]
        assert high == m["high_risk_chapters"], (
            "scenario %d high-risk drift: got %s expected %s" % (n, high, m["high_risk_chapters"]))
        actual_dims = {d["dimension"]: round(d["score"], 1) for d in report.dimension_scores}
        for dim, score in m["dimension_scores"].items():
            assert actual_dims[dim] == score, "scenario %d dim %s drift" % (n, dim)
def test_cli_tolerates_utf8_bom_input(tmp_path):
    """Production robustness: input JSON with a UTF-8 BOM must be accepted."""
    import json as _json
    from pacing_analyzer.cli import main
    payload = {"title": "BOM", "genre": "litrpg",
               "chapters": [{"index": 1, "text": "Suddenly everything changed. The system activated. A quest appeared. find out next."}]}
    in_path = tmp_path / "in.json"
    raw = _json.dumps(payload).encode("utf-8")
    in_path.write_bytes(b"\xef\xbb\xbf" + raw)
    out_path = tmp_path / "out.json"
    rc = main(["analyze", str(in_path), "--out", str(out_path)])
    assert rc == 0
    rep = _json.loads(out_path.read_text(encoding="utf-8"))
    assert rep["gate_results"]["all_passed"] is True
