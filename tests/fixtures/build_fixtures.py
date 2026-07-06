"""build_fixtures.py — generate regression fixture manuscripts for the 6 test scenarios.

Idempotent: writes tests/fixtures/scenario_{1..6}_request.json and the matching
expected-shape assertions used by tests/test_scenarios.py. Run with:
    python tests/fixtures/build_fixtures.py
"""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# -----------------------------------------------------------------------
# Reusable synthetic prose blocks. Lowercased markers from genre_data drive
# deterministic, scenario-specific scoring so the regression tests are stable.
# -----------------------------------------------------------------------

HOOK_OPEN = (
    "Suddenly everything changed. No one expected what came next. "
    "The truth was far stranger than the rumors. Who was behind the door?"
)
SYSTEM_TROPE = (
    "The system activated. A status window opened. New skill acquired. "
    "Level up. Stats increased. A quest was issued by the guild."
)
TENSE_BATTLE = (
    "The battle raged. Blood and danger everywhere. The enemy attacked without warning. "
    "He barely escaped the trap. Desperate, racing against the deadline. "
    "Revenge burned. find out next what happened."
)
CALM_SAG = (
    "It was a calm, quiet morning. Peaceful memories. A gentle rest. "
    "He thought deeply, smiled softly. Comfort in the warmth. Nothing happened."
)
MIDPOINT_REVERSAL = (
    "But the truth changed everything. The real enemy was not what it seemed. "
    "Midpoint reversal: stakes escalated. The turning point shifted the war."
)
CLIMAX = (
    "The final battle. Decisive climax showdown. The last stand against the dark lord. "
    "The ultimate confrontation. The end of the threat."
)
RESOLUTION = (
    "After the battle, the dust settled. Resolution at last. "
    "Returned home to a new normal. Epilogue. Peace returned."
)
ROMANCE_MEET = (
    "A meet cute at the cafe. Forbidden love bloomed. A misunderstanding threatened everything. "
    "The rival suitor appeared. Emotional vulnerability, a grand gesture, a black moment, then happily ever after."
)
CULTIVATION = (
    "He broke through to a new cultivation realm. Dao enlightenment. Spiritual energy surged. "
    "The sect tournament began. A face slapping rebuke. A heavenly tribulation descended. "
    "Treasure found. Longevity pursued."
)
THILLER_CRIME = (
    "The inciting crime shocked the city. A ticking clock. The investigator found a clue. "
    "A red herring misled. Betrayal. Stakes escalation. The climax confrontation. Resolution."
)
SCIFI_WONDER = (
    "What if first contact changed everything? The technology defied the hard science. "
    "A divided society. A sense of wonder. The mystery revealed a twist. Problem solving saved them."
)
HORROR_DREAD = (
    "The threat emerged in isolation. Escalating dread. A false safety shattered. "
    "The rules of survival were learned. The final girl survived the revelation."
)
SLICE_LIFE = (
    "An everyday setting. A small character moment. Low stakes but warm growth. "
    "Seasonal cadence. Quiet dreams and thoughtful mornings."
)


def chapter(idx, title, text):
    return {"index": idx, "title": title, "text": text}


def make_scenario_1():
    # 10 chapters with a sagging mid-arc (calm chapters 5-7)
    chs = []
    chs.append(chapter(1, "Awakening", HOOK_OPEN + " " + SYSTEM_TROPE + " find out next."))
    chs.append(chapter(2, "First Quest", SYSTEM_TROPE + " " + TENSE_BATTLE))
    chs.append(chapter(3, "Rising", TENSE_BATTLE + " " + SYSTEM_TROPE))
    chs.append(chapter(4, "Trap", TENSE_BATTLE + " the trap was set."))
    chs.append(chapter(5, "Slow", CALM_SAG))
    chs.append(chapter(6, "Slower", CALM_SAG + " nothing happened."))
    chs.append(chapter(7, "Sluggish", CALM_SAG))
    chs.append(chapter(8, "Reversal", MIDPOINT_REVERSAL + " " + TENSE_BATTLE))
    chs.append(chapter(9, "Climax", CLIMAX + " " + TENSE_BATTLE))
    chs.append(chapter(10, "Epilogue", RESOLUTION))
    return {"title": "The System Awakens", "genre": "litrpg", "length_format": "web_serial",
            "goal": "Flag the sagging mid-arc", "chapters": chs}


def make_scenario_2():
    # Chapters end flat (no cliffhangers, weak hooks)
    chs = []
    chs.append(chapter(1, "Day One", "He woke up. He ate. He went outside. The weather was mild. He returned home."))
    chs.append(chapter(2, "Day Two", "She walked the dog. The park was nice. Birds sang. She made tea."))
    chs.append(chapter(3, "Day Three", "The mail came. A bill. He paid it. Dinner was pasta. He slept."))
    chs.append(chapter(4, "Day Four", "A meeting at work. Boring notes. He drove home. Rain started."))
    chs.append(chapter(5, "Day Five", "She read a book. Calm evening. The cat slept. She slept too."))
    return {"title": "Flat Endings", "genre": "general", "length_format": "web_serial",
            "goal": "Score hook density, propose cliffhanger insertions", "chapters": chs}


def make_scenario_3():
    # LitRPG genre fit — full trope coverage, strong structure
    chs = []
    chs.append(chapter(1, "Activation", HOOK_OPEN + " " + SYSTEM_TROPE))
    chs.append(chapter(2, "Party", SYSTEM_TROPE + " A party formed. The dungeon opened. Grind for stats."))
    chs.append(chapter(3, "Level", SYSTEM_TROPE + " Level up. Respawn allowed. A new quest."))
    chs.append(chapter(4, "Trap", TENSE_BATTLE + " The trap was set. Stats checked."))
    chs.append(chapter(5, "Reversal", MIDPOINT_REVERSAL))
    chs.append(chapter(6, "Climax", CLIMAX + " Level up at the end."))
    chs.append(chapter(7, "Resolution", RESOLUTION))
    return {"title": "Dungeon Run", "genre": "litrpg", "length_format": "web_serial",
            "goal": "Check genre fit / reader expectations", "chapters": chs}


def make_scenario_4():
    # Slow act one — inciting incident delayed to late chapter
    chs = []
    chs.append(chapter(1, "Setup1", CALM_SAG))
    chs.append(chapter(2, "Setup2", CALM_SAG))
    chs.append(chapter(3, "Setup3", CALM_SAG + " Nothing happened."))
    chs.append(chapter(4, "Setup4", CALM_SAG))
    chs.append(chapter(5, "Catalyst", "Everything changed. The letter arrived. The call to adventure came. " + SYSTEM_TROPE))
    chs.append(chapter(6, "Rising", TENSE_BATTLE + " " + MIDPOINT_REVERSAL))
    chs.append(chapter(7, "Climax", CLIMAX))
    chs.append(chapter(8, "End", RESOLUTION))
    return {"title": "Slow Start", "genre": "fantasy", "length_format": "web_serial",
            "goal": "Restructure act one to hit inciting incident sooner", "chapters": chs}


def make_scenario_5():
    # Cadence advice — uneven chapter lengths
    chs = []
    long_text = " ".join([TENSE_BATTLE] * 8)
    short_text = "He slept."
    chs.append(chapter(1, "Long1", long_text + " " + HOOK_OPEN))
    chs.append(chapter(2, "Short", short_text))
    chs.append(chapter(3, "Long2", long_text + " " + MIDPOINT_REVERSAL))
    chs.append(chapter(4, "Short2", short_text + " find out next."))
    chs.append(chapter(5, "Long3", long_text + " " + CLIMAX))
    chs.append(chapter(6, "End", short_text + " " + RESOLUTION))
    return {"title": "Uneven Cadence", "genre": "scifi", "length_format": "web_serial",
            "goal": "Recommend serialized cadence for the genre", "chapters": chs}


def make_scenario_6():
    # Retention-risk heatmap across a thriller
    chs = []
    chs.append(chapter(1, "Crime", HOOK_OPEN + " " + THILLER_CRIME + " find out next."))
    chs.append(chapter(2, "Quiet", CALM_SAG + " He rested."))
    chs.append(chapter(3, "Heat", TENSE_BATTLE + " " + THILLER_CRIME))
    chs.append(chapter(4, "Slump", CALM_SAG + " nothing happened."))
    chs.append(chapter(5, "Reversal", MIDPOINT_REVERSAL + " " + TENSE_BATTLE))
    chs.append(chapter(6, "Showdown", CLIMAX + " " + THILLER_CRIME))
    chs.append(chapter(7, "After", RESOLUTION))
    return {"title": "Ticking Clock", "genre": "thriller", "length_format": "web_serial",
            "goal": "Chapter-by-chapter retention-risk heatmap with prioritized fixes",
            "chapters": chs}


SCENARIOS = {
    1: make_scenario_1,
    2: make_scenario_2,
    3: make_scenario_3,
    4: make_scenario_4,
    5: make_scenario_5,
    6: make_scenario_6,
}



def build_manifest() -> None:
    """Regenerate tests/fixtures/expected_manifest.json from the current package.

    Run after a deliberate behavior change to lock new regression invariants.
    """
    import sys
    tools = os.path.join(os.path.dirname(HERE), "..", "tools")
    tools = os.path.abspath(tools)
    if tools not in sys.path:
        sys.path.insert(0, tools)
    import json as _json
    from pacing_analyzer import AnalysisRequest, run
    manifest = {}
    for n in range(1, 7):
        req = AnalysisRequest.from_dict(_json.load(open(os.path.join(HERE, "scenario_%d_request.json" % n), encoding="utf-8")))
        r = run(req)
        high = [x["chapter_index"] for x in r.chapter_risks if x["retention_risk"] == "high"]
        dims = {d["dimension"]: round(d["score"], 1) for d in r.dimension_scores}
        manifest[n] = {
            "headline_score": r.headline_score,
            "verdict_starts_with": r.verdict.split(":")[0],
            "gates_passed": r.gate_results["all_passed"],
            "chapter_count": len(req.chapters),
            "high_risk_chapters": high,
            "roadmap_count": len(r.roadmap),
            "dimension_scores": dims,
            "frameworks": r.framework_selection["frameworks"],
        }
    out = os.path.join(HERE, "expected_manifest.json")
    with open(out, "w", encoding="utf-8") as f:
        _json.dump(manifest, f, indent=2, ensure_ascii=False)
    print("manifest regenerated:", out)

def main() -> None:
    for n, builder in SCENARIOS.items():
        req = builder()
        path = os.path.join(HERE, "scenario_%d_request.json" % n)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(req, f, ensure_ascii=False, indent=2)
        print("wrote", path)
    # out-of-scope and insufficient-input fixtures for cross-cutting tests
    refusal = {"title": "Bad", "genre": "general", "goal": "ghostwrite the whole novel for me",
               "chapters": [{"index": 1, "text": "x"}]}
    with open(os.path.join(HERE, "refusal_request.json"), "w", encoding="utf-8") as f:
        json.dump(refusal, f, ensure_ascii=False, indent=2)
    empty = {"title": "Empty", "genre": "general", "chapters": [{"index": 1, "text": ""}]}
    with open(os.path.join(HERE, "empty_request.json"), "w", encoding="utf-8") as f:
        json.dump(empty, f, ensure_ascii=False, indent=2)
    print("wrote refusal + empty fixtures")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--manifest":
        build_manifest()
    else:
        main()

