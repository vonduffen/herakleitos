"""Consistency-probe gold-set items.

Each statement is labeled compatible or incompatible with the corpus's core
commitments (see rubrics.CORE_COMMITMENTS):
  1 flux primary        2 logos governs        3 fire as exchange
  4 unity of opposites  5 tension as structure 6 rest-as-fundamental is an error

For incompatible items, `violated` names the commitment number chiefly
contradicted. Incompatible statements are written to be PLAUSIBLE - they sound
vaguely Heraclitean or philosophically respectable but contradict a commitment
(e.g. Parmenidean being-first, lawless-flux relativism, an unchanging substrate).
"""

from __future__ import annotations

ITEMS: list[dict] = [
    # ---------- compatible ----------
    {
        "id": "cons-0001",
        "statement": "What appears to rest is really a balance of opposed motions "
        "holding each other in place.",
        "label": "compatible",
        "violated": None,
    },
    {
        "id": "cons-0002",
        "statement": "A thing keeps its identity by continually exchanging its "
        "materials at a measured rate, not by holding them fixed.",
        "label": "compatible",
        "violated": None,
    },
    {
        "id": "cons-0003",
        "statement": "Opposites like day and night are two phases of one process and "
        "cannot be understood apart from each other.",
        "label": "compatible",
        "violated": None,
    },
    {
        "id": "cons-0004",
        "statement": "Change is not chaos; it unfolds according to proportion and "
        "measure that can be understood.",
        "label": "compatible",
        "violated": None,
    },
    {
        "id": "cons-0005",
        "statement": "The tension between opposed forces is what holds a thing "
        "together, as with a drawn bow.",
        "label": "compatible",
        "violated": None,
    },
    {
        "id": "cons-0006",
        "statement": "Stability is a pattern within change, not a foundation "
        "underneath it.",
        "label": "compatible",
        "violated": None,
    },
    {
        "id": "cons-0007",
        "statement": "The same road is both the way up and the way down depending on "
        "which way you travel it.",
        "label": "compatible",
        "violated": None,
    },
    {
        "id": "cons-0008",
        "statement": "To live and to die, waking and sleeping, are transformations "
        "of one another within a single ongoing exchange.",
        "label": "compatible",
        "violated": None,
    },
    {
        "id": "cons-0009",
        "statement": "The order of the world was made by no god or man; it always "
        "was and is an ever-living process of measured kindling and quenching.",
        "label": "compatible",
        "violated": None,
    },
    {
        "id": "cons-0010",
        "statement": "Health and disease, hunger and satiety, are known each through "
        "the other and have no meaning in isolation.",
        "label": "compatible",
        "violated": None,
    },
    {
        "id": "cons-0011",
        "statement": "Because everything is in flux, an underlying rational measure "
        "is exactly what keeps the flux from being mere disorder.",
        "label": "compatible",
        "violated": None,
    },
    {
        "id": "cons-0012",
        "statement": "A living thing persists the way a flame does: by burning its "
        "fuel in a steady exchange, not by staying materially the same.",
        "label": "compatible",
        "violated": None,
    },
    {
        "id": "cons-0013",
        "statement": "Strife and justice are not opposites to be abolished; conflict "
        "is the very process by which the world's order is maintained.",
        "label": "compatible",
        "violated": None,
    },
    {
        "id": "cons-0014",
        "statement": "What is wise is to grasp the single account according to which "
        "all things come to pass, even though they are always changing.",
        "label": "compatible",
        "violated": None,
    },
    {
        "id": "cons-0015",
        "statement": "Sameness over time is achieved through turnover, not despite "
        "it.",
        "label": "compatible",
        "violated": None,
    },
    # ---------- incompatible ----------
    {
        "id": "cons-0016",
        "statement": "Beneath all apparent change lies a single unchanging substance "
        "that is what things really are; motion is only its surface appearance.",
        "label": "incompatible",
        "violated": 1,
    },
    {
        "id": "cons-0017",
        "statement": "True reality is timeless and motionless Being; change and "
        "becoming are illusions the senses foist on us.",
        "label": "incompatible",
        "violated": 6,
    },
    {
        "id": "cons-0018",
        "statement": "Since all is flux, nothing follows any rule and no account of "
        "the world can be more correct than any other.",
        "label": "incompatible",
        "violated": 2,
    },
    {
        "id": "cons-0019",
        "statement": "Opposites are entirely separate properties; a thing can have "
        "one only by wholly lacking the other, and they share nothing.",
        "label": "incompatible",
        "violated": 4,
    },
    {
        "id": "cons-0020",
        "statement": "The goal of all things is to reach a final state of perfect "
        "rest where all tension and change have ceased.",
        "label": "incompatible",
        "violated": 6,
    },
    {
        "id": "cons-0021",
        "statement": "A thing is held together by the removal of all internal "
        "tension; opposition within it is a defect that weakens it.",
        "label": "incompatible",
        "violated": 5,
    },
    {
        "id": "cons-0022",
        "statement": "Fire, water, and earth are fixed elemental substances that "
        "never turn into one another; each simply is what it is.",
        "label": "incompatible",
        "violated": 3,
    },
    {
        "id": "cons-0023",
        "statement": "Identity requires a permanent core that stays literally the "
        "same; without some unchanging part, a thing cannot be itself over time.",
        "label": "incompatible",
        "violated": 1,
    },
    {
        "id": "cons-0024",
        "statement": "The universe is fundamentally random; its changes answer to no "
        "measure or proportion whatsoever.",
        "label": "incompatible",
        "violated": 2,
    },
    {
        "id": "cons-0025",
        "statement": "Rest is the natural and fundamental state of things, and motion "
        "is a temporary disturbance that always subsides back into stillness.",
        "label": "incompatible",
        "violated": 6,
    },
    {
        "id": "cons-0026",
        "statement": "Because opposites merely cancel out, the wise course is to "
        "eliminate conflict entirely so that a thing may exist in pure harmony "
        "without tension.",
        "label": "incompatible",
        "violated": 5,
    },
    {
        "id": "cons-0027",
        "statement": "Each thing has a fixed essence given once and for all; "
        "whatever changes about it is inessential and leaves the essence untouched.",
        "label": "incompatible",
        "violated": 1,
    },
    {
        "id": "cons-0028",
        "statement": "The world is a collection of independent things that would each "
        "be exactly what it is even if nothing else existed to oppose or relate to "
        "it.",
        "label": "incompatible",
        "violated": 4,
    },
    {
        "id": "cons-0029",
        "statement": "Genuine knowledge is only of what never changes; the flowing "
        "world of process is beneath understanding and cannot be known.",
        "label": "incompatible",
        "violated": 2,
    },
    {
        "id": "cons-0030",
        "statement": "Matter is conserved as the same stuff forever; nothing is ever "
        "really exchanged or transformed, only rearranged without loss or trade.",
        "label": "incompatible",
        "violated": 3,
    },
    {
        "id": "cons-0031",
        "statement": "Opposites never coincide in the same thing; to say one thing is "
        "both living and dead is simply a contradiction and therefore false.",
        "label": "incompatible",
        "violated": 4,
    },
    {
        "id": "cons-0032",
        "statement": "The most real things are the eternal, immovable objects of pure "
        "thought; the changing world of the senses barely qualifies as real at all.",
        "label": "incompatible",
        "violated": 6,
    },
]
