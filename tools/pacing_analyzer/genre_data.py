"""genre_data.py — curated genre / trope / cadence knowledge base.

Offline, deterministic knowledge used by the trope matcher and the framework
selector. Kept in-code (no network) so production runs are reproducible. These
are reader-expectation conventions distilled from public craft resources and
platform trend patterns (Royal Road, Wattpad, WebNovel); the
``sub-trope-trend-updater`` extends them at runtime from SECOND-KNOWLEDGE-BRAIN
when a fresh crawl is available.
"""
from __future__ import annotations

from typing import Dict, List

# Canonical web-fiction genres we score against. Each entry holds the
# reader-expectation conventions that the trope matcher checks for.
GENRE_PROFILES: Dict[str, Dict[str, object]] = {
    "litrpg": {
        "expected_tropes": [
            "system_prompt", "status_window", "level_up", "skill_acquisition",
            "stat_block", "quest", "party", "dungeon", "respawn", "grind",
        ],
        "tension_driver": "progression + escalating stakes",
        "cadence_chapters_per_arc": 12,
        "target_word_count": 2200,
        "hook_must_appear_by_chapter": 1,
        "cliffhanger_density": 0.7,
        "inciting_incident_by_pct": 0.10,
    },
    "xianxia": {
        "expected_tropes": [
            "cultivation_realm", "dao_enlightenment", "spiritual_energy",
            "sect", "tournament", "face_slapping", "treasure", "breakthrough",
            "heavenly_tribulation", "longevity",
        ],
        "tension_driver": "power scaling + recurring rivals",
        "cadence_chapters_per_arc": 20,
        "target_word_count": 2000,
        "hook_must_appear_by_chapter": 1,
        "cliffhanger_density": 0.6,
        "inciting_incident_by_pct": 0.08,
    },
    "romance": {
        "expected_tropes": [
            "meet_cute", "forbidden_love", "misunderstanding", "grand_gesture",
            "rival_suitor", "emotional_vulnerability", "black_moment",
            "happily_ever_after",
        ],
        "tension_driver": "emotional push-pull + curiosity about the couple",
        "cadence_chapters_per_arc": 8,
        "target_word_count": 2500,
        "hook_must_appear_by_chapter": 1,
        "cliffhanger_density": 0.5,
        "inciting_incident_by_pct": 0.12,
    },
    "fantasy": {
        "expected_tropes": [
            "call_to_adventure", "mentor", "magic_system", "prophecy",
            "quest", "worldbuilding", "dark_lord", "allies", "setback", "final_battle",
        ],
        "tension_driver": "escalating external stakes",
        "cadence_chapters_per_arc": 15,
        "target_word_count": 2800,
        "cliffhanger_density": 0.55,
        "hook_must_appear_by_chapter": 2,
        "inciting_incident_by_pct": 0.15,
    },
    "scifi": {
        "expected_tropes": [
            "what_if", "technology", "first_contact", "society_division",
            "problem_solving", "sense_of_wonder", "twist", "hard_science",
        ],
        "tension_driver": "mystery + implication of the premise",
        "cadence_chapters_per_arc": 12,
        "target_word_count": 2600,
        "cliffhanger_density": 0.55,
        "hook_must_appear_by_chapter": 1,
        "inciting_incident_by_pct": 0.12,
    },
    "thriller": {
        "expected_tropes": [
            "inciting_crime", "ticking_clock", "investigator", "red_herring",
            "stakes_escalation", "betrayal", "climax_confrontation", "resolution",
        ],
        "tension_driver": "tension + page-turner pacing",
        "cadence_chapters_per_arc": 10,
        "target_word_count": 2400,
        "cliffhanger_density": 0.8,
        "hook_must_appear_by_chapter": 1,
        "inciting_incident_by_pct": 0.08,
    },
    "mystery": {
        "expected_tropes": [
            "crime", "detective", "clues", "suspects", "deduction",
            "false_solution", "reveal", "fair_play",
        ],
        "tension_driver": "curiosity gap + fair deduction",
        "cadence_chapters_per_arc": 10,
        "target_word_count": 2500,
        "cliffhanger_density": 0.5,
        "hook_must_appear_by_chapter": 1,
        "inciting_incident_by_pct": 0.10,
    },
    "horror": {
        "expected_tropes": [
            "threat", "isolation", "escalating_dread", "false_safety",
            "rules_of_survival", "final_girl", "revelation", "survival",
        ],
        "tension_driver": "dread + reader vulnerability",
        "cadence_chapters_per_arc": 9,
        "target_word_count": 2300,
        "cliffhanger_density": 0.65,
        "hook_must_appear_by_chapter": 1,
        "inciting_incident_by_pct": 0.10,
    },
    "slice_of_life": {
        "expected_tropes": [
            "everyday_setting", "character_moment", "small_stakes",
            "warmth", "seasonal_cadence", "growth_arc",
        ],
        "tension_driver": "character warmth + low-grade curiosity",
        "cadence_chapters_per_arc": 6,
        "target_word_count": 1800,
        "cliffhanger_density": 0.25,
        "hook_must_appear_by_chapter": 2,
        "inciting_incident_by_pct": 0.20,
    },
    "general": {
        "expected_tropes": [
            "hook", "inciting_incident", "rising_action", "midpoint_reversal",
            "climax", "resolution",
        ],
        "tension_driver": "balanced external + internal stakes",
        "cadence_chapters_per_arc": 12,
        "target_word_count": 2500,
        "cliffhanger_density": 0.55,
        "hook_must_appear_by_chapter": 1,
        "inciting_incident_by_pct": 0.12,
    },
}

# Lexicons for deterministic heuristic analysis (lowercased substrings).
HOOK_MARKERS: List[str] = [
    "suddenly", "but then", "everything changed", "until", "just when",
    "no one expected", "the truth was", "what nobody knew", "he never saw",
    "she never saw", "little did", "and then", "without warning", "out of nowhere",
]

CLIFFHANGER_MARKERS: List[str] = [
    "to be continued", "continued in", "next chapter", "what happened next",
    "before he could", "before she could", "and the door opened", "the figure",
    "the screen read", "the message", "...?", "ended abruptly", "cut to black",
    "stay tuned", "find out next",
]

OPEN_QUESTION_MARKERS: List[str] = [
    "who was", "what was", "why did", "where was", "how could", "was it",
    "could it be", "is this", "are they", "?",
]

TENSION_LEXICON = {
    # word -> tension weight (negative = calm, positive = tense)
    "fight": 0.8, "battle": 0.9, "kill": 0.9, "death": 0.7, "blood": 0.6,
    "danger": 0.7, "threat": 0.7, "fear": 0.6, "scream": 0.7, "attack": 0.8,
    "betrayal": 0.7, "enemy": 0.5, "war": 0.9, "chase": 0.7, "escape": 0.6,
    "crisis": 0.8, "deadline": 0.6, "explosion": 0.8, "trap": 0.6, "revenge": 0.7,
    "secret": 0.4, "mystery": 0.4, "reveal": 0.5, "shocking": 0.6, "shocked": 0.6,
    "trembled": 0.5, "raced": 0.5, "racing": 0.5, "desperate": 0.7,
    "calm": -0.4, "peace": -0.5, "quiet": -0.4, "rest": -0.5, "sleep": -0.4,
    "dream": -0.3, "memories": -0.3, "thoughtful": -0.4, "gentle": -0.4,
    "warm": -0.3, "smiled": -0.3, "comfort": -0.4, "soft": -0.3, "morning": -0.2,
}

INCITING_MARKERS: List[str] = [
    "inciting", "everything changed", "call to adventure", "the letter arrived",
    "the message", "summoned", "chosen", "awakened", "the system activated",
    "first quest", "the discovery", "the murder", "the accident", "news arrived",
]

MIDPOINT_MARKERS: List[str] = [
    "but the truth", "midpoint", "turning point", "everything shifted",
    "reversal", "the real enemy", "the real threat", "not what it seemed",
    "stake raised", "stake escalated", "raise the stakes",
]

CLIMAX_MARKERS: List[str] = [
    "final battle", "climax", "confrontation", "showdown", "last stand",
    "the ultimate", "final showdown", "decisive", "the end of",
]

RESOLUTION_MARKERS: List[str] = [
    "aftermath", "resolution", "after the battle", "the dust settled",
    "peace returned", "returned home", "happily ever after", "new normal",
    "epilogue",
]

BEAT_MARKERS: Dict[str, List[str]] = {
    "inciting": INCITING_MARKERS,
    "midpoint": MIDPOINT_MARKERS,
    "climax": CLIMAX_MARKERS,
    "resolution": RESOLUTION_MARKERS,
}
