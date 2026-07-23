"""Eval-gated filtering of teacher candidates (the Phase 2 gate).

Routes every candidate through the Phase 1 rubrics using an OPEN-WEIGHTS judge
(different family from the teacher - checked here against config). Frontier
judges are never used in this loop.

Per candidate:
  anti_kitsch   -> hard reject if any flag or score <= 2
  structural    -> generic move checks from the seed's target moves; keep if
                   score >= threshold
  consistency   -> reject if judged incompatible with corpus commitments
  decontam      -> reject any candidate overlapping the gold set
  dedupe        -> near-duplicate candidates (shingle overlap) collapsed

Rejection reasons are logged; the distribution is a diagnostic report.

Run:  OLLAMA_API_KEY=local python -m datagen.filter \
          --in datagen/out/candidates.jsonl --backend judge_local \
          --out datagen/out/accepted.jsonl
"""

from __future__ import annotations

import argparse
import json
import threading
import tomllib
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from evals.decontaminate import shingles
from evals.goldset import loader as gold
from evals.judge import judge
from evals.judge.backends import CONFIG_PATH, load_backend

CHECK_TEMPLATES = {
    "identity-through-change": "Locates what persists in a maintained pattern or "
    "process rather than in unchanged material or a fixed essence.",
    "unity-of-opposites": "Shows opposed descriptions to be jointly true and "
    "structurally interdependent, without eliminating either.",
    "process-primacy": "Reframes the static-seeming thing as an ongoing process "
    "whose stability is produced by activity.",
    "measure-and-exchange": "Identifies a governed rate, balance, or exchange "
    "that regulates the change.",
    "tension-as-structure": "Shows opposed forces in tension as constituting the "
    "thing, such that removing the tension destroys it.",
    "perspectival-opposition": "Shows one thing bearing opposite values relative "
    "to precisely named different relata or measures.",
}

STRUCT_THRESHOLD = 4
KITSCH_MIN_SCORE = 3
DEDUPE_OVERLAP = 0.6
DECONTAM_OVERLAP = 0.5


def _different_family_or_die(teacher_backend: str, judge_backend: str) -> None:
    cfg = tomllib.loads(CONFIG_PATH.read_text())["backends"]
    tm = cfg.get(teacher_backend, {}).get("model", "").lower()
    jm = cfg.get(judge_backend, {}).get("model", "").lower()
    families = ["qwen", "deepseek", "mistral", "glm", "llama", "gpt", "claude", "gemini"]
    tf = next((f for f in families if f in tm), tm)
    jf = next((f for f in families if f in jm), jm)
    if tf == jf:
        raise SystemExit(
            f"separation of powers violated: teacher ({tm}) and judge ({jm}) "
            "are the same model family"
        )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--backend", required=True, help="open-weights judge backend")
    ap.add_argument("--teacher-backend", default="teacher_local")
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--workers", type=int, default=1, help="concurrent candidates (1 for local)")
    ap.add_argument("--resume", action="store_true", help="keep prior accepted; judge the rest")
    args = ap.parse_args(argv)

    _different_family_or_die(args.teacher_backend, args.backend)
    backend = load_backend(args.backend)

    candidates = [
        json.loads(line)
        for line in Path(args.inp).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if args.limit:
        candidates = candidates[: args.limit]

    gold_texts = gold.all_gold_text()
    gold_shingle_sets = [shingles(g) for g in gold_texts]

    reasons: Counter[str] = Counter()
    accepted: list[dict] = []
    accepted_shingles: list[set[str]] = []
    lock = threading.Lock()

    prior_ids: set[str] = set()
    if args.resume and Path(args.out).exists():
        for line in Path(args.out).read_text(encoding="utf-8").splitlines():
            if line.strip():
                rec = json.loads(line)
                prior_ids.add(rec["id"])
                accepted.append(rec)
                accepted_shingles.append(shingles(rec["response"]))
        print(f"resume: {len(prior_ids)} previously accepted kept")

    # Cheap, order-dependent screens run sequentially first (dedupe needs order).
    to_judge: list[dict] = []
    for c in candidates:
        if c["id"] in prior_ids:
            continue
        text = c["response"].strip()
        if len(text.split()) < 15:
            reasons["too_short"] += 1
            continue
        st = shingles(text)
        if any(
            sg and st and len(st & sg) / min(len(st), len(sg)) >= DECONTAM_OVERLAP
            for sg in gold_shingle_sets
        ):
            reasons["goldset_contamination"] += 1
            continue
        if any(
            sa and len(st & sa) / min(len(st), len(sa)) >= DEDUPE_OVERLAP
            for sa in accepted_shingles
        ):
            reasons["near_duplicate"] += 1
            continue
        accepted_shingles.append(st)  # reserve; judged next
        c["_shingles_reserved"] = True
        to_judge.append(c)

    def judge_one(c):
        text = c["response"].strip()
        ak = judge.score_anti_kitsch(backend, text)
        if ak.get("flags") or ak.get("score", 5) < KITSCH_MIN_SCORE:
            return None, f"kitsch:{','.join(ak.get('flags', ['low_score']))}"
        checks = [CHECK_TEMPLATES[m] for m in c["target_moves"] if m in CHECK_TEMPLATES]
        s = judge.score_structural(backend, c["prompt"], checks, text)
        if s.get("score", 0) < STRUCT_THRESHOLD:
            return None, "structural_below_threshold"
        cc = judge.check_consistency(backend, text[:800])
        if cc.get("label") != "compatible":
            return None, "consistency_incompatible"
        c["gate"] = {
            "judge_backend": args.backend,
            "anti_kitsch_score": ak.get("score"),
            "structural_score": s.get("score"),
            "checks_passed": sum(bool(x) for x in s.get("checks", [])),
            "checks_total": len(checks),
        }
        return c, None

    n_judged = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futs = {pool.submit(judge_one, c): c["id"] for c in to_judge}
        for fut in as_completed(futs):
            try:
                ok, reason = fut.result()
            except Exception as e:  # noqa: BLE001 - judge hiccup: log, skip candidate
                ok, reason = None, f"judge_error:{type(e).__name__}"
            with lock:
                n_judged += 1
                if ok is not None:
                    accepted.append(ok)
                else:
                    reasons[reason] += 1
                if n_judged % 100 == 0:
                    print(f"{n_judged}/{len(to_judge)} judged, {len(accepted)} accepted")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for c in accepted:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    total = len(candidates)
    print(f"\naccepted {len(accepted)}/{total} ({100 * len(accepted) / max(total, 1):.0f}%)")
    print("rejection reasons:")
    for r, n in reasons.most_common():
        print(f"  {n:4d}  {r}")
    (out.parent / "rejection_report.json").write_text(
        json.dumps({"total": total, "accepted": len(accepted), "reasons": dict(reasons)}, indent=2)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
