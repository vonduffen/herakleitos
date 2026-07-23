"""Expand the hand-authored scenario bank to Phase 2 scale using the teacher.

Seeds are PROMPTS, not training data, so teacher-generated scenarios are fine
under the frontier/open-weights rules (the teacher is open-weights anyway).
The hand-authored scenarios serve as few-shot style anchors; new scenarios are
deduped (shingle overlap) against both the hand bank and the gold set.

Run:  python -m datagen.expand_seeds --backend teacher --target 2000 \
          --out datagen/out/seeds_expanded.jsonl
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from datagen.seeds import MOVES, SCENARIOS, TASK_TEMPLATES, Seed, build_seeds
from evals.decontaminate import shingles
from evals.goldset import loader as gold
from evals.judge.backends import load_backend
from evals.judge.judge import strip_thinking

EXPAND_PROMPT = """Here are examples of one-line scenario descriptions for the domain \
"{domain}". Each names a concrete situation where something persists through change, \
opposites depend on each other, or tension holds a thing together — WITHOUT naming any \
philosopher or using the words 'flux' or 'eternal':

{examples}

Write {n} NEW one-line scenarios for the same domain, same register, same concreteness. \
Different situations — do not rephrase the examples. One per line, no numbering, \
no commentary. /no_think"""


def expand(backend_name: str, target: int, seed: int = 11) -> list[Seed]:
    backend = load_backend(backend_name)
    if hasattr(backend, "temperature"):
        backend.temperature = 0.9
    rng = random.Random(seed)

    hand = build_seeds()
    gold_shingle = [shingles(t) for t in gold.all_gold_text()]
    seen: list[set[str]] = [shingles(s.prompt) for s in hand]

    def is_fresh(text: str) -> bool:
        st = shingles(text)
        if not st:
            return False
        for sg in seen + gold_shingle:
            if sg and len(st & sg) / min(len(st), len(sg)) >= 0.5:
                return False
        return True

    domains = list(SCENARIOS)
    per_domain_needed = max(1, (target - len(hand)) // len(domains) + 1)
    new_scenarios: list[tuple[str, str]] = []  # (domain, scenario)

    for domain in domains:
        got = 0
        rounds = 0
        while got < per_domain_needed and rounds < 8:
            rounds += 1
            examples = "\n".join(
                f"- {s}" for s in rng.sample(SCENARIOS[domain], min(6, len(SCENARIOS[domain])))
            )
            raw = strip_thinking(
                backend.complete(
                    "You write concrete scenario one-liners for a reasoning dataset.",
                    EXPAND_PROMPT.format(domain=domain, examples=examples, n=20),
                    max_tokens=1200,
                )
            )
            for line in raw.splitlines():
                line = line.strip().lstrip("-•0123456789.) ").strip()
                if 6 <= len(line.split()) <= 40 and is_fresh(line):
                    seen.append(shingles(line))
                    new_scenarios.append((domain, line))
                    got += 1
                    if got >= per_domain_needed:
                        break
        print(f"{domain}: +{got} scenarios")

    task_names = list(TASK_TEMPLATES)
    seeds: list[Seed] = list(hand)
    n = len(hand)
    for domain, scenario in new_scenarios:
        task = task_names[n % len(task_names)]
        moves = (MOVES[n % len(MOVES)], MOVES[(n + 2) % len(MOVES)])
        n += 1
        seeds.append(
            Seed(
                id=f"seed-x{n:05d}",
                domain=domain,
                task_type=task,
                prompt=TASK_TEMPLATES[task].format(scenario=scenario),
                target_moves=moves,
            )
        )
        if len(seeds) >= target:
            break
    return seeds


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--backend", required=True)
    ap.add_argument("--target", type=int, default=2000)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    seeds = expand(args.backend, args.target)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for s in seeds:
            f.write(
                json.dumps(
                    {
                        "id": s.id,
                        "domain": s.domain,
                        "task_type": s.task_type,
                        "prompt": s.prompt,
                        "target_moves": list(s.target_moves),
                        "provenance": (
                            "hand" if not s.id.startswith("seed-x") else "teacher-expanded"
                        ),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
    print(f"wrote {len(seeds)} seeds to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
