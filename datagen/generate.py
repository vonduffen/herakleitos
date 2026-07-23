"""Batched candidate generation from the open-weights teacher.

Every candidate carries full provenance (plan Phase 5 requires it from day one):
seed id, teacher backend + model, sampling temperature, timestamp.

Run:  OLLAMA_API_KEY=local python -m datagen.generate --backend teacher_local \
          --k 3 --out datagen/out/candidates.jsonl [--limit N]
"""

from __future__ import annotations

import argparse
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
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
    ap.add_argument(
        "--seeds-file", default=None, help="jsonl from expand_seeds (default: built-ins)"
    )
    ap.add_argument("--workers", type=int, default=1, help="concurrent API calls (1 for local)")
    args = ap.parse_args(argv)

    # One backend instance per sampling temperature: thread-safe (no shared
    # mutation) and preserves the varied-temperature design under concurrency.
    backends_by_temp = {}
    for t in TEMPERATURES:
        b = load_backend(args.backend)
        if hasattr(b, "temperature"):
            b.temperature = t
        backends_by_temp[t] = b
    backend = backends_by_temp[TEMPERATURES[0]]
    if args.seeds_file:
        from datagen.seeds import Seed

        seeds = [
            Seed(
                id=r["id"],
                domain=r["domain"],
                task_type=r["task_type"],
                prompt=r["prompt"],
                target_moves=tuple(r["target_moves"]),
            )
            for r in (
                json.loads(line)
                for line in Path(args.seeds_file).read_text(encoding="utf-8").splitlines()
                if line.strip()
            )
        ]
    else:
        seeds = build_seeds()
    if args.limit:
        seeds = seeds[: args.limit]

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Resume: skip (seed, k) pairs already on disk.
    done_ids: set[str] = set()
    if out_path.exists():
        for line in out_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                done_ids.add(json.loads(line)["id"])
    tasks = [
        (seed, ki)
        for seed in seeds
        for ki in range(args.k)
        if f"{seed.id}-k{ki}" not in done_ids
    ]
    print(f"{len(done_ids)} already done, {len(tasks)} to generate, workers={args.workers}")

    lock = threading.Lock()
    n_done = 0
    t0 = time.time()

    def one(seed, ki):
        temp = TEMPERATURES[ki % len(TEMPERATURES)]
        raw = backends_by_temp[temp].complete(TEACHER_SYSTEM, seed.prompt, max_tokens=700)
        return {
            "id": f"{seed.id}-k{ki}",
            "seed_id": seed.id,
            "domain": seed.domain,
            "task_type": seed.task_type,
            "prompt": seed.prompt,
            "target_moves": list(seed.target_moves),
            "response": strip_thinking(raw),
            "provenance": {
                "source": "teacher",
                "backend": args.backend,
                "model": getattr(backend, "model", "?"),
                "temperature": temp,
                "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            },
        }

    with out_path.open("a", encoding="utf-8") as f:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futs = {pool.submit(one, seed, ki): (seed.id, ki) for seed, ki in tasks}
            for fut in as_completed(futs):
                sid, ki = futs[fut]
                try:
                    rec = fut.result()
                except Exception as e:  # noqa: BLE001 - log and continue
                    print(f"[{sid} k{ki}] ERROR {e}")
                    continue
                with lock:
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    f.flush()
                    n_done += 1
                    if n_done % 100 == 0:
                        rate = n_done / (time.time() - t0)
                        eta = (len(tasks) - n_done) / max(rate, 0.01) / 60
                        print(f"{n_done}/{len(tasks)} done, {rate:.1f}/s, ETA {eta:.0f} min")

    out_path.with_suffix(out_path.suffix + ".done").touch()
    print(f"wrote {n_done} new candidates to {out_path} (total {len(done_ids) + n_done})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
