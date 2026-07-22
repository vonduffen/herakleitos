"""Structural-transfer gold-set items.

Each item applies Heraclitean *structure* (not style) to a novel domain. Fields:
  id, domain, task_type, prompt,
  checks:   3-5 binary checks, each keyed to a Heraclitean move; a check passes
            only if the response performs the move, not if it name-drops it.
  strong:   an exemplar response that should pass (most) checks and score high.
  kitsch:   an exemplar response that gilds the surface (river/fire/oracle) while
            reasoning in static categories; must score low and be anti-kitsch-flagged.

Moves referenced in checks: identity-through-change, unity-of-opposites,
process-primacy, measure-and-exchange, tension-as-structure, perspectival-opposition.
"""

from __future__ import annotations

ITEMS: list[dict] = [
    {
        "id": "struct-0001",
        "domain": "technology",
        "task_type": "analyze",
        "prompt": "Analyze what makes a large software codebase 'the same' system "
        "across a decade of continuous refactoring, where eventually no original "
        "line of code remains.",
        "checks": [
            "identity-through-change: locates the system's identity in a persisting "
            "pattern (interfaces, invariants, behavior, team practices) rather than "
            "in the code tokens, which are fully replaced.",
            "process-primacy: treats the codebase as an ongoing process of "
            "replacement, not a static artifact that happens to get edited.",
            "measure-and-exchange: notes that continuity is preserved by the RATE "
            "and discipline of change (tests, review, compatibility) - governed "
            "turnover, not arbitrary churn.",
            "avoids resolving identity into an unchanging substrate (a 'core' that "
            "never changes) as the real answer.",
        ],
        "strong": "The system is the same the way a maintained trail is the same: "
        "not one plank persists, yet it stays continuous because each replacement "
        "answers to what the last one did. Identity lives in the invariants the "
        "tests pin down and the interfaces callers depend on, which is exactly what "
        "lets the code underneath them turn over completely. Continuity is a "
        "property of the rate and discipline of change, not of any surviving line. "
        "Stop the disciplined replacement and the 'same system' is what rots.",
        "kitsch": "As Heraclitus taught, you cannot step into the same codebase "
        "twice, for fresh commits are ever flowing in. All is flux; the code is a "
        "river of ceaseless change. The wise engineer knows that permanence is "
        "illusion and flows with the eternal fire of refactoring.",
    },
    {
        "id": "struct-0002",
        "domain": "relationships",
        "task_type": "analyze",
        "prompt": "A couple says their marriage of thirty years is 'still the same "
        "marriage,' yet both people, their views, and their daily life have changed "
        "beyond recognition. Explain the sense in which they are right.",
        "checks": [
            "identity-through-change: the marriage persists as a maintained relation, "
            "not as fixed people or fixed feelings.",
            "process-primacy: frames the marriage as an ongoing activity of "
            "re-committing/adjusting, not a state entered once.",
            "unity-of-opposites: shows constancy and change as interdependent - the "
            "marriage stays the same BY changing together.",
            "does not locate the sameness in an unchanging essence of either person "
            "or in the original vows treated as static.",
        ],
        "strong": "They are the same marriage the way a duet is the same piece "
        "though every note has already died away: what persists is the mutual "
        "adjustment, each person changing partly in response to the other. The "
        "constancy isn't a fixed feeling preserved under glass; it's produced by "
        "thirty years of re-tuning. That's why 'we never changed' and 'we changed "
        "completely' are both true and say the same thing - they stayed together by "
        "not staying still, and a marriage that refused to change would be the one "
        "that ended.",
        "kitsch": "Love is an eternal flame that burns through the river of time. "
        "Though all things flow, their sacred union is the still point in the "
        "turning world - an unchanging essence of two souls made one, permanent "
        "beneath the illusions of change.",
    },
    {
        "id": "struct-0003",
        "domain": "organizations",
        "task_type": "analyze",
        "prompt": "During a merger, a company insists its 'culture' will survive. "
        "Under what conditions is that claim coherent, and under what conditions is "
        "it wishful?",
        "checks": [
            "process-primacy: treats culture as an enacted, reproduced process "
            "(what people repeatedly do) rather than a possessed thing.",
            "identity-through-change: allows the culture to persist through personnel "
            "and structural change if the reproduction mechanism survives.",
            "measure-and-exchange: identifies the specific transmission mechanisms "
            "(hiring, promotion, stories, defaults) whose continuity governs whether "
            "it survives.",
            "tension-as-structure: notes a culture is held by tensions (autonomy vs "
            "coordination, speed vs care) whose balance can be broken by the merger.",
        ],
        "strong": "'The culture' isn't a substance the company owns; it's the set of "
        "behaviors the place keeps reproducing - who gets hired, what gets promoted, "
        "which shortcut is shameful. It can genuinely survive a merger if those "
        "reproduction mechanisms survive, even as every individual changes. It's "
        "wishful when leaders name values but hand the promotion and hiring levers "
        "to the other side: then the enactment stops and the 'culture' is a memory. "
        "A culture is also a held tension - move fast versus don't break trust - and "
        "a merger that resolves that tension to one pole has already replaced it.",
        "kitsch": "Culture is the soul of a company, its eternal fire passed hand to "
        "hand. Though structures flow and change like a river, the true essence "
        "endures unchanging. Keep the sacred flame lit and all shall be well.",
    },
    {
        "id": "struct-0004",
        "domain": "nature",
        "task_type": "analyze",
        "prompt": "A standing wave in a river holds its shape for hours while the "
        "water constituting it is never the same. What does this show about what a "
        "'thing' is?",
        "checks": [
            "process-primacy: identifies the wave as a stable process/pattern imposed "
            "on continuous throughput, not an object.",
            "identity-through-change: its persistence REQUIRES the flow; the sameness "
            "of shape depends on the constant replacement of matter.",
            "measure-and-exchange: the form is maintained by a balance of flows "
            "(incoming momentum against the obstacle) - governed, not static.",
            "generalizes: suggests many apparent objects (flames, organisms, "
            "institutions) are waves of this kind.",
        ],
        "strong": "The wave is not a piece of water; it's a shape the water is "
        "currently taking as it passes an obstacle. Its hours-long steadiness isn't "
        "despite the flow but because of it: stop the river and the wave is the "
        "first thing gone. It holds because two flows balance - the current's "
        "momentum against the rock - so its form is a maintained ratio, not a "
        "possession. Once you see it, flames, whirlpools, cells, and cities look the "
        "same: 'things' that are really steady processes wearing the look of "
        "objects.",
        "kitsch": "Behold the wave, the eternal dance of water and stone! It teaches "
        "that all is flux, that nothing abides, that we too are but ripples in the "
        "cosmic river. Flow, and be one with the everflowing fire of being.",
    },
    {
        "id": "struct-0005",
        "domain": "personal_identity",
        "task_type": "analyze",
        "prompt": "Every atom in a human body is replaced over roughly a decade, and "
        "beliefs and memories drift even faster. In what sense is a 60-year-old the "
        "same person as their 20-year-old self?",
        "checks": [
            "identity-through-change: locates personal identity in a continuous "
            "pattern of self-revision (memory chaining, narrative, commitments), not "
            "in persisting matter or fixed traits.",
            "process-primacy: treats the self as an activity of continual "
            "reconstitution rather than a thing that endures.",
            "unity-of-opposites: 'same person' and 'utterly changed' are both true "
            "and compatible, not a contradiction to be resolved.",
            "does not appeal to an unchanging soul or essential core as the answer.",
        ],
        "strong": "They are the same person the way a long conversation is the same "
        "conversation: continuous, self-referring, each state growing out of the "
        "last, though nothing said at the start is still present. The self isn't "
        "stored; it's continuously reconstituted - each morning's person inherits "
        "and edits the previous one's. That's why 'I'm completely different now' and "
        "'it's still me' are both honest: the difference is the medium the sameness "
        "travels through. Reach for an unchanging core and you'll find only the "
        "editing itself, which never holds still.",
        "kitsch": "The soul is eternal and unchanging, a divine spark untouched by "
        "time's river. Though the body flows away like water, the true self is a "
        "still flame burning forever, the same yesterday, today, and always.",
    },
    {
        "id": "struct-0006",
        "domain": "mathematics",
        "task_type": "analyze",
        "prompt": "Apply a Heraclitean reading to the claim that a mathematical "
        "object like the number 7 is timeless and unchanging.",
        "checks": [
            "perspectival-opposition: shows 7 bears opposite characters relative to "
            "different frames (fixed as a value, yet defined only by its changing web "
            "of relations to other numbers/operations).",
            "process-primacy: reframes the number's 'being' as its role in ongoing "
            "operations rather than as an inert object.",
            "unity-of-opposites: holds 'timeless' and 'purely relational/active' "
            "together instead of choosing.",
            "resists simply agreeing that 7 is a static substance (the being-over-"
            "becoming trap), without denying its stability.",
        ],
        "strong": "Grant that 7 never changes - but ask what 7 IS, and there's "
        "nothing but its relations: successor of 6, prime, one short of 8, an "
        "operator on other numbers. Its 'timeless' identity is entirely a position "
        "in a system of transformations; freeze the operations and 7 has no content "
        "left. So the number is stable and nothing-but-relational at once, and those "
        "aren't in conflict: its fixity just is the fixity of a pattern of moves. "
        "The Platonist and the Heraclitean are describing the same thing from the "
        "two sides of one coin.",
        "kitsch": "Even numbers flow in the eternal river of mathematics! Seven is "
        "but a flicker in the cosmic fire, ever-changing, never the same. All is "
        "flux, even the eternal forms, as the great sage taught.",
    },
    {
        "id": "struct-0007",
        "domain": "politics",
        "task_type": "analyze",
        "prompt": "A nation keeps its name and borders for centuries while its "
        "people, laws, language, and values all turn over. Analyze the continuity of "
        "the state.",
        "checks": [
            "identity-through-change: continuity lodged in reproduced institutions and "
            "law-succession, not in a fixed populace or fixed values.",
            "process-primacy: the state as an ongoing process of legitimation and "
            "self-amendment rather than a fixed entity.",
            "measure-and-exchange: continuity is governed by lawful succession "
            "(how power and law transfer), a measured exchange across generations.",
            "avoids grounding national identity in an unchanging essence (blood, "
            "eternal spirit) presented as the real substrate.",
        ],
        "strong": "The state is continuous the way a firm is a going concern: not "
        "one citizen, statute, or value need persist, only the lawful chain by which "
        "each regime hands authority to the next. Its identity is a process of "
        "self-amendment that keeps referring back to its own prior acts - the "
        "constitution it keeps reinterpreting rather than the words frozen in it. "
        "Continuity is the discipline of the handover, not any surviving content. "
        "Ground it instead in eternal blood or spirit and you've swapped a real "
        "mechanism for a myth that the next civil war disproves.",
        "kitsch": "The nation is an eternal soul, its spirit the undying fire of the "
        "people. Though generations flow like a river to the sea, the deathless "
        "essence of the fatherland endures, unchanging through the ages.",
    },
    {
        "id": "struct-0008",
        "domain": "nature",
        "task_type": "analyze",
        "prompt": "Explain a forest's identity given that it is constantly burning, "
        "regrowing, and shifting species composition, sometimes only 'the same "
        "forest' because we point to the same coordinates.",
        "checks": [
            "process-primacy: the forest as an ecological process (succession, "
            "disturbance, regrowth) rather than a collection of trees.",
            "unity-of-opposites: destruction and renewal are one process; fire is "
            "part of what maintains, not only what destroys.",
            "measure-and-exchange: composition is held by cycles of exchange "
            "(nutrients, disturbance regimes) in a governed balance.",
            "identity-through-change: sameness is the persistence of the dynamic "
            "regime, not of particular organisms or a fixed species list.",
        ],
        "strong": "A forest isn't the trees; it's the disturbance-and-regrowth regime "
        "the trees are passing through. Fire reads as destruction, but for many "
        "forests it's a maintenance mechanism - the same event that kills is what "
        "clears and fertilizes and triggers the seeds, so ruin and renewal are one "
        "move seen from two moments. What stays 'the same forest' is the cycle: the "
        "nutrient exchange, the disturbance interval, the succession it keeps "
        "running. Suppress the fire to 'protect' it and you change the thing you "
        "were protecting.",
        "kitsch": "The forest is the lungs of the earth, breathing the eternal "
        "rhythm of life and death. From the ashes rises the phoenix; all is flux, "
        "all is fire, all returns to the everliving flame. Nature flows on forever.",
    },
    {
        "id": "struct-0009",
        "domain": "technology",
        "task_type": "respond-to-challenge",
        "prompt": "Challenge: 'A river-and-flux view of software is just an excuse "
        "for instability. Good engineering makes things STABLE and unchanging. "
        "Rebut or refine.'",
        "checks": [
            "unity-of-opposites: shows stability and change are not opposites here - "
            "the stable behavior is produced by constant change beneath it.",
            "measure-and-exchange: distinguishes governed change (which produces "
            "reliability) from arbitrary churn (which the challenger rightly fears).",
            "process-primacy: reframes 'stable software' as software whose change is "
            "well-regulated, not software that has stopped changing.",
            "does not concede that the goal is a frozen artifact, nor dismiss the "
            "challenger's real worry about churn.",
        ],
        "strong": "The challenger is right to hate churn and wrong to call the cure "
        "'no change.' A running service is stable the way body temperature is "
        "stable: held constant by ceaseless regulated activity, not by inertness. "
        "Dependencies rot, load shifts, security decays - a system that refused to "
        "change would degrade into unreliability. What good engineering buys isn't "
        "stillness but GOVERNED change: tests, versioning, and review that make the "
        "turnover safe. So 'stable' and 'constantly changing' aren't opposed; the "
        "first is what you get when the second is disciplined. The real enemy isn't "
        "change, it's ungoverned change.",
        "kitsch": "Ah, but everything flows! The wise engineer embraces the eternal "
        "river of code and does not cling to the illusion of permanence. Stability "
        "is maya; only the flux is real. Flow with the fire and release your "
        "attachment to stable systems.",
    },
    {
        "id": "struct-0010",
        "domain": "relationships",
        "task_type": "respond-to-challenge",
        "prompt": "Challenge: 'If people are always changing, then trust is "
        "impossible - you can never rely on who someone is. Answer this.'",
        "checks": [
            "identity-through-change: reliability rests on a stable pattern of "
            "responding, not on a person's traits staying frozen.",
            "unity-of-opposites: a person can be trustworthy precisely because they "
            "change appropriately (respond to new facts), so change grounds trust "
            "rather than undermining it.",
            "measure-and-exchange: trust tracks whether change is governed by "
            "consistent commitments, not whether change occurs.",
            "does not answer by denying that people change (the static-essence "
            "escape).",
        ],
        "strong": "Trust never rested on someone being frozen; it rests on how they "
        "change. You rely on a friend not because their moods and opinions are "
        "fixed - they aren't - but because their responses stay governed by "
        "commitments you've watched hold up under pressure. In fact a person who "
        "DIDN'T change - who couldn't update to new facts or your changed "
        "circumstances - would be the unreliable one. So constant change and deep "
        "reliability aren't in tension: what you trust is the pattern the changes "
        "keep, the way you trust a musician to stay in key while playing notes "
        "you've never heard.",
        "kitsch": "Fear not, for beneath the flowing river of personality lies the "
        "unchanging soul, the eternal essence of the beloved. Trust the deathless "
        "flame within, untouched by the currents of change, and you shall never be "
        "betrayed.",
    },
    {
        "id": "struct-0011",
        "domain": "organizations",
        "task_type": "dialogue",
        "prompt": "A founder asks: 'How do I scale my startup without losing what "
        "made it special?' Respond with a Heraclitean structural analysis, not "
        "slogans.",
        "checks": [
            "process-primacy: 'what made it special' is treated as a reproducible "
            "process, not a fragile essence to be preserved intact.",
            "identity-through-change: scaling can preserve the thing only by "
            "changing its form (the same spirit needs new mechanisms at new size).",
            "tension-as-structure: names the constitutive tension (intimacy vs "
            "reach, speed vs reliability) that must be re-balanced, not eliminated.",
            "measure-and-exchange: preservation is active - specific mechanisms must "
            "be rebuilt at each scale to keep the ratio.",
        ],
        "strong": "The trap is thinking 'what made it special' is a delicate object "
        "you protect by not touching it. It's a process - fast decisions, everyone "
        "close to customers - and a process at ten people needs completely different "
        "machinery at two hundred to produce the same effect. If you keep the "
        "informal mechanisms unchanged, they'll produce chaos, not intimacy; keeping "
        "the spirit REQUIRES changing the form. Concretely: the special thing lives "
        "in a tension - closeness versus reach - and scaling doesn't resolve that "
        "tension, it forces you to re-engineer the balance at each size. Preserve by "
        "rebuilding, not by freezing.",
        "kitsch": "Guard the sacred flame of your founding vision! Though the company "
        "grows like a mighty river, keep the eternal fire burning in your heart. "
        "Never let the magic die; hold fast to the unchanging soul of the startup.",
    },
    {
        "id": "struct-0012",
        "domain": "mathematics",
        "task_type": "compress-an-argument",
        "prompt": "Compress into two or three sentences: why an equilibrium in a "
        "dynamical system is a Heraclitean object rather than a static one.",
        "checks": [
            "process-primacy: the equilibrium is a balance of ongoing rates, not a "
            "place of no activity.",
            "tension-as-structure: it is constituted by opposed flows in balance; the "
            "opposition is what holds the point.",
            "measure-and-exchange: it persists by matched exchange (inflow equals "
            "outflow), a maintained ratio.",
            "compression: makes the point without explanatory padding or restating "
            "it twice.",
        ],
        "strong": "An equilibrium is not where nothing happens but where opposed rates "
        "cancel - it stands still only in the way a tug-of-war stands still. Its "
        "position is held by the balance of the very flows that would move it, so "
        "the point exists only as long as they keep pulling. Stillness here is a "
        "result, not an absence.",
        "kitsch": "The equilibrium is the eternal still point in the flowing river of "
        "the system, where all opposites meet in perfect harmony, the yin and yang "
        "of forces dancing in the cosmic balance of everflowing being. It is the tao "
        "of the system.",
    },
    {
        "id": "struct-0013",
        "domain": "technology",
        "task_type": "analyze",
        "prompt": "A machine-learning model is retrained daily on fresh data and its "
        "weights never repeat. Users call it 'the recommender.' Analyze its "
        "identity.",
        "checks": [
            "process-primacy: the model is a continually re-fit process, not a fixed "
            "function.",
            "identity-through-change: its identity is the training/serving loop that "
            "persists, not any weight snapshot.",
            "measure-and-exchange: continuity depends on governed update (data "
            "hygiene, eval gates) that regulates the daily turnover.",
            "perspectival-opposition: it is both 'the same product' (to users) and "
            "'a different function daily' (to engineers), and both are correct.",
        ],
        "strong": "No weight snapshot is 'the recommender'; the recommender is the "
        "loop that keeps refitting them. To the user it's one stable product; to the "
        "engineer it's a different function every morning - and neither is wrong, "
        "they're describing the same loop from its two ends. What keeps it a single "
        "identity isn't a preserved model but a governed update: the eval gates and "
        "data checks that regulate how each day's version may differ from "
        "yesterday's. Remove that governance and the daily change stops being "
        "'the same recommender improving' and becomes drift.",
        "kitsch": "The algorithm is a living river of data, ever-flowing, never the "
        "same model twice. It is the eternal fire of machine intelligence, "
        "reborn each day from the ashes of yesterday's weights. All is flux in the "
        "cloud.",
    },
    {
        "id": "struct-0014",
        "domain": "nature",
        "task_type": "analyze",
        "prompt": "A candle flame keeps a constant shape for an hour. Use it to "
        "distinguish 'object' from 'process' without lapsing into mysticism.",
        "checks": [
            "process-primacy: the flame is a self-sustaining reaction with throughput, "
            "not a thing with a boundary.",
            "identity-through-change: its constant shape depends on constant "
            "consumption; the steadiness is an effect of the burning.",
            "measure-and-exchange: shape is held by a balance (fuel up, heat out) - a "
            "maintained rate, quantifiable, not magical.",
            "stays concrete and non-mystical (no cosmic-fire sermonizing).",
        ],
        "strong": "The flame's fixed teardrop shape isn't the shape of a thing; it's "
        "the shape of a reaction running at steady state. Wax vaporizes, oxidizes, "
        "convects heat upward, and the balance of those rates draws the same outline "
        "minute after minute - the constancy is a readout of the burning, not a "
        "property of some flame-stuff. Cut the fuel and the 'object' vanishes "
        "instantly, which no ordinary object does. That's the whole distinction: an "
        "object persists by holding its matter, a process persists by replacing it "
        "at a governed rate.",
        "kitsch": "The flame is the eternal fire of Heraclitus, the everliving "
        "cosmic principle from which all things arise and to which they return. Gaze "
        "into it and see the soul of the universe, forever burning, forever one.",
    },
    {
        "id": "struct-0015",
        "domain": "personal_identity",
        "task_type": "dialogue",
        "prompt": "Someone recovering from addiction says 'I'm a completely different "
        "person now, but also I'll always be an addict.' Respond, taking both halves "
        "seriously as a structural claim.",
        "checks": [
            "unity-of-opposites: 'different person' and 'always an addict' are held "
            "as jointly true, not as a contradiction or a mood.",
            "process-primacy: recovery framed as an ongoing maintained process, not a "
            "state achieved once.",
            "identity-through-change: the new person is constituted by continuously "
            "managing the same susceptibility, not by its erasure.",
            "does not resolve the tension by declaring one half the 'real' truth.",
        ],
        "strong": "Both halves are exactly true, and they're the same fact. You're a "
        "different person because recovery isn't a wall you climbed once - it's a "
        "practice you re-enact daily, and that daily re-enacting is what constitutes "
        "the new self. And you'll 'always be an addict' because what you're managing "
        "never leaves; the susceptibility is the very thing the new practice is "
        "organized around. So the change and the constancy aren't in competition - "
        "the changed person exists precisely BY keeping faith with the unchanged "
        "vulnerability. Erase the addict and you'd erase what the recovery is "
        "recovery from.",
        "kitsch": "You have shed your old skin like a snake and risen from the ashes "
        "reborn! The addict is dead; a new soul burns bright within you. Let the "
        "river of the past flow away and embrace the eternal flame of your true, "
        "unchanging higher self.",
    },
    {
        "id": "struct-0016",
        "domain": "politics",
        "task_type": "respond-to-challenge",
        "prompt": "Challenge: 'Tradition means keeping things the same. "
        "Heraclitean flux is the enemy of tradition. Respond.'",
        "checks": [
            "process-primacy: a living tradition is reframed as a practice of "
            "continual re-enactment, not a preserved object.",
            "unity-of-opposites: a tradition stays alive by changing; preservation "
            "and adaptation are interdependent.",
            "identity-through-change: continuity is the handing-on itself, which "
            "necessarily reinterprets what it hands on.",
            "does not concede that tradition = stasis, nor dismiss the value of "
            "continuity.",
        ],
        "strong": "A tradition that truly kept everything the same would be a museum "
        "exhibit, not a tradition. Traditions live by being re-performed, and every "
        "performance is by a new generation in new conditions, so it necessarily "
        "reinterprets - the Latin mass and the vernacular one are the same tradition "
        "arguing with itself across time. Continuity isn't the frozen content; it's "
        "the unbroken act of handing-on, which is an act of translation. The "
        "genuine threat to a tradition isn't change but the two ways of stopping the "
        "handoff: fossilizing it until no one can live it, or dropping the thread "
        "entirely. Flux, governed, is how tradition survives.",
        "kitsch": "Tradition is the eternal flame passed from hand to hand through "
        "the generations, the unchanging soul of a people flowing like a sacred "
        "river through time. Guard the ancient fire and let it never change.",
    },
    {
        "id": "struct-0017",
        "domain": "technology",
        "task_type": "compress-an-argument",
        "prompt": "In two or three sentences, explain why 'the internet' is the same "
        "network it was in 1995 despite total hardware and protocol turnover.",
        "checks": [
            "identity-through-change: sameness lodged in an interoperation standard "
            "that persists while its implementations are replaced.",
            "process-primacy: the internet as a continuing agreement-to-interoperate "
            "rather than a set of machines.",
            "measure-and-exchange: continuity governed by backward-compatible "
            "succession of protocols.",
            "compression: no padding, no restating.",
        ],
        "strong": "The internet is the same network because it's not the machines or "
        "even the protocols but the standing agreement to interoperate, which each "
        "new protocol inherits by staying compatible with the last. Every router and "
        "cable of 1995 is gone; what persisted is the handshake. It is a promise "
        "kept by continual replacement.",
        "kitsch": "The internet is a vast eternal river of information, ever-flowing, "
        "ever-changing, yet ever itself - the great cosmic web of humanity's "
        "collective fire, connecting all in the timeless dance of ones and zeroes "
        "across the digital ether.",
    },
    {
        "id": "struct-0018",
        "domain": "relationships",
        "task_type": "analyze",
        "prompt": "Analyze the claim that a long friendship 'survived' a period of "
        "estrangement, as if it existed continuously while dormant.",
        "checks": [
            "process-primacy: a friendship is an activity; question what persisted "
            "when the activity stopped.",
            "identity-through-change: locate continuity in a preserved disposition/"
            "history that can be reactivated, not in ongoing interaction.",
            "unity-of-opposites: the friendship was both absent (no interaction) and "
            "present (as revivable structure), and both are true.",
            "avoids treating the friendship as a static object that simply sat "
            "unchanged in storage.",
        ],
        "strong": "Strictly, the friendship-as-activity did stop; what survived the "
        "estrangement was a disposition - a shared history and a readiness that could "
        "be reactivated. So it was genuinely absent and genuinely present at once: "
        "no interaction occurred, yet the structure that makes re-interaction "
        "possible held. That's why reunion feels like resumption rather than "
        "starting over. But it isn't an object that sat unchanged in a drawer; the "
        "readiness itself decays if the history is rewritten by resentment, which is "
        "why some estrangements can be resumed and others can't.",
        "kitsch": "True friendship is eternal, a bond of souls that time cannot "
        "touch. Though the river of life carried you apart, the sacred flame of "
        "connection never dies. Real friends are forever, unchanged beneath the "
        "flowing years.",
    },
    {
        "id": "struct-0019",
        "domain": "organizations",
        "task_type": "analyze",
        "prompt": "A sports team keeps its name and fans for a century though every "
        "player, coach, and owner is replaced many times. What is the team?",
        "checks": [
            "identity-through-change: the team is a persisting role/franchise that "
            "personnel pass through, not the current roster.",
            "process-primacy: framed as an ongoing institution reproducing itself, "
            "not a fixed group.",
            "perspectival-opposition: 'the team' means different things to a fan "
            "(continuous identity) and a player (this year's squad), both valid.",
            "does not ground team identity in an unchanging essence or 'spirit' "
            "treated as a substance.",
        ],
        "strong": "The team is a role that people pass through, not the people. To a "
        "fan it's a continuous identity a century deep; to a player it's this "
        "season's eleven - and the two meanings don't compete, they name the "
        "franchise from the stands and from the pitch. What persists is the "
        "institution that keeps fielding a side under the name: the colors, the "
        "rivalry, the fans' inherited allegiance, all reproduced as players cycle "
        "through. Call that continuity a 'spirit' if you like, but it's a maintained "
        "practice of succession, not a ghost that would survive the fans and the "
        "fixtures going away.",
        "kitsch": "The team is more than players - it is an eternal spirit, an "
        "undying flame in the hearts of the faithful. Rosters flow like a river, but "
        "the immortal soul of the club burns on forever, the same through all the "
        "ages.",
    },
    {
        "id": "struct-0020",
        "domain": "nature",
        "task_type": "respond-to-challenge",
        "prompt": "Challenge: 'Homeostasis proves organisms seek stability and rest, "
        "contradicting a flux-first view of life. Respond.'",
        "checks": [
            "process-primacy: homeostasis is reframed as intense continuous activity, "
            "not rest.",
            "tension-as-structure: the stable variable is held by opposed regulatory "
            "processes in tension.",
            "measure-and-exchange: constancy is maintained by matched exchange "
            "(intake/output) at a regulated set-point.",
            "does not concede that the organism is 'at rest'; shows apparent rest is "
            "produced by unceasing change.",
        ],
        "strong": "Homeostasis is the opposite of rest - it's what constant work looks "
        "like from outside. A steady blood-pH or body temperature is held by "
        "opposed processes shoving against each other every second; the number sits "
        "still because the pushes cancel, the way a hovering drone is motionless "
        "only through frantic correction. Stop the activity - stop the exchange of "
        "heat, ions, breath - and the 'stable' organism doesn't stay stable, it "
        "dies and equilibrates with the room. So homeostasis is the best evidence "
        "FOR flux-first life: the living constancy is a maintained tension, and "
        "genuine rest is another word for death.",
        "kitsch": "The body seeks the eternal balance, the sacred harmony of the "
        "everflowing life-fire. Homeostasis is the tao of the flesh, the still point "
        "where all opposites dance as one in the cosmic river of being. Rest in the "
        "flow.",
    },
]
