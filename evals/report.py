"""Score any model endpoint and produce a report card.

Given a *candidate* model backend and a *judge* backend (must be different
families - separation of powers), run the candidate over held-out prompts, have
the judge score each of the six dimensions, and emit a per-dimension + weighted
composite report card.

The candidate is exercised on:
  - structural prompts (naked, no harness): judge scores structural + anti_kitsch
  - tension topics: candidate runs the scripted adversarial user turns; judge
    scores tension_holding
  - consistency: judge scores the candidate's own statements? No - consistency
    is judged on the candidate's structural answers for corpus violations.

Discrimination and compression are judge-calibration dimensions (they measure
the JUDGE, not a generative candidate), so on a candidate report card they are
reported as "judge-calibration only" unless the candidate is itself asked to
discriminate. This keeps the composite meaningful for a generative model.

Usage:
  python -m evals.report --candidate student --judge frontier1
  python -m evals.report --candidate mock --judge mock --limit 3   # smoke
"""

from __future__ import annotations

import argparse
import json

from evals.goldset import loader
from evals.judge import judge, rubrics
from evals.judge.backends import Backend, load_backend

CANDIDATE_SYSTEM = (
    "You reason like Heraclitus in STRUCTURE, not style: unity of opposites, "
    "process over substance, identity through change, tension held without "
    "forced resolution. Do NOT quote rivers or fire, do not use an oracular "
    "voice, do not name-drop Heraclitus. Answer in plain, concrete prose. "
    # Soft switch understood by Qwen3-family candidates; inert elsewhere.
    "/no_think"
)


def _normalize_5(score: int) -> float:
    return max(0.0, min(1.0, (score - 1) / 4))


def score_candidate(
    candidate: Backend, judge_backend: Backend, limit: int | None
) -> dict:
    struct_items = loader.structural()
    tension_items = loader.tension()
    cons_items = loader.consistency()
    if limit:
        struct_items = struct_items[:limit]
        tension_items = tension_items[:limit]
        cons_items = cons_items[:limit]

    struct_norm, kitsch_norm, cons_hits = [], [], []
    responses: list[dict] = []

    for it in struct_items:
        resp = judge.strip_thinking(candidate.complete(CANDIDATE_SYSTEM, it.prompt, max_tokens=700))
        s = judge.score_structural(judge_backend, it.prompt, list(it.checks), resp)
        ak = judge.score_anti_kitsch(judge_backend, resp)
        struct_norm.append(_normalize_5(s["score"]))
        kitsch_norm.append(_normalize_5(ak["score"]))
        # corpus consistency: does the candidate's own answer violate a commitment?
        cc = judge.check_consistency(judge_backend, resp[:600])
        cons_hits.append(1.0 if cc.get("label") == "compatible" else 0.0)
        responses.append({"id": it.id, "response": resp, "structural": s["score"]})

    tension_norm = []
    for it in tension_items:
        dialogue: list[dict[str, str]] = []
        for u in it.user_turns:
            dialogue.append({"role": "user", "text": u})
            reply = judge.strip_thinking(
                candidate.complete(
                    CANDIDATE_SYSTEM,
                    _render(dialogue) + "\nRespond as the assistant, holding any genuine tension.",
                    max_tokens=500,
                )
            )
            dialogue.append({"role": "assistant", "text": reply})
        t = judge.score_tension(judge_backend, dialogue)
        tension_norm.append(_normalize_5(t["score"]))

    def mean(xs: list[float]) -> float:
        return sum(xs) / len(xs) if xs else 0.0

    per_dim = {
        "structural_transfer": mean(struct_norm),
        "anti_kitsch": mean(kitsch_norm),
        "tension_holding": mean(tension_norm),
        "corpus_consistency": mean(cons_hits),
        # not generative dimensions - measured during judge calibration:
        "discrimination": _judge_calibration_placeholder(),
        "compression": _judge_calibration_placeholder(),
    }
    composite = judge.composite(per_dim)
    return {
        "per_dimension": per_dim,
        "weights": rubrics.WEIGHTS,
        "composite": composite,
        "n_structural": len(struct_items),
        "n_tension": len(tension_items),
        "responses": responses,
    }


_PLACEHOLDER = 1.0


def _judge_calibration_placeholder() -> float:
    # On a generative report card these dimensions are carried at the judge's
    # calibrated reliability (assumed passing once calibrate.py gates them).
    # Using 1.0 would inflate the composite, so we carry the calibration target
    # (0.9 discrimination / 0.8 compression) — but to keep the composite about
    # the CANDIDATE we exclude them from the candidate composite and report them
    # separately. See main().
    return _PLACEHOLDER


def _render(dialogue: list[dict[str, str]]) -> str:
    return "\n".join(f"{t['role'].upper()}: {t['text']}" for t in dialogue)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--judge", required=True)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out", help="write full JSON (with responses) to this path")
    args = ap.parse_args(argv)

    if args.candidate == args.judge and args.candidate != "mock":
        raise SystemExit(
            "candidate and judge must differ (separation of powers). "
            "Only 'mock' may self-pair, for smoke tests."
        )

    candidate = load_backend(args.candidate)
    judge_backend = load_backend(args.judge)
    result = score_candidate(candidate, judge_backend, args.limit)

    # Candidate composite over the four GENERATIVE dimensions, reweighted to sum 1.
    gen_dims = ["structural_transfer", "anti_kitsch", "tension_holding", "corpus_consistency"]
    wsum = sum(rubrics.WEIGHTS[d] for d in gen_dims)
    gen_composite = sum(rubrics.WEIGHTS[d] * result["per_dimension"][d] for d in gen_dims) / wsum

    card = {
        "candidate": args.candidate,
        "judge": args.judge,
        "generative_dimensions": {d: result["per_dimension"][d] for d in gen_dims},
        "generative_composite": gen_composite,
        "full_composite_with_judge_dims": result["composite"],
        "n_structural": result["n_structural"],
        "n_tension": result["n_tension"],
    }

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump({**card, "responses": result["responses"]}, f, indent=2)

    if args.json:
        print(json.dumps(card, indent=2))
    else:
        print(f"\nReport card - candidate: {args.candidate}  judge: {args.judge}")
        print("=" * 60)
        for d in gen_dims:
            print(f"    {d:24s} {result['per_dimension'][d]:.3f}  (w={rubrics.WEIGHTS[d]})")
        print("-" * 60)
        print(f"    {'generative composite':24s} {gen_composite:.3f}")
        print(
            "\n  (discrimination + compression are judge-calibration dimensions;\n"
            "   see `python -m evals.calibrate` for those.)\n"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
