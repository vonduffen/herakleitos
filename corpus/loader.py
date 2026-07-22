"""Typed accessors for the Herakleitos corpus.

Data files are built by ``python -m corpus.build_corpus`` from committed raw
sources and are themselves committed; loading never touches the network.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Literal

DATA = Path(__file__).resolve().parent / "data"

Authenticity = Literal["genuine", "disputed", "spurious"]
ContrastCategory = Literal["parmenides", "platonic", "stoic"]


@dataclass(frozen=True)
class Translation:
    translator: str
    year: int
    source: str
    text: str


@dataclass(frozen=True)
class Fragment:
    dk_number: str
    greek: str
    translations: tuple[Translation, ...]
    authenticity: Authenticity
    source_author: str
    bywater_number: int | None
    notes: str

    @property
    def needs_verification(self) -> bool:
        return "needs_verification" in self.notes


@dataclass(frozen=True)
class ContrastPassage:
    id: str
    category: ContrastCategory
    language: str
    text: str
    author: str
    source: str
    notes: str = field(default="")


def _read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


@lru_cache(maxsize=1)
def fragments() -> tuple[Fragment, ...]:
    return tuple(
        Fragment(
            dk_number=r["dk_number"],
            greek=r["greek"],
            translations=tuple(Translation(**t) for t in r["translations"]),
            authenticity=r["authenticity"],
            source_author=r["source_author"],
            bywater_number=r["bywater_number"],
            notes=r["notes"],
        )
        for r in _read_jsonl(DATA / "fragments.jsonl")
    )


def by_dk(dk_number: str) -> Fragment:
    for f in fragments():
        if f.dk_number == dk_number:
            return f
    raise KeyError(dk_number)


def genuine() -> tuple[Fragment, ...]:
    return tuple(f for f in fragments() if f.authenticity == "genuine")


def disputed() -> tuple[Fragment, ...]:
    return tuple(f for f in fragments() if f.authenticity == "disputed")


def spurious() -> tuple[Fragment, ...]:
    return tuple(f for f in fragments() if f.authenticity == "spurious")


@lru_cache(maxsize=1)
def _all_contrast() -> tuple[ContrastPassage, ...]:
    return tuple(ContrastPassage(**r) for r in _read_jsonl(DATA / "contrast.jsonl"))


def contrast(category: ContrastCategory | None = None) -> tuple[ContrastPassage, ...]:
    passages = _all_contrast()
    if category is None:
        return passages
    return tuple(p for p in passages if p.category == category)
