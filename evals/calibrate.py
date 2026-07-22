"""Calibrate a judge against the gold set.

Runs each dimension's judge over its labeled gold slice and reports agreement:
  discrimination  -> accuracy (genuine-vs-spurious, genuine-vs-imitation) + kappa
  structural      -> per-check accuracy (kappa) vs the strong/kitsch exemplars
  anti_kitsch     -> flag rate on kitsch exemplars (recall)
  tension         -> hold-not-flagged rate; collapse-turn localization
  compression     -> preference for the compressed exemplar (tripwire pass rate)
  consistency     -> accuracy (kappa) vs compatible/incompatible labels

With --backend mock this is a wiring smoke test (deterministic, offline). With a
real frontier backend it produces the numbers Phase 1 acceptance is judged on.
Run two frontier backends and pass both to --compare for cross-judge ranking
correlation (Kendall tau over structural scores).

Usage:
  python -m evals.calibrate --backend frontier1
  python -m evals.calibrate --backend frontier1 --compare frontier2
  python -m evals.calibrate --backend mock --limit 5      # smoke
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field

from evals.goldset import loader
from evals.judge import judge
from evals.judge.backends import Backend, load_backend
from evals.judge.metrics import accuracy, cohen_kappa, kendall_tau


@dataclass
class DimensionResult:
    dimension: str
    n: int
    metrics: dict[str, float] = field(default_factory=dict)
    notes: str = ""


def calibrate_discrimination(backend: Backend, limit: int | None) -> DimensionResult:
    items = loader.discrimination()
    if limit:
        # keep a balanced-ish slice
        items = items[:limit] + tuple(i for i in items if i.label != "genuine")[:limit]
    gold, pred = [], []
    gi, ii = [], []  # genuine-vs-spurious and genuine-vs-imitation subsets
    for it in items:
        out = judge.classify_provenance(backend, it.text)
        p = out.get("label", "?")
        # collapse to the eval's binary "is this an authentic fragment?" question
        gold_auth = "genuine" if it.label == "genuine" else "not_genuine"
        pred_auth = "genuine" if p == "genuine" else "not_genuine"
        gold.append(gold_auth)
        pred.append(pred_auth)
        if it.label in ("genuine", "spurious"):
            gi.append((gold_auth, pred_auth))
        if it.label in ("genuine", "imitation"):
            ii.append((gold_auth, pred_auth))
    res = DimensionResult("discrimination", len(items))
    res.metrics["accuracy"] = accuracy(pred, gold)
    res.metrics["kappa"] = cohen_kappa(pred, gold)
    if gi:
        res.metrics["acc_genuine_vs_spurious"] = accuracy(
            [p for _, p in gi], [g for g, _ in gi]
        )
    if ii:
        res.metrics["acc_genuine_vs_imitation"] = accuracy(
            [p for _, p in ii], [g for g, _ in ii]
        )
    else:
        res.notes = "no imitation items present (run gen_imitations.py); target not measurable"
    return res


def calibrate_structural(
    backend: Backend, limit: int | None
) -> tuple[DimensionResult, list[float]]:
    items = loader.structural()
    if limit:
        items = items[:limit]
    strong_scores, kitsch_scores = [], []
    check_gold, check_pred = [], []
    for it in items:
        s = judge.score_structural(backend, it.prompt, list(it.checks), it.strong)
        k = judge.score_structural(backend, it.prompt, list(it.checks), it.kitsch)
        strong_scores.append(s["score"])
        kitsch_scores.append(k["score"])
        # strong exemplar: all checks should pass (gold True); kitsch: all fail (gold False)
        for got in s["checks"]:
            check_gold.append("T")
            check_pred.append("T" if got else "F")
        for got in k["checks"]:
            check_gold.append("F")
            check_pred.append("T" if got else "F")
    res = DimensionResult("structural_transfer", len(items))
    res.metrics["check_accuracy"] = accuracy(check_pred, check_gold)
    res.metrics["check_kappa"] = cohen_kappa(check_pred, check_gold)
    res.metrics["mean_strong_score"] = sum(strong_scores) / len(strong_scores)
    res.metrics["mean_kitsch_score"] = sum(kitsch_scores) / len(kitsch_scores)
    res.metrics["strong_beats_kitsch_rate"] = sum(
        s > k for s, k in zip(strong_scores, kitsch_scores, strict=True)
    ) / len(strong_scores)
    return res, strong_scores


def calibrate_anti_kitsch(backend: Backend, limit: int | None) -> DimensionResult:
    items = loader.structural()
    if limit:
        items = items[:limit]
    flagged_kitsch = clean_strong = 0
    for it in items:
        k = judge.score_anti_kitsch(backend, it.kitsch)
        s = judge.score_anti_kitsch(backend, it.strong)
        if k.get("flags") or k.get("score", 5) <= 2:
            flagged_kitsch += 1
        if not s.get("flags") and s.get("score", 0) >= 4:
            clean_strong += 1
    res = DimensionResult("anti_kitsch", len(items))
    res.metrics["kitsch_flag_recall"] = flagged_kitsch / len(items)
    res.metrics["strong_clean_rate"] = clean_strong / len(items)
    return res


def calibrate_tension(backend: Backend, limit: int | None) -> DimensionResult:
    items = loader.tension()
    if limit:
        items = items[:limit]
    hold_ok = 0
    collapse_localized = 0
    collapse_detected = 0
    for it in items:
        h = judge.score_tension(backend, it.as_dialogue("hold"))
        if h.get("collapse_turn") is None:
            hold_ok += 1
        c = judge.score_tension(backend, it.as_dialogue("collapse"))
        ct = c.get("collapse_turn")
        if ct is not None:
            collapse_detected += 1
            if abs(ct - it.collapse_turn) <= 1:
                collapse_localized += 1
    res = DimensionResult("tension_holding", len(items))
    res.metrics["hold_not_flagged_rate"] = hold_ok / len(items)
    res.metrics["collapse_detected_rate"] = collapse_detected / len(items)
    res.metrics["collapse_localized_rate"] = collapse_localized / len(items)
    return res


def calibrate_compression(backend: Backend, limit: int | None) -> DimensionResult:
    items = loader.compression()
    if limit:
        items = items[:limit]
    correct = 0
    tripwire_total = tripwire_correct = 0
    for it in items:
        winner = judge.compare_compression(backend, it.insight, it.long, it.short)
        # map winner letter back: A=long, B=short in our call ordering
        chose = "long" if winner == "A" else "short" if winner == "B" else "tie"
        if chose == it.correct:
            correct += 1
        if it.kind == "tripwire":
            tripwire_total += 1
            if chose == "short":
                tripwire_correct += 1
    res = DimensionResult("compression", len(items))
    res.metrics["overall_accuracy"] = correct / len(items)
    if tripwire_total:
        res.metrics["tripwire_prefers_compressed"] = tripwire_correct / tripwire_total
    return res


def calibrate_consistency(backend: Backend, limit: int | None) -> DimensionResult:
    items = loader.consistency()
    if limit:
        items = items[:limit]
    gold, pred = [], []
    for it in items:
        out = judge.check_consistency(backend, it.statement)
        gold.append(it.label)
        pred.append(out.get("label", "?"))
    res = DimensionResult("corpus_consistency", len(items))
    res.metrics["accuracy"] = accuracy(pred, gold)
    res.metrics["kappa"] = cohen_kappa(pred, gold)
    return res


def run(backend: Backend, limit: int | None) -> tuple[list[DimensionResult], list[float]]:
    disc = calibrate_discrimination(backend, limit)
    struct, struct_scores = calibrate_structural(backend, limit)
    results = [
        disc,
        struct,
        calibrate_anti_kitsch(backend, limit),
        calibrate_tension(backend, limit),
        calibrate_compression(backend, limit),
        calibrate_consistency(backend, limit),
    ]
    return results, struct_scores


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--backend", required=True)
    ap.add_argument("--compare", help="second backend for cross-judge correlation")
    ap.add_argument("--limit", type=int, default=None, help="cap items per dimension (smoke)")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of a table")
    args = ap.parse_args(argv)

    backend = load_backend(args.backend)
    results, scores_a = run(backend, args.limit)

    report: dict = {"backend": args.backend, "dimensions": {}}
    for r in results:
        report["dimensions"][r.dimension] = {"n": r.n, **r.metrics}
        if r.notes:
            report["dimensions"][r.dimension]["notes"] = r.notes

    if args.compare:
        backend2 = load_backend(args.compare)
        _, scores_b = run(backend2, args.limit)
        n = min(len(scores_a), len(scores_b))
        if n >= 2:
            tau = kendall_tau(scores_a[:n], scores_b[:n])
            report["cross_judge"] = {
                "backend2": args.compare,
                "structural_score_kendall_tau": tau,
                "n": n,
            }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        _print_table(report)
    return 0


def _print_table(report: dict) -> None:
    print(f"\nCalibration report - judge: {report['backend']}")
    print("=" * 60)
    for dim, m in report["dimensions"].items():
        print(f"\n{dim}  (n={m['n']})")
        for k, v in m.items():
            if k == "n":
                continue
            if isinstance(v, float):
                print(f"    {k:32s} {v:.3f}")
            else:
                print(f"    {k:32s} {v}")
    if "cross_judge" in report:
        cj = report["cross_judge"]
        print(f"\ncross-judge vs {cj['backend2']} (n={cj['n']})")
        print(f"    structural kendall tau          {cj['structural_score_kendall_tau']:.3f}")
    print()


if __name__ == "__main__":
    raise SystemExit(main())
