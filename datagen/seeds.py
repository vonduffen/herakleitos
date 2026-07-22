"""Seed prompt bank for synthetic data generation.

PoC scale: a deterministic combinatorial bank across the plan's seven domains
and four task types. None of these scenarios overlaps with the gold set (the
filter additionally enforces decontamination), and no seed mentions Heraclitus
by name - the model must learn the moves, not the trigger word.

Full Phase 2 will grow this to >=2,000 seeds; the structure is already the
production one.
"""

from __future__ import annotations

from dataclasses import dataclass

MOVES = (
    "identity-through-change",
    "unity-of-opposites",
    "process-primacy",
    "measure-and-exchange",
    "tension-as-structure",
    "perspectival-opposition",
)

# domain -> concrete scenarios (kept disjoint from gold-set scenarios)
SCENARIOS: dict[str, list[str]] = {
    "technology": [
        "a database schema that has been migrated dozens of times while the "
        "application kept running",
        "a version-control history where every file has been rewritten but the "
        "project is 'the same repo'",
        "a cache that is only useful because its contents keep expiring",
        "a network protocol handshake that establishes a stable connection out "
        "of retries and timeouts",
        "a password that must keep changing to keep securing the same account",
        "an operating system updated in place for fifteen years",
    ],
    "relationships": [
        "a weekly phone call between siblings that has lasted thirty years",
        "a mentorship where the student now teaches the mentor",
        "a household's division of labor renegotiated after an illness",
        "a couple's shared vocabulary of private jokes that keeps being replaced",
        "an argument two friends have been having, in different forms, for years",
        "a neighbor relationship maintained entirely through small favors",
    ],
    "organizations": [
        "a night-shift crew whose members all changed but whose reputation "
        "persists",
        "a committee that only functions because two factions keep opposing "
        "each other",
        "a family restaurant handed down three generations with a changing menu",
        "an open-source project surviving its founder's departure",
        "a union and a management that define each other through negotiation",
        "a hospital ward that stays calm only through constant triage",
    ],
    "nature": [
        "a tidal pool whose inhabitants are exchanged with every tide",
        "a snowfield that persists through summer by melting and refreezing",
        "a migratory flock that is never the same birds two years running",
        "a topsoil layer maintained by continuous decomposition",
        "a beaver dam repaired nightly against the current that shapes it",
        "a scent trail that ants must keep re-walking to keep it existing",
    ],
    "mathematics": [
        "a running average that stays steady while every sample changes",
        "a sorting algorithm whose invariant holds only mid-motion",
        "a random walk whose distribution is perfectly predictable",
        "a feedback controller that holds a setpoint by never resting",
        "a proof by induction, where each step consumes and renews the claim",
        "two infinite series that converge to the same value along opposite "
        "paths",
    ],
    "personal_identity": [
        "a handwriting that stayed recognizable while every letterform drifted",
        "a childhood fear that became, transformed, an adult strength",
        "a diary whose author disagrees with every previous entry",
        "a skill maintained only by daily practice that keeps altering it",
        "a name kept through emigration while everything it referred to changed",
        "a scar that renews its own tissue while marking one past event",
    ],
    "politics": [
        "a ceasefire held in place by both sides' readiness to break it",
        "a law whose meaning is kept constant only by continual reinterpretation",
        "a public square repurposed by every generation of protest",
        "a treaty between countries whose governments keep changing",
        "an electoral system stable because power keeps changing hands",
        "a border town whose identity is made by what it separates",
    ],
}

TASK_TEMPLATES: dict[str, str] = {
    "analyze": "Analyze {scenario}. What persists, what changes, and how are the "
    "two related?",
    "dialogue": "Someone puzzled by {scenario} asks you to explain what is really "
    "going on. Answer them directly, in plain prose.",
    "respond-to-challenge": "A skeptic says about {scenario}: 'Underneath all the "
    "change there must be something fixed that stays what it is - otherwise "
    "nothing would persist.' Respond to the skeptic using this case.",
    "compress-an-argument": "In two or three sentences, state the sharpest true "
    "thing you can about {scenario}. No preamble, no summary of what you are "
    "about to say.",
}


@dataclass(frozen=True)
class Seed:
    id: str
    domain: str
    task_type: str
    prompt: str
    target_moves: tuple[str, ...]


def build_seeds() -> list[Seed]:
    seeds: list[Seed] = []
    task_names = list(TASK_TEMPLATES)
    n = 0
    for domain, scenarios in SCENARIOS.items():
        for scenario in scenarios:
            task = task_names[n % len(task_names)]
            moves = (MOVES[n % len(MOVES)], MOVES[(n + 2) % len(MOVES)])
            n += 1
            seeds.append(
                Seed(
                    id=f"seed-{n:04d}",
                    domain=domain,
                    task_type=task,
                    prompt=TASK_TEMPLATES[task].format(scenario=scenario),
                    target_moves=moves,
                )
            )
    return seeds


if __name__ == "__main__":
    ss = build_seeds()
    from collections import Counter

    print(f"{len(ss)} seeds")
    print(Counter(s.domain for s in ss))
    print(Counter(s.task_type for s in ss))
