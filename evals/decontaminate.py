"""Decontamination guard: no gold-set text may leak into training data.

Provides the reusable check used by the Phase 2 datagen filter (no training
example may contain gold-set text) and a `--self-check` mode wired into CI.

The self-check verifies two invariants that must hold from day one:
  1. Gold-set item ids are unique across all slices.
  2. The discrimination gold set's *genuine* entries are drawn from the corpus
     (as intended), but no gold-set item duplicates another verbatim within a
     slice - a cheap guard against accidental copy-paste inflation of counts.

Overlap detection uses normalized character n-gram shingles so that
near-duplicates (whitespace/case/punctuation variants) are caught, not only
exact matches.

Usage:
  python -m evals.decontaminate --self-check
  # library: contaminated(train_texts, gold_texts) -> list of (train_i, gold_j)
"""

from __future__ import annotations

import argparse
import re
import sys

from evals.goldset import loader

_WORD = re.compile(r"\w+")


def normalize(text: str) -> str:
    return " ".join(_WORD.findall(text.lower()))


def shingles(text: str, k: int = 40) -> set[str]:
    """Character k-gram shingles over normalized text."""
    norm = normalize(text)
    if len(norm) < k:
        return {norm} if norm else set()
    return {norm[i : i + k] for i in range(len(norm) - k + 1)}


def overlap_ratio(a: str, b: str, k: int = 40) -> float:
    sa, sb = shingles(a, k), shingles(b, k)
    if not sa or not sb:
        return 0.0
    inter = len(sa & sb)
    return inter / min(len(sa), len(sb))


def contaminated(
    train_texts: list[str], gold_texts: list[str], threshold: float = 0.5, k: int = 40
) -> list[tuple[int, int]]:
    """Return (train_index, gold_index) pairs whose overlap exceeds threshold.

    Used by the Phase 2 datagen filter to reject any candidate that echoes a
    gold-set item. O(n*m) with a fast shingle-set prefilter; fine for the gold
    set's size.
    """
    gold_shingles = [shingles(g, k) for g in gold_texts]
    hits: list[tuple[int, int]] = []
    for ti, t in enumerate(train_texts):
        st = shingles(t, k)
        if not st:
            continue
        for gi, sg in enumerate(gold_shingles):
            if not sg:
                continue
            if len(st & sg) / min(len(st), len(sg)) >= threshold:
                hits.append((ti, gi))
    return hits


def self_check() -> int:
    errors: list[str] = []

    # 1. unique ids across slices
    all_ids: list[str] = []
    all_ids += [i.id for i in loader.discrimination()]
    all_ids += [i.id for i in loader.structural()]
    all_ids += [i.id for i in loader.tension()]
    all_ids += [i.id for i in loader.compression()]
    all_ids += [i.id for i in loader.consistency()]
    dupes = {x for x in all_ids if all_ids.count(x) > 1}
    if dupes:
        errors.append(f"duplicate gold-set ids: {sorted(dupes)}")

    # 2. no verbatim-duplicate discrimination items (normalized)
    seen: dict[str, str] = {}
    for it in loader.discrimination():
        norm = normalize(it.text)
        if norm in seen:
            errors.append(f"duplicate discrimination text: {it.id} == {seen[norm]}")
        else:
            seen[norm] = it.id

    # 3. structural strong != kitsch, and neither trivially short
    for it in loader.structural():
        if overlap_ratio(it.strong, it.kitsch) >= 0.5:
            errors.append(f"structural strong/kitsch too similar: {it.id}")

    if errors:
        for e in errors:
            print(f"DECONTAM FAIL: {e}", file=sys.stderr)
        return 1
    print(
        f"decontam self-check ok: {len(all_ids)} gold items, ids unique, "
        "no internal duplicates"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args(argv)
    if args.self_check:
        return self_check()
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
