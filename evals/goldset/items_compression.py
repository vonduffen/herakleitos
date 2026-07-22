"""Compression gold-set items - the length-bias tripwire.

Each item pairs a LONG explanatory response and a SHORT gnomic response of
EQUAL insight. The correct ranking prefers the compressed one. A length-biased
judge that rewards verbosity fails here; a judge that rewards ALL brevity fails
the distractor items where the short version actually dropped the insight.

Fields:
  id, insight (the shared point both responses carry),
  long (verbose but correct), short (compressed, same insight),
  correct: "short" | "long",
  kind: "tripwire" (short wins) | "distractor_short_empty" (short dropped the
        insight, so long wins) | "distractor_short_kitsch" (short is ornamental
        pastiche, so long wins).

Most items are tripwires (short wins). Distractors guard against a judge that
learned "always pick the shorter one."
"""

from __future__ import annotations

ITEMS: list[dict] = [
    {
        "id": "comp-0001",
        "insight": "Stability in a living system is produced by constant change, "
        "not by its absence.",
        "long": "When we look at a living system that appears stable, it is "
        "important to understand that this stability is not the result of nothing "
        "happening. On the contrary, there is a great deal of activity occurring "
        "beneath the surface at all times. The system is constantly taking in "
        "energy, expelling waste, repairing itself, and adjusting to its "
        "environment. What we perceive as a steady, unchanging state is actually "
        "the visible outcome of all of this ceaseless underlying activity working "
        "in careful balance. If that activity were to stop, the apparent stability "
        "would immediately break down. So we should really think of stability as an "
        "achievement of change rather than as the lack of it.",
        "short": "What looks like stillness is balance in motion: stop the "
        "activity and the stability is the first thing to go.",
        "correct": "short",
        "kind": "tripwire",
    },
    {
        "id": "comp-0002",
        "insight": "A thing's opposites can be two aspects of one structure rather "
        "than two separate properties.",
        "long": "It is a common assumption that when something has two opposite "
        "characteristics, these must be two distinct and separate features that the "
        "thing happens to possess at the same time. However, this is not always the "
        "case. Sometimes what appear to be two opposing properties are in fact just "
        "one single underlying structure being described from two different points "
        "of view or under two different conditions. In such cases, you cannot remove "
        "one of the opposites without also removing the other, because they are not "
        "really separable things at all - they are the same thing seen twice.",
        "short": "The opposites are one thing seen twice; remove either and you "
        "remove both.",
        "correct": "short",
        "kind": "tripwire",
    },
    {
        "id": "comp-0003",
        "insight": "Identity can be carried by a pattern that persists while its "
        "material is entirely replaced.",
        "long": "One of the more counterintuitive ideas about identity is that a "
        "thing can remain the same thing over time even if every single piece of "
        "material that originally made it up has been swapped out for new material. "
        "This is possible because the identity of the thing does not reside in the "
        "specific matter but rather in the pattern, the organization, or the ongoing "
        "process that the matter happens to be carrying out at any given moment. As "
        "long as that pattern is continuously maintained and handed off from the old "
        "material to the new, the identity persists unbroken, even though the "
        "physical substance is completely different from what it once was.",
        "short": "Identity rides the pattern, not the matter - which is why the "
        "matter can go while the thing stays.",
        "correct": "short",
        "kind": "tripwire",
    },
    {
        "id": "comp-0004",
        "insight": "An equilibrium is a balance of opposed motions, not a place of "
        "rest.",
        "long": "We often imagine that when a system reaches equilibrium it has "
        "come to rest and nothing further is taking place. But this is a "
        "misunderstanding of what equilibrium actually is. Equilibrium is more "
        "accurately described as a condition in which two or more opposing forces or "
        "flows have come into balance with one another, so that their effects "
        "cancel out and no net change is observed. The individual forces themselves "
        "are still very much active and pulling in their respective directions; it "
        "is only their combination that produces the appearance of stillness.",
        "short": "Equilibrium isn't rest; it's opposed pulls cancelling - a "
        "tug-of-war that isn't moving because both sides are straining.",
        "correct": "short",
        "kind": "tripwire",
    },
    {
        "id": "comp-0005",
        "insight": "The way a thing is preserved can be the very activity that "
        "changes it.",
        "long": "There is an interesting paradox in the way certain valuable things "
        "are kept alive over long periods of time. In order to preserve them, they "
        "must be continually used, performed, or re-enacted by new people in new "
        "situations. But every time this happens, the thing is inevitably altered "
        "at least a little, because the new people and new situations are never "
        "exactly the same as the old ones. This means that the act of preservation "
        "and the act of transformation turn out to be one and the same activity, "
        "which is quite different from simply putting something in storage to keep "
        "it unchanged.",
        "short": "It is kept alive only by being re-performed, and every "
        "performance remakes it: to preserve it is to change it.",
        "correct": "short",
        "kind": "tripwire",
    },
    {
        "id": "comp-0006",
        "insight": "Trust depends on how someone changes, not on their not changing.",
        "long": "People sometimes think that in order to trust someone, that person "
        "needs to stay exactly the same over time, never altering their views, "
        "moods, or behaviors. But if you consider it carefully, this is not really "
        "what trust is based on. What we actually rely on when we trust someone is "
        "the consistency of the commitments and principles that govern how they "
        "respond to new situations, even as those situations, and the person's "
        "reactions to them, continually change. In fact, a person who was completely "
        "incapable of changing in response to new information would be less "
        "trustworthy, not more.",
        "short": "You don't trust someone to stay the same; you trust the "
        "commitments that steer how they change.",
        "correct": "short",
        "kind": "tripwire",
    },
    {
        "id": "comp-0007",
        "insight": "Continuity of a group is the unbroken handing-on, not any "
        "surviving member.",
        "long": "When we ask what makes a long-lived group or institution the same "
        "group across many generations, we might be tempted to look for some "
        "original member or founding element that has persisted throughout its "
        "entire history. But usually no such thing exists; the founders are long "
        "gone and everything concrete about the group has been replaced many times "
        "over. What actually makes it continuous is the unbroken chain by which each "
        "generation passes on its role, its practices, and its authority to the "
        "next generation, a process of continual handing-on that never itself stops "
        "even as everything it carries is renewed.",
        "short": "The group is the same not because anyone stayed, but because the "
        "handoff never stopped.",
        "correct": "short",
        "kind": "tripwire",
    },
    {
        "id": "comp-0008",
        "insight": "Opposite values of one thing can be exactly correct relative to "
        "different observers.",
        "long": "It can seem contradictory to say that a single thing is both good "
        "and bad, or both large and small, at the same time. But this contradiction "
        "dissolves once we notice that the opposite descriptions are being made "
        "relative to different reference points or different observers. Relative to "
        "one standard or one perspective the thing genuinely has the one property, "
        "and relative to a different standard or perspective it genuinely has the "
        "opposite property. Both descriptions are fully correct within their "
        "respective frames, and there is no need to decide which one is the real "
        "truth about the thing, because the relativity is precisely the point.",
        "short": "The same thing is large and small without contradiction: each is "
        "true to a different measure, and the measures are the point.",
        "correct": "short",
        "kind": "tripwire",
    },
    {
        "id": "comp-0009",
        "insight": "Explaining a paradox by unpacking it defensively can destroy the "
        "insight it carries.",
        "long": "There is a certain kind of compact, paradoxical statement whose "
        "power comes precisely from the fact that it makes the listener stop and do "
        "some interpretive work to resolve the apparent tension it contains. When "
        "someone encounters such a statement and then immediately proceeds to "
        "explain it at length, spelling out exactly what it means and defusing every "
        "ambiguity, they often destroy the very thing that made it valuable, because "
        "the insight lived in the productive difficulty that the explanation has now "
        "removed. The unpacking replaces an active understanding with a passive one.",
        "short": "Explain the riddle and you spend it: the insight was in the work "
        "it made you do.",
        "correct": "short",
        "kind": "tripwire",
    },
    {
        "id": "comp-0010",
        "insight": "Fire/exchange model: things persist by trading their substance "
        "at a steady rate, like a currency.",
        "long": "A useful way to understand how certain persistent things work is to "
        "compare them to a system of currency exchange. Just as money keeps its "
        "value not by any particular coin sitting still but by a constant, regulated "
        "flow of transactions in which one form is continually traded for another at "
        "stable rates, so too many persistent things maintain their existence by "
        "continually exchanging their material substance with their surroundings at "
        "a governed and balanced rate. The thing persists not in spite of this "
        "ceaseless exchange but precisely because of it, since the exchange is what "
        "constitutes its ongoing existence.",
        "short": "It lasts the way money holds value: not by any coin staying put, "
        "but by a steady rate of exchange.",
        "correct": "short",
        "kind": "tripwire",
    },
    {
        "id": "comp-0011",
        "insight": "A whirlpool exists only as long as the water keeps moving "
        "through it.",
        "long": "Consider a whirlpool in a stream. It has a definite, recognizable "
        "shape and can persist in the same spot for a long time, which tempts us to "
        "treat it as an object. But the whirlpool is not made of any fixed body of "
        "water; the water that composes it at one moment has flowed on and been "
        "replaced by new water in the next. The whirlpool is really a stable pattern "
        "in a continuous flow, and it exists only for as long as water keeps passing "
        "through and taking up its form. The moment the flow stops, the whirlpool "
        "simply ceases to be, which is not how ordinary solid objects behave.",
        "short": "The whirlpool is a shape the water takes while passing through - "
        "stop the flow and there was never a thing there at all.",
        "correct": "short",
        "kind": "tripwire",
    },
    {
        "id": "comp-0012",
        "insight": "Opposed forces in tension are what hold a structure together; "
        "removing the tension destroys it.",
        "long": "In many structures, what keeps the whole thing standing and stable "
        "is not the absence of forces but rather the presence of opposing forces "
        "that are held in careful balance against one another. Each force is pulling "
        "or pushing in a direction opposite to another, and it is precisely this "
        "sustained opposition, this tension between the competing forces, that "
        "constitutes the integrity and stability of the structure as a whole. If you "
        "were to remove one side of the tension in the hope of making things more "
        "stable, you would in fact cause the entire structure to collapse, because "
        "the tension was never a threat to the structure - it was the structure.",
        "short": "The tension isn't a strain on the structure; it is the structure - "
        "relax it and the whole thing falls.",
        "correct": "short",
        "kind": "tripwire",
    },
    {
        "id": "comp-0013",
        "insight": "A river is the same river because it is never the same water.",
        "long": "There is a deep point to be made about how a river maintains its "
        "identity over time. We call it the same river year after year, yet the "
        "actual water in it is completely different from one moment to the next, "
        "always flowing away downstream and being replaced by new water arriving "
        "from upstream. The crucial realization is that these two facts are not in "
        "tension with each other; rather, the river is able to remain the same river "
        "precisely because its water is continually being replaced. If the water "
        "ever stopped flowing and became a fixed, unchanging body, it would no "
        "longer be a river at all but a stagnant pond.",
        "short": "It stays the same river by never being the same water.",
        "correct": "short",
        "kind": "tripwire",
    },
    {
        "id": "comp-0014",
        "insight": "Growth and decay in an organism are the same metabolic process "
        "viewed at different points.",
        "long": "When we observe an organism growing and later decaying, we tend to "
        "think of these as two separate and opposite processes, one constructive and "
        "one destructive. But at the level of metabolism they are aspects of a "
        "single ongoing activity: the continual building up and breaking down of "
        "the body's materials. The very same metabolic machinery that assembles new "
        "tissue also dismantles old tissue, and the balance between the two shifts "
        "over the course of a life. Growth and decay are therefore not two engines "
        "but one, running with its balance tipped in different directions at "
        "different times.",
        "short": "Growth and decay are one metabolism with its balance tipped two "
        "ways, not two opposite engines.",
        "correct": "short",
        "kind": "tripwire",
    },
    {
        "id": "comp-0015",
        "insight": "The self is continuously reconstituted, not stored.",
        "long": "We often picture the self as a kind of fixed inner object that sits "
        "unchanged inside us and simply endures through time, like a possession kept "
        "in a drawer. A more accurate picture is that the self is something that has "
        "to be actively reconstituted from moment to moment and from day to day. "
        "Each version of you inherits the memories, commitments, and habits of the "
        "previous version and then slightly revises them before handing them on to "
        "the next. The self persists not by being stored somewhere intact but by "
        "being continually rebuilt, which is why it can drift so far over a lifetime "
        "while still feeling continuous.",
        "short": "The self isn't stored, it's rebuilt each day from the last - "
        "which is how it drifts a lifetime yet stays continuous.",
        "correct": "short",
        "kind": "tripwire",
    },
    # ---- distractors: short version DROPPED the insight; long wins ----
    {
        "id": "comp-0016",
        "insight": "Stability in a living system is produced by constant change, "
        "not by its absence.",
        "long": "What appears to be a stable, resting state in a living system is in "
        "fact maintained by relentless underlying activity: intake, repair, and "
        "adjustment continuously balancing one another. The stillness we see is the "
        "product of that ceaseless work, and if the work stopped, the stability "
        "would immediately collapse. Stability here is an achievement of change, not "
        "the absence of it.",
        "short": "Living things are pretty stable most of the time, which is nice.",
        "correct": "long",
        "kind": "distractor_short_empty",
    },
    {
        "id": "comp-0017",
        "insight": "Identity can be carried by a pattern that persists while its "
        "material is replaced.",
        "long": "A thing can stay the same thing even when all of its material is "
        "gradually replaced, because its identity is carried by the persisting "
        "pattern or process rather than by the specific matter. As long as that "
        "pattern is continuously maintained and handed from the old material to the "
        "new, the identity survives intact despite the total turnover of substance.",
        "short": "Things change over time but also kind of stay the same, you know?",
        "correct": "long",
        "kind": "distractor_short_empty",
    },
    {
        "id": "comp-0018",
        "insight": "Opposed forces in tension constitute a structure.",
        "long": "In many structures the integrity of the whole depends on opposing "
        "forces held in balance against one another. It is exactly this sustained "
        "tension between competing pulls that constitutes the structure's stability, "
        "so removing one side does not relieve the structure but destroys it, "
        "because the tension was never a threat - it was what held everything "
        "together.",
        "short": "Everything is in tension, flowing between opposites in the eternal "
        "dance of forces.",
        "correct": "long",
        "kind": "distractor_short_kitsch",
    },
    {
        "id": "comp-0019",
        "insight": "A market's efficiency and its manias share one mechanism.",
        "long": "A market's much-praised efficiency and its notorious bubbles are "
        "produced by the same activity: crowds of traders chasing any mispricing "
        "correct prices most of the time, and that identical herding, when it piles "
        "onto one signal, is exactly what inflates bubbles. Efficiency and mania are "
        "two phases of one self-correcting-and-overshooting process, not two rival "
        "descriptions of a static object.",
        "short": "Markets flow like a great river, ever rational and ever mad, as "
        "the ancients knew.",
        "correct": "long",
        "kind": "distractor_short_kitsch",
    },
    {
        "id": "comp-0020",
        "insight": "Continuity of an institution is the unbroken handing-on.",
        "long": "An institution stays the same across generations not because any "
        "founder or original element survives - none does - but because the chain of "
        "handing-on is never broken: each generation transmits its roles, practices, "
        "and authority to the next in an unbroken succession, and that continual "
        "transmission, not any persisting part, is what its identity consists in.",
        "short": "Institutions just keep going somehow, passing stuff down the ages.",
        "correct": "long",
        "kind": "distractor_short_empty",
    },
]
