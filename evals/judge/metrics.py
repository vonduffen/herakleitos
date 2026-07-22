"""Agreement metrics for judge calibration (pure stdlib, no scipy)."""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence


def accuracy(pred: Sequence[str], gold: Sequence[str]) -> float:
    if len(pred) != len(gold) or not gold:
        raise ValueError("pred and gold must be equal-length, non-empty")
    return sum(p == g for p, g in zip(pred, gold, strict=True)) / len(gold)


def cohen_kappa(pred: Sequence[str], gold: Sequence[str]) -> float:
    """Cohen's kappa for two label sequences."""
    if len(pred) != len(gold) or not gold:
        raise ValueError("pred and gold must be equal-length, non-empty")
    n = len(gold)
    po = accuracy(pred, gold)
    pc = Counter(pred)
    gc = Counter(gold)
    pe = sum(pc[k] * gc[k] for k in set(pc) | set(gc)) / (n * n)
    if pe == 1.0:
        return 1.0
    return (po - pe) / (1 - pe)


def kendall_tau(a: Sequence[float], b: Sequence[float]) -> float:
    """Kendall's tau-a over paired rankings/scores."""
    if len(a) != len(b) or len(a) < 2:
        raise ValueError("need >=2 paired observations")
    n = len(a)
    concordant = discordant = 0
    for i in range(n):
        for j in range(i + 1, n):
            da, db = a[i] - a[j], b[i] - b[j]
            prod = da * db
            if prod > 0:
                concordant += 1
            elif prod < 0:
                discordant += 1
    pairs = n * (n - 1) / 2
    return (concordant - discordant) / pairs
