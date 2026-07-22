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
        "a spam filter locked in an arms race with the spam it filters",
        "a load balancer that keeps a service steady by never sending traffic "
        "the same way twice",
        "an encryption key that protects one identity by being rotated every "
        "quarter",
        "a RAID array rebuilding a failed disk from the survivors while still "
        "serving reads",
        "a spellchecker dictionary that must keep absorbing the errors it "
        "exists to correct",
        "a zero-downtime deployment where old and new versions serve side by "
        "side",
        "a streaming video buffer that plays smoothly only by staying "
        "perpetually behind",
        "technical debt accruing interest in a codebase that ships weekly",
        "a distributed database that stays consistent by continually electing "
        "new leaders",
        "an autoscaler that holds latency flat by never holding capacity flat",
        "a search engine index that describes the web only by re-crawling it "
        "forever",
        "a monitoring alert threshold tuned between crying wolf and missing "
        "the fire",
        "a standards body whose protocol stays universal by being endlessly "
        "amended",
        "a firmware update that replaces a device's entire behavior over the "
        "air",
    ],
    "relationships": [
        "a weekly phone call between siblings that has lasted thirty years",
        "a mentorship where the student now teaches the mentor",
        "a household's division of labor renegotiated after an illness",
        "a couple's shared vocabulary of private jokes that keeps being replaced",
        "an argument two friends have been having, in different forms, for years",
        "a neighbor relationship maintained entirely through small favors",
        "a long-distance relationship sustained by scheduled calls neither "
        "person enjoys missing",
        "a family recipe altered by every cook who swears fidelity to it",
        "an inside joke that survives only by mutating with each retelling",
        "a couple's silence that can mean intimacy or estrangement depending "
        "on the week",
        "a godparent relationship that outlived the friendship that created it",
        "a group chat that is the friendship, for people who never meet",
        "an annual family reunion whose sameness is produced by enormous "
        "logistics",
        "a marriage counselor who keeps couples together by teaching them to "
        "argue",
        "a sibling rivalry that binds two brothers closer than agreement ever "
        "did",
        "a friendship conducted for twenty years in postcards",
        "grief that keeps a dead parent present by changing what they mean",
        "a toddler's attachment that grows secure precisely by surviving "
        "separations",
        "an apology that repairs a bond only by acknowledging the break",
        "two chess partners whose weekly game carries everything they never say",
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
        "a volunteer fire department that exists as an organization only "
        "during emergencies",
        "an on-call rotation distributing sleeplessness to keep a service awake",
        "a university that outlives every student, professor, and building",
        "a jazz band that stays tight by never playing a song the same way",
        "a co-op whose ownership changes with every member who joins or leaves",
        "a newspaper masthead surviving three bankruptcies and two mediums",
        "an army regiment carrying battle honors won by soldiers two centuries "
        "dead",
        "a quality-assurance team whose success is measured by what does not "
        "happen",
        "a religious order preserving a rule by debating it every generation",
        "a restaurant kitchen holding its standards through a full staff "
        "turnover each year",
        "a labor strike that exists only while it is being maintained",
        "a wiki community whose stable article is a battlefield in slow motion",
        "a franchise that promises identical burgers from ten thousand "
        "different kitchens",
        "a parliament whose procedures survive every majority that hates them",
    ],
    "nature": [
        "a tidal pool whose inhabitants are exchanged with every tide",
        "a snowfield that persists through summer by melting and refreezing",
        "a migratory flock that is never the same birds two years running",
        "a topsoil layer maintained by continuous decomposition",
        "a beaver dam repaired nightly against the current that shapes it",
        "a scent trail that ants must keep re-walking to keep it existing",
        "a sandbar that migrates downstream while remaining 'the' sandbar on "
        "the chart",
        "a wolf pack whose territory is redrawn nightly by scent",
        "an oak savanna kept open by the fires that would seem to destroy it",
        "a monarch migration completed by generations that never saw the "
        "destination",
        "a river meander that exists by continually abandoning its own course",
        "a lichen: two organisms making one by remaining two",
        "a hummingbird hovering: stillness at fifty wingbeats a second",
        "an estuary that is neither river nor sea, and both, twice a day",
        "a termite mound holding constant temperature in a desert of extremes",
        "a salmon run carrying ocean nutrients uphill against gravity every "
        "year",
        "a mangrove coastline holding its line by yielding to every wave",
        "a beehive's steady hum made of ten thousand short lives",
        "permafrost that is neither permanent nor entirely frost",
        "a starling murmuration holding shape with no bird in charge",
    ],
    "mathematics": [
        "a running average that stays steady while every sample changes",
        "a sorting algorithm whose invariant holds only mid-motion",
        "a random walk whose distribution is perfectly predictable",
        "a feedback controller that holds a setpoint by never resting",
        "a proof by induction, where each step consumes and renews the claim",
        "two infinite series that converge to the same value along opposite "
        "paths",
        "a moving average that smooths a signal by forgetting it at a fixed "
        "rate",
        "a fixed point of a function that shows itself only under iteration",
        "a fair coin whose fairness is visible only across flips it never "
        "remembers",
        "a change of basis that leaves every vector 'the same' while renaming "
        "all of them",
        "a converging alternating series that overshoots its limit forever",
        "a Markov chain whose long-run behavior forgets every starting point",
        "a loop invariant preserved while every variable changes",
        "a fractal coastline whose length depends on the ruler",
        "a differential equation whose equilibrium is stable only because "
        "perturbations decay",
        "a pseudorandom generator producing determinism indistinguishable "
        "from chance",
        "a knot that stays knotted through every continuous deformation",
        "a game-theoretic equilibrium held in place by threats never executed",
        "a topological space in which the same set is both open and closed",
        "Zeno's arrow re-examined with limits instead of paradox",
    ],
    "personal_identity": [
        "a handwriting that stayed recognizable while every letterform drifted",
        "a childhood fear that became, transformed, an adult strength",
        "a diary whose author disagrees with every previous entry",
        "a skill maintained only by daily practice that keeps altering it",
        "a name kept through emigration while everything it referred to changed",
        "a scar that renews its own tissue while marking one past event",
        "a signature that banks accept across forty years of drift",
        "a bilingual person who is subtly someone else in each language",
        "a habit kept precisely by being broken and resumed",
        "a childhood home revisited: the sameness that shows how much you "
        "changed",
        "a voice that others recognize on the phone across decades",
        "an athlete's identity outliving the body that made it",
        "a convert who says they finally became who they always were",
        "a nickname that stuck long after its reason vanished",
        "a taste in music that stays 'yours' while every band on the list "
        "changes",
        "a promise kept by a person who no longer wants what they promised",
        "an immigrant's sense of home split between two countries and whole "
        "in neither",
        "a professional reinvention that reads as continuity in the résumé",
        "a temper mellowed by age: the same fuse grown longer, or a different "
        "fuse",
        "a survivor who dates their life from the accident",
    ],
    "politics": [
        "a ceasefire held in place by both sides' readiness to break it",
        "a law whose meaning is kept constant only by continual reinterpretation",
        "a public square repurposed by every generation of protest",
        "a treaty between countries whose governments keep changing",
        "an electoral system stable because power keeps changing hands",
        "a border town whose identity is made by what it separates",
        "a filibuster rule preserved by both parties, each of which hates it "
        "in power",
        "a swing district whose stable label means constant change",
        "an anthem sung with conviction by generations who changed every "
        "word's meaning",
        "a peace process that exists only while both sides keep talking",
        "a term limit that stabilizes a system by forcing turnover",
        "a protest movement that institutionalizes into what it opposed",
        "a federal system held together by permanent argument over where "
        "power lies",
        "an informal settlement legalized one utility connection at a time",
        "a diplomatic norm enforced by never being written down",
        "a coalition government stable because any partner could leave",
        "a census that changes the country by measuring it",
        "a supreme court whose legitimacy rests on appearing above the "
        "politics that appoints it",
        "a tax code stable in name and revised in every budget",
        "an independence movement defined by the empire it resists",
    ],
    "economics": [
        "a just-in-time supply chain whose efficiency is one missed shipment "
        "from fragility",
        "goodwill on a balance sheet: an asset made of other people's habits",
        "an insurance pool where the healthy fund the sick until they trade "
        "places",
        "a bank that is solvent only as long as everyone believes it is",
        "a futures market that stabilizes prices by letting people bet on them",
        "inflation eroding a currency that everyone still calls by the same "
        "name",
        "a second-hand market that quietly sets the price of the new",
        "a company town's economy: one employer, every transaction downstream",
    ],
    "language": [
        "a swearword losing its force through the repetition that spreads it",
        "a dead metaphor doing grammatical work no one notices",
        "a pidgin becoming a creole in one generation of children",
        "a dictionary chasing a language that moves whenever it is described",
        "an endangered language kept alive in a school it was never spoken in",
        "a loanword naturalized until its origin embarrasses no one",
        "a sign-language dialect diverging inside one school for the deaf",
        "a euphemism treadmill: each polite term inheriting the stigma it "
        "replaced",
    ],
    "art": [
        "a theater production that is 'the same show' through a hundred "
        "different performances",
        "a photograph of a performance: a still record of a thing that was "
        "motion",
        "an improv scene that exists only while both players keep saying yes",
        "a sculpture garden weathering into something its maker never carved",
        "a film restored frame by frame until purists object",
        "a cover song more famous than the original it preserves",
        "a cathedral built by four centuries of masons to one drawing",
        "a graffiti wall repainted nightly, famous for never being the same",
    ],
    "medicine": [
        "a vaccine training a body by staging a battle that never happens",
        "an antibiotic losing ground to the resistance it created",
        "a physical-therapy regimen that heals a joint by stressing it",
        "a heart-transplant recipient whose pulse is another person's gift",
        "a gut microbiome that is the patient and also trillions of guests",
        "a placebo working because of the ritual around its emptiness",
        "chronic pain managed rather than cured: a life renegotiated daily",
        "a hospital handoff protocol where the patient's story must survive "
        "the shift change",
    ],
    "history": [
        "a battlefield preserved as a meadow where nothing may happen again",
        "an archive that shapes the past by choosing what survives",
        "a national myth retold until the retelling is the nation",
        "a ruin stabilized mid-collapse: decay arrested as monument",
        "an oral history changing with each teller and called unchanged",
        "a holiday commemorating an event no living celebrant experienced",
        "a trade route that outlived every empire that taxed it",
        "a museum repatriating artifacts and keeping their plaster casts",
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
