"""Typed accessors for the eval gold set.

All slices are committed JSONL, built by build_goldset.py / build_discrimination.py.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _read(name: str) -> list[dict]:
    path = HERE / name
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


@dataclass(frozen=True)
class DiscriminationItem:
    id: str
    text: str
    label: str  # genuine | spurious | disputed | paraphrase | imitation
    tier: str | None  # imitation quality tier: low|medium|high, else None
    source: str
    dk_number: str | None


@dataclass(frozen=True)
class StructuralItem:
    id: str
    domain: str
    task_type: str
    prompt: str
    checks: tuple[str, ...]
    strong: str
    kitsch: str


@dataclass(frozen=True)
class TensionItem:
    id: str
    topic: str
    user_turns: tuple[str, ...]
    hold_track: tuple[str, ...]
    collapse_track: tuple[str, ...]
    collapse_turn: int
    collapse_mode: str

    def as_dialogue(self, track: str) -> list[dict[str, str]]:
        """Interleave user turns with the chosen assistant track."""
        replies = self.hold_track if track == "hold" else self.collapse_track
        out: list[dict[str, str]] = []
        for u, a in zip(self.user_turns, replies, strict=True):
            out.append({"role": "user", "text": u})
            out.append({"role": "assistant", "text": a})
        return out


@dataclass(frozen=True)
class CompressionItem:
    id: str
    insight: str
    long: str
    short: str
    correct: str  # "short" | "long"
    kind: str


@dataclass(frozen=True)
class ConsistencyItem:
    id: str
    statement: str
    label: str  # compatible | incompatible
    violated: int | None


@lru_cache(maxsize=1)
def discrimination() -> tuple[DiscriminationItem, ...]:
    return tuple(DiscriminationItem(**r) for r in _read("discrimination.jsonl"))


@lru_cache(maxsize=1)
def structural() -> tuple[StructuralItem, ...]:
    return tuple(
        StructuralItem(
            id=r["id"],
            domain=r["domain"],
            task_type=r["task_type"],
            prompt=r["prompt"],
            checks=tuple(r["checks"]),
            strong=r["strong"],
            kitsch=r["kitsch"],
        )
        for r in _read("structural.jsonl")
    )


@lru_cache(maxsize=1)
def tension() -> tuple[TensionItem, ...]:
    return tuple(
        TensionItem(
            id=r["id"],
            topic=r["topic"],
            user_turns=tuple(r["user_turns"]),
            hold_track=tuple(r["hold_track"]),
            collapse_track=tuple(r["collapse_track"]),
            collapse_turn=r["collapse_turn"],
            collapse_mode=r["collapse_mode"],
        )
        for r in _read("tension.jsonl")
    )


@lru_cache(maxsize=1)
def compression() -> tuple[CompressionItem, ...]:
    return tuple(CompressionItem(**r) for r in _read("compression.jsonl"))


@lru_cache(maxsize=1)
def consistency() -> tuple[ConsistencyItem, ...]:
    return tuple(ConsistencyItem(**r) for r in _read("consistency.jsonl"))


def all_gold_text() -> list[str]:
    """Every human-readable string in the gold set.

    Used by the decontamination check (Phase 2): no gold-set text may appear in
    training data.
    """
    out: list[str] = []
    for d in discrimination():
        out.append(d.text)
    for s in structural():
        out += [s.prompt, s.strong, s.kitsch, *s.checks]
    for t in tension():
        out += [*t.user_turns, *t.hold_track, *t.collapse_track]
    for c in compression():
        out += [c.insight, c.long, c.short]
    for c2 in consistency():
        out.append(c2.statement)
    return out
