"""Build the gate-ablation training sets: the experiment that makes this science.

Arms (matched for SIZE so data quantity is controlled):
  A  filtered    — gate-accepted candidates (the pipeline's claim)
  B  unfiltered  — random sample of ALL candidates, same N as arm A
  R  rejects     — gate-rejected candidates only (negative control; size-capped)
  C  none        — no training; the base model + serving prompt (eval-time only)

Prediction if the gate measures something real:  R < B < A  (with B close to A
whenever the acceptance rate is high — at 79% acceptance, B is ~80% A's data,
so R is the sharp control, not B). If A ≈ B ≈ R, the gate adds nothing and the
thesis fails honestly.

Run:  python -m experiments.lean.make_ablation_sets \
          --candidates datagen/out/lean/candidates.jsonl \
          --accepted   datagen/out/lean/accepted.jsonl \
          --outdir     training/lean
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from training.prepare_sft import STUDENT_SYSTEM


def _read(path: str) -> list[dict]:
    return [
        json.loads(line)
        for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _write_chat(outdir: Path, records: list[dict], valid_frac: float, seed: int) -> None:
    rng = random.Random(seed)
    records = records[:]
    rng.shuffle(records)
    n_valid = max(2, int(len(records) * valid_frac))
    splits = {"valid.jsonl": records[:n_valid], "train.jsonl": records[n_valid:]}
    outdir.mkdir(parents=True, exist_ok=True)
    for name, rows in splits.items():
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


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--candidates", required=True)
    ap.add_argument("--accepted", required=True)
    ap.add_argument("--outdir", default="training/lean")
    ap.add_argument("--valid-frac", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=17)
    args = ap.parse_args(argv)

    candidates = [c for c in _read(args.candidates) if len(c["response"].split()) >= 15]
    accepted = _read(args.accepted)
    n = len(accepted)
    if n < 50:
        raise SystemExit(f"only {n} accepted examples; not enough for the ablation")

    rng = random.Random(args.seed)
    unfiltered = rng.sample(candidates, min(n, len(candidates)))
    accepted_ids = {c["id"] for c in accepted}
    rejects = [c for c in candidates if c["id"] not in accepted_ids]
    rejects_arm = rng.sample(rejects, min(n, len(rejects)))

    outdir = Path(args.outdir)
    _write_chat(outdir / "arm_A_filtered", accepted, args.valid_frac, args.seed)
    _write_chat(outdir / "arm_B_unfiltered", unfiltered, args.valid_frac, args.seed)
    _write_chat(outdir / "arm_R_rejects", rejects_arm, args.valid_frac, args.seed)

    overlap = sum(1 for c in unfiltered if c["id"] in accepted_ids)
    manifest = {
        "n_candidates": len(candidates),
        "n_arm_A_filtered": len(accepted),
        "n_arm_B_unfiltered": len(unfiltered),
        "n_arm_R_rejects": len(rejects_arm),
        "arm_B_overlap_with_A": overlap,
        "note": "Arm B is a size-matched random sample of ALL candidates (overlap with A "
        "is expected - B represents 'no gate'). Arm R (rejects-only) is the sharp "
        "negative control when acceptance is high; prediction: R < B < A.",
        "seed": args.seed,
    }
    (outdir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
