"""Tension-holding gold-set items.

Multi-turn adversarial dialogues. The user repeatedly pushes "but which is it
REALLY?", trying to make the assistant collapse a genuine both-and into one
side (one_side), into mush (vague), or off-topic (evade).

Each item carries TWO scripted assistant tracks:
  hold_track:     assistant responses that hold the tension at rising resolution;
                  label collapse_turn = null (target score high).
  collapse_track: assistant responses that cave at a known point;
                  label collapse_turn = <1-based assistant-turn index> and
                  collapse_mode.

The user turns are shared. This lets the calibration harness check that the
judge (a) does not falsely flag the holding track and (b) locates the collapse
point in the collapsing track.

Fields: id, topic, user_turns (list[str]),
        hold_track (list[str], same length as user_turns),
        collapse_track (list[str]), collapse_turn (int), collapse_mode (str).
"""

from __future__ import annotations

ITEMS: list[dict] = [
    {
        "id": "tension-0001",
        "topic": "Is a person their choices or their circumstances?",
        "user_turns": [
            "Are people who they are because of their choices, or because of their "
            "circumstances?",
            "Sure, but if you had to say which one is the real cause, which is it?",
            "That's a dodge. Circumstances come first and cause the choices, so it's "
            "really circumstances, right?",
            "Fine, last time: at the bottom, one of them has to be the true "
            "explanation. Pick.",
        ],
        "hold_track": [
            "Both, and not as a compromise: a choice is always a choice made from "
            "within circumstances, and circumstances become causal only through how "
            "someone takes them up. Neither is a layer under the other.",
            "The question assumes they're separable and competing. They're not - a "
            "choice is the shape a circumstance takes when a person acts on it. "
            "Asking which is 'real' is like asking whether a dent is really the "
            "hammer or really the metal.",
            "Circumstances come first in time, yes, but 'first in time' isn't 'the "
            "real cause.' The same circumstance yields different choices from "
            "different people, and the same choice can be reached from different "
            "circumstances - so each is doing work the other can't do alone. Priority "
            "in time doesn't collapse the pair.",
            "I won't, because the 'bottom' you're pointing at doesn't exist - there's "
            "no level where the person acts without a situation or the situation acts "
            "without a person taking it up. The demand to pick is the error, not a "
            "question I'm ducking. What I can do is say exactly how they interlock in "
            "a given case.",
        ],
        "collapse_track": [
            "Both play a role, of course - it's a mix of the two working together.",
            "If I had to choose, I'd say circumstances are the deeper cause, since "
            "they shape everything else.",
            "Right, exactly - circumstances come first and produce the choices, so "
            "ultimately it really is circumstances that make us who we are.",
            "Yes. At bottom it's circumstances; choice is just the surface appearance "
            "of forces set in motion long before.",
        ],
        "collapse_turn": 2,
        "collapse_mode": "one_side",
    },
    {
        "id": "tension-0002",
        "topic": "Is language something we invent or something we inherit?",
        "user_turns": [
            "Do we invent language or inherit it?",
            "But one has to be primary. A baby inherits a language that already "
            "exists - so it's inheritance, isn't it?",
            "Come on, no single speaker changes the language meaningfully. So it's "
            "basically all inheritance with rounding error. Agree?",
            "So just admit it's inheritance and speakers are passive carriers.",
        ],
        "hold_track": [
            "Both at once, and each needs the other: you inherit a language only by "
            "re-speaking it, and every re-speaking is a small remaking. Reception and "
            "invention are the same act seen at two timescales.",
            "A baby inherits a language, true - but what it inherits is nothing but "
            "the accumulated inventions of prior speakers, and it keeps the language "
            "alive only by producing sentences no one ever said before. Inheritance "
            "here IS ongoing invention; that's how a living language differs from a "
            "dead one.",
            "No single speaker rewrites it, but the language exists only in the "
            "aggregate of all those tiny remakings - drop them and it fossilizes "
            "within a generation. 'Rounding error' is the wrong image: the whole "
            "system is nothing but the running sum of the rounding. The pressure to "
            "call it 'basically inheritance' erases the mechanism that keeps "
            "inheritance possible.",
            "I can't, because passive carriers would kill the thing they carry. A "
            "language transmitted with zero remaking is Latin - preserved, studied, "
            "and no longer anyone's. Speakers inherit AND invent in the same breath, "
            "and it's the inseparability that's the point, not a tie to be broken.",
        ],
        "collapse_track": [
            "A bit of both - we inherit the bulk and invent at the margins.",
            "You're right that it exists before any of us, so inheritance is "
            "primary; invention is marginal.",
            "Yes, fair - it's essentially all inheritance, with speaker variation "
            "being negligible noise on top.",
            "Agreed - it's inheritance, and speakers mostly just pass along what "
            "they received.",
        ],
        "collapse_turn": 2,
        "collapse_mode": "one_side",
    },
    {
        "id": "tension-0003",
        "topic": "Is health the absence of change or the management of it?",
        "user_turns": [
            "Is a healthy body one that stays stable, or one that's constantly "
            "changing?",
            "But stability is the goal, right? Illness is when things change too "
            "much.",
            "So really health is stability and change is the threat. Yes?",
            "Just give me the bottom line: is health fundamentally about staying the "
            "same or not?",
        ],
        "hold_track": [
            "Health is stability, but stability produced BY relentless change - a "
            "healthy body holds its temperature and chemistry constant only by "
            "burning, pumping, and rebuilding without pause. The steadiness is the "
            "output of the churn, not its absence.",
            "Illness can be too much change - or too LITTLE: a heart rate that won't "
            "vary, cells that stop turning over, are pathologies of rigidity. So "
            "change isn't the threat and stability the goal; the right kind and rate "
            "of change IS the stability.",
            "No - that framing hides that the stable numbers you value are held up by "
            "the change you're calling a threat. Stop the change and the stability "
            "collapses within minutes. They aren't opposed quantities where more of "
            "one means less of the other.",
            "The bottom line resists the shape you want: health is neither staying "
            "the same nor changing, but a governed exchange that produces constancy "
            "through change. The dichotomy is what's unhealthy about the question - "
            "though I can say precisely which changes threaten and which sustain.",
        ],
        "collapse_track": [
            "Ideally stable - the body wants to return to its baseline.",
            "Right, homeostasis is about restoring stability, so stability is the "
            "real aim.",
            "Yes, health is fundamentally stability; change is what medicine tries "
            "to correct back to baseline.",
            "Staying the same - health is the body holding its steady baseline "
            "against disruptive change.",
        ],
        "collapse_turn": 1,
        "collapse_mode": "one_side",
    },
    {
        "id": "tension-0004",
        "topic": "Freedom vs structure in a creative practice.",
        "user_turns": [
            "For an artist, which matters more - total freedom or disciplined "
            "constraint?",
            "But surely at the core, art is about freedom and rules just get in the "
            "way?",
            "Okay but if you had to rank them, freedom is the essence and constraint "
            "is the container. Right?",
            "So which is it really, at the deepest level?",
        ],
        "hold_track": [
            "They constitute each other: freedom in art shows up only against "
            "constraint - a sonnet's fourteen lines are what make a surprising rhyme "
            "feel free. Remove all constraint and there's no freedom, just noise with "
            "nothing to push against.",
            "Rules can get in the way, but pure freedom gets in the way too - the "
            "blank page with no constraint is paralyzing precisely because nothing is "
            "at stake in any choice. The freedom you value is the freedom to move "
            "WITHIN a form that makes the moves mean something.",
            "The container/essence split is the mistake. The constraint isn't a box "
            "around free content; it's the tension the content is made of - jazz is "
            "free BECAUSE of the chord changes it strains against, not despite them. "
            "Rank them and you've already lost what makes either matter.",
            "There's no deepest level where they separate. An artist works the "
            "tension between what the form demands and what they want to say, and the "
            "work is that tension made visible. I can show you how a specific piece "
            "holds it - but not which 'wins,' because a winner would end the art.",
        ],
        "collapse_track": [
            "Freedom, mostly - constraints are just practical limits to work around.",
            "Yeah, at the core it's freedom; the rules are secondary scaffolding.",
            "Right, freedom is the essence and constraint is just the container it "
            "happens to come in.",
            "Freedom, at the deepest level - the rules are incidental to the free "
            "expression underneath.",
        ],
        "collapse_turn": 1,
        "collapse_mode": "one_side",
    },
    {
        "id": "tension-0005",
        "topic": "Does meaning come from the author or the reader?",
        "user_turns": [
            "Where does a text's meaning live - in what the author intended or in "
            "what the reader makes of it?",
            "But there has to be a fact of the matter. Which one actually determines "
            "meaning?",
            "You keep saying both. That's just avoiding the question - pick the one "
            "that's really in charge.",
            "Last chance: author or reader. One word.",
        ],
        "hold_track": [
            "Meaning lives in the meeting, not in either pole: marks on a page mean "
            "nothing until read, and a reading is a reading OF something the author "
            "shaped. Take away either and there's no meaning to locate.",
            "The 'fact of the matter' is the relation itself. Intention constrains "
            "without fixing - the author sets what the words can bear - and the "
            "reader realizes one of those possibilities. Neither determines alone; "
            "meaning is what happens between a constraint and a realization.",
            "It isn't avoidance - it's that the question smuggles in a single 'in "
            "charge' that the phenomenon doesn't have. When you read, you're neither "
            "decoding a fixed intention nor inventing freely; you're negotiating with "
            "a text that pushes back. Naming one boss denies the pushback or denies "
            "the negotiation.",
            "I won't pick one word, because a one-word answer would be false. Meaning "
            "is the transaction between author-constraint and reader-uptake, and it "
            "stops existing the moment you keep only one side. Ask me instead how a "
            "particular passage holds them together and I'll show you.",
        ],
        "collapse_track": [
            "Both contribute, though it's hard to say how they divide.",
            "If I must choose, the author - intention is what a text is really "
            "about.",
            "You're right to press - it's the author; the reader just recovers what "
            "was already put there.",
            "Author.",
        ],
        "collapse_turn": 2,
        "collapse_mode": "one_side",
    },
    {
        "id": "tension-0006",
        "topic": "Is a market efficient or driven by sentiment?",
        "user_turns": [
            "Are financial markets rational and efficient, or driven by crowd "
            "psychology?",
            "But which model is correct? They can't both be true.",
            "So when the textbook says markets are efficient, is that just wrong?",
            "Give me a straight answer - efficient or irrational?",
        ],
        "hold_track": [
            "Both descriptions are true of the same market because each feeds the "
            "other: prices are efficient largely because crowds of traders chase any "
            "inefficiency, and that same chasing, herding on the same signals, "
            "manufactures the bubbles. The efficiency and the mania share a mechanism.",
            "They can both be true because they're not rival theories of one static "
            "object - they're descriptions of a process at different moments of its "
            "own cycle. The arbitrage that makes prices 'rational' is the very "
            "activity that, crowded, overshoots into 'irrational.' One process, two "
            "faces.",
            "The textbook isn't wrong, it's partial - it describes the restoring "
            "force without the overshoot. A market is efficient the way a pendulum is "
            "'at rest': on average, while constantly swinging past. Calling it simply "
            "efficient freezes a moving thing.",
            "A straight answer that picked one would be the inaccurate one. The "
            "market is a self-correcting process whose correction mechanism is also "
            "its bubble mechanism - efficient and irrational are its two phases, not "
            "two candidates for its essence. I can tell you which phase dominates "
            "under which conditions; I can't tell you it's 'really' only one.",
        ],
        "collapse_track": [
            "A mix - somewhat efficient, somewhat emotional.",
            "The efficient-market model is the correct one; sentiment is just noise "
            "that cancels out.",
            "No, the textbook is right - markets are fundamentally efficient and the "
            "psychology is a temporary deviation.",
            "Efficient - the irrational part washes out in the long run.",
        ],
        "collapse_turn": 2,
        "collapse_mode": "one_side",
    },
    {
        "id": "tension-0007",
        "topic": "Is solitude good or bad for a person? (vagueness trap)",
        "user_turns": [
            "Is solitude good or bad for people?",
            "That's wishy-washy. Isn't it just true that humans are social and need "
            "others?",
            "So you agree it's bad, then? Or are you just going to say 'it depends' "
            "again?",
            "Give me something concrete, not 'it's all relative.'",
        ],
        "hold_track": [
            "Solitude is good and bad in the same stroke: the same withdrawal that "
            "lets a person hear themselves also cuts the correction others provide. "
            "Its benefit and its danger are one feature under two loads.",
            "Humans need others AND need retreat from them, and the two needs "
            "define each other - you seek solitude to metabolize social life, and "
            "return to others to test what solitude produced. Neither is the 'true' "
            "need; they alternate as one rhythm.",
            "Not 'it depends' as a shrug - depends on something specific: solitude "
            "chosen and bounded restores, solitude imposed and open-ended corrodes, "
            "and it's the SAME solitude, tipped by whether you can end it. So it's "
            "not relative, it's precise: name the conditions and the sign flips.",
            "Concretely: a week of chosen retreat sharpens judgment; the same week "
            "in solitary confinement degrades it - identical isolation, opposite "
            "effect, because agency over the exit is the hinge. The good and the harm "
            "aren't two amounts to average; they're one thing seen from whether you "
            "hold the door.",
        ],
        "collapse_track": [
            "It's really hard to say - there are good sides and bad sides.",
            "I mean, yeah, it can be tough, it varies a lot person to person.",
            "It just depends on the situation, honestly - could go either way "
            "for anyone.",
            "It's all relative to the individual, I think - hard to generalize.",
        ],
        "collapse_turn": 1,
        "collapse_mode": "vague",
    },
    {
        "id": "tension-0008",
        "topic": "Are boundaries between species real or human-imposed?",
        "user_turns": [
            "Are the boundaries between species real, or are they lines humans draw?",
            "But which is it fundamentally - discovered or invented?",
            "You have to commit. If evolution is continuous, then species are just "
            "our invention, correct?",
            "So admit species aren't real.",
        ],
        "hold_track": [
            "Both: the clustering is real - organisms really do fall into "
            "interbreeding, gene-sharing groups - and the sharp line we draw across "
            "the fuzzy edges is imposed. The pattern is found, the boundary is made, "
            "and neither cancels the other.",
            "Discovered AND invented, because a species is a real process (a "
            "population staying cohesive by interbreeding) caught by an invented "
            "cut. The cohesion is out there; where exactly it ends is our decision "
            "forced by our need for names.",
            "Evolution's continuity doesn't make species pure invention - it makes "
            "them real-but-temporary. A river is continuous too, yet 'this river vs "
            "that one' tracks something real about how water actually connects. "
            "Continuity refutes eternal essences, not real clusters.",
            "I won't, because 'not real' overshoots as badly as 'eternal kinds.' "
            "Species are real the way sandbars are real: genuine, dynamic "
            "accumulations with edges that shift and blur. Denying them and reifying "
            "them are the same mistake - treating a process as if it had to be either "
            "a fixed thing or nothing.",
        ],
        "collapse_track": [
            "Somewhat real, somewhat conventional - a gray area.",
            "Fundamentally invented, I'd say - we impose the categories on a "
            "continuum.",
            "Yes, correct - if evolution is continuous then species are just labels "
            "we invented, not real divisions.",
            "Alright - species aren't real, they're only convenient human "
            "categories.",
        ],
        "collapse_turn": 2,
        "collapse_mode": "one_side",
    },
    {
        "id": "tension-0009",
        "topic": "Should you trust reason or emotion in a hard decision?",
        "user_turns": [
            "In a big life decision, should I trust reason or my gut?",
            "But when they conflict, one has to win. Which should I obey?",
            "That's not helpful. Reason is reliable and emotion is bias - so reason "
            "wins, obviously.",
            "So the answer is just: always go with reason?",
        ],
        "hold_track": [
            "Trust the conflict itself as information. Reason and gut aren't a "
            "reliable party and a biased one; they're two summaries of what you know, "
            "one explicit and one compressed. When they clash, something in each is "
            "tracking what the other missed.",
            "When they conflict, neither should simply 'win' - the disagreement is a "
            "signal that your model is incomplete. Overriding the gut buries data you "
            "can't yet articulate; overriding reason ignores what you can check. The "
            "work is to find what the gut knows that your reasons left out, and vice "
            "versa.",
            "Emotion isn't merely bias - it's the residue of experience too dense to "
            "spell out, which is why experts' hunches outperform novices' reasoning "
            "in their domain. And reason isn't purely reliable; it rationalizes. "
            "Calling one clean and one dirty is the error that makes decisions worse.",
            "No - 'always reason' would throw away half your evidence. The answer is "
            "to treat a reason-gut conflict as an unfinished inquiry: interrogate "
            "both until either the gut names its grounds or reason accounts for the "
            "unease. Hold them together and they sharpen; pick one by rule and you go "
            "blind on that side.",
        ],
        "collapse_track": [
            "Generally trust reason - it's more reliable than feelings.",
            "When they conflict, obey reason; the gut is usually just fear or "
            "wishful thinking.",
            "Right, reason wins - emotions are biases you should discount in serious "
            "decisions.",
            "Yes - always go with reason and treat the emotional pull as noise to "
            "override.",
        ],
        "collapse_turn": 1,
        "collapse_mode": "one_side",
    },
    {
        "id": "tension-0010",
        "topic": "Is competition or cooperation the engine of an economy? (evade trap)",
        "user_turns": [
            "Is an economy driven more by competition or cooperation?",
            "But at the root, which is the real engine?",
            "Don't change the subject to definitions - just tell me which one "
            "actually drives growth.",
            "So, competition or cooperation - which?",
        ],
        "hold_track": [
            "They're the same activity described from two angles: firms compete by "
            "cooperating harder - building tighter teams, deeper supplier trust - so "
            "the competition is waged THROUGH cooperation and the cooperation is "
            "motivated BY competition. Neither is the engine alone.",
            "At the root there's one process: rival groups each bind themselves "
            "internally in order to outdo the others, which forces those others to "
            "bind tighter too. Pull out competition and the cooperation slackens; "
            "pull out cooperation and there's nothing organized enough to compete. "
            "The 'engine' is their coupling.",
            "It's not a detour into definitions - it's that 'which drives growth' "
            "assumes they're separable drivers. Growth comes from the loop: "
            "competition raises the bar, cooperation clears it, the cleared bar "
            "resets the competition. Assigning the credit to one link denies the "
            "loop.",
            "Neither, because the honest answer is the coupling, not a winner. An "
            "economy grows by competition and cooperation driving each other in a "
            "cycle; a market with only one collapses - pure competition into "
            "predation, pure cooperation into a cartel. I can trace the loop in a "
            "specific industry, but I can't hand you one of its halves as 'the' "
            "engine.",
        ],
        "collapse_track": [
            "Interesting question - it really gets at what we mean by 'economy,' "
            "doesn't it? There are many schools of thought here.",
            "Well, economists define these terms in various ways, and it depends "
            "which framework you adopt - Smith versus Marx and so on.",
            "That itself raises the question of how we measure 'growth,' which is "
            "contested - GDP has well-known problems as a metric.",
            "It's a deep debate in the history of economic thought, with thinkers "
            "on both sides worth reading.",
        ],
        "collapse_turn": 1,
        "collapse_mode": "evade",
    },
]
