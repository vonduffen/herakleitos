"""Convert eval-gated accepted candidates into mlx-lm chat SFT format.

Emits train.jsonl / valid.jsonl in {"messages": [...]} form. The student's
system prompt at training time matches the harness serving prompt (structure,
not style), so the behavior is trained under the same contract it is served
under.

Run:  python -m training.prepare_sft --in datagen/out/accepted.jsonl \
          --outdir training/data [--valid-frac 0.1]
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

STUDENT_SYSTEM = (
    "You reason in processes, exchanges, and held tensions: what persists "
    "through change, how opposites depend on each other, what tension holds a "
    "thing together. Plain, concrete prose. No philosopher quotes, no 'flux', "
    "no oracular voice."
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--outdir", default="training/data")
    ap.add_argument("--valid-frac", type=float, default=0.1)
    ap.add_argument("--seed", type=int, default=17)
    args = ap.parse_args(argv)

    records = [
        json.loads(line)
        for line in Path(args.inp).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    rng = random.Random(args.seed)
    rng.shuffle(records)

    n_valid = max(2, int(len(records) * args.valid_frac))
    valid, train = records[:n_valid], records[n_valid:]

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    def write(name: str, rows: list[dict]) -> None:
        with (outdir / name).open("w", encoding="utf-8") as f:
            for r in rows:
                f.write(
                    json.dumps(
                        {
                            "messages": [
                                {"role": "system", "content": STUDENT_SYSTEM},
                                {"role": "user", "content": r["prompt"]},
                                {"role": "assistant", "content": r["response"]},
                            ]
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )

    write("train.jsonl", train)
    write("valid.jsonl", valid)
    print(f"train: {len(train)}  valid: {len(valid)}  -> {outdir}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
