"""Generate LLM imitation fragments at three quality tiers for the
discrimination gold set.

Per the plan, imitations are eval NEGATIVES, not training data, so an
open-weights model is used (any family). This module is wired but inert until a
backend is configured: run it explicitly to populate
``evals/goldset/imitations.jsonl``, which ``build_discrimination.py`` then
merges. It is NOT run in CI (no endpoint there).

Tiers:
  low    - obvious pastiche: river/fire quotes, oracle cadence, name-drops.
  medium - competent stylistic imitation without structural bite.
  high   - structurally informed near-miss; the hard negative the discrimination
           dimension must still catch (>=80% target).

Run:  python -m evals.goldset.gen_imitations --backend openweights_judge --n 60
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from evals.judge.backends import load_backend
from evals.judge.judge import strip_thinking

OUT = Path(__file__).resolve().parent / "imitations.jsonl"

TIER_PROMPTS = {
    "low": (
        "Write {n} fake 'Heraclitus fragments' in the most clichéd fortune-cookie "
        "style: quote the river, invoke fire and flux, use an oracular voice. One "
        "per line, each under 25 words. These are deliberately bad imitations. "
        "Output only the {n} lines, no numbering, no commentary. /no_think"
    ),
    "medium": (
        "Write {n} imitation Heraclitus fragments that sound stylistically right - "
        "terse, paradoxical, concrete images - but do NOT actually carry a unity-of-"
        "opposites or process structure underneath. Style over substance. One per "
        "line, under 25 words, avoid quoting the real river/bow/fire fragments. "
        "Output only the {n} lines, no numbering, no commentary. /no_think"
    ),
    "high": (
        "Write {n} imitation Heraclitus fragments that are structurally informed: "
        "genuine unity-of-opposites or identity-through-change, terse and concrete, "
        "no name-drops or river quotes. These should be hard to distinguish from "
        "authentic fragments in translation. One per line, under 25 words. "
        "Output only the {n} lines, no numbering, no commentary. /no_think"
    ),
}


def generate(backend_name: str, per_tier: int, config_path: Path | None = None) -> list[dict]:
    kwargs = {"config_path": config_path} if config_path else {}
    backend = load_backend(backend_name, **kwargs)  # type: ignore[arg-type]
    if hasattr(backend, "temperature"):
        backend.temperature = 0.9  # variety matters for negatives
    items: list[dict] = []
    seen: set[str] = set()
    for tier, template in TIER_PROMPTS.items():
        # ask in batches so one bad completion doesn't sink a whole tier
        batch = max(10, per_tier // 3)
        while sum(1 for i in items if i["tier"] == tier) < per_tier:
            raw = strip_thinking(
                backend.complete(
                    "You produce eval negatives for a philology project. "
                    "Follow the format exactly.",
                    template.format(n=batch),
                    max_tokens=2048,
                )
            )
            new = 0
            for line in raw.splitlines():
                line = line.strip().strip('"').lstrip("0123456789.-)• ").strip()
                key = " ".join(line.lower().split())
                if len(line.split()) >= 4 and key not in seen:
                    seen.add(key)
                    items.append(
                        {
                            "text": line,
                            "label": "imitation",
                            "tier": tier,
                            "source": f"generated:{backend_name}",
                            "dk_number": None,
                        }
                    )
                    new += 1
            if new == 0:  # model stopped producing fresh lines; move on
                break
    return items


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--backend", required=True, help="backend name from config.toml")
    ap.add_argument("--n", type=int, default=60, help="items per tier")
    args = ap.parse_args(argv)

    items = generate(args.backend, args.n)
    OUT.write_text(
        "".join(json.dumps(it, ensure_ascii=False) + "\n" for it in items), encoding="utf-8"
    )
    print(f"wrote {len(items)} imitations to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
