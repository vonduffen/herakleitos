"""Batched candidate generation from the open-weights teacher.

Every candidate carries full provenance (plan Phase 5 requires it from day one):
seed id, teacher backend + model, sampling temperature, timestamp.

Run:  OLLAMA_API_KEY=local python -m datagen.generate --backend teacher_local \
          --k 3 --out datagen/out/candidates.jsonl [--limit N]
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from datagen.seeds import build_seeds
from evals.judge.backends import load_backend
from evals.judge.judge import strip_thinking

TEACHER_SYSTEM = (
    "You are a writer who thinks in processes, exchanges, and held tensions. "
    "Answer the task in plain, concrete, contemporary prose. Do not quote or "
    "mention any philosopher. Never use the words 'flux', 'river of', 'eternal', "
    "or an oracular voice. Show the structure of the situation - what persists "
    "through change, how opposites depend on each other, what tension holds the "
    "thing together - by analyzing the case itself. 2-6 sentences unless the "
    "task asks for fewer. /no_think"
)

TEMPERATURES = [0.7, 0.9, 1.1]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--backend", required=True)
    ap.add_argument("--k", type=int, default=3, help="candidates per seed")
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=None, help="cap number of seeds")
    args = ap.parse_args(argv)

    backend = load_backend(args.backend)
    seeds = build_seeds()
    if args.limit:
        seeds = seeds[: args.limit]

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    n_done = 0
    t0 = time.time()
    with out_path.open("w", encoding="utf-8") as f:
        for si, seed in enumerate(seeds):
            for ki in range(args.k):
                temp = TEMPERATURES[ki % len(TEMPERATURES)]
                backend.temperature = temp  # OpenAICompatBackend dataclass field
                try:
                    raw = backend.complete(TEACHER_SYSTEM, seed.prompt, max_tokens=700)
                except Exception as e:  # noqa: BLE001 - log and continue
                    print(f"[{seed.id} k{ki}] ERROR {e}")
                    continue
                text = strip_thinking(raw)
                rec = {
                    "id": f"{seed.id}-k{ki}",
                    "seed_id": seed.id,
                    "domain": seed.domain,
                    "task_type": seed.task_type,
                    "prompt": seed.prompt,
                    "target_moves": list(seed.target_moves),
                    "response": text,
                    "provenance": {
                        "source": "teacher",
                        "backend": args.backend,
                        "model": getattr(backend, "model", "?"),
                        "temperature": temp,
                        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    },
                }
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                f.flush()
                n_done += 1
            if (si + 1) % 5 == 0:
                rate = n_done / (time.time() - t0)
                print(f"{si + 1}/{len(seeds)} seeds, {n_done} candidates, {rate:.2f}/s")

    print(f"wrote {n_done} candidates to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
