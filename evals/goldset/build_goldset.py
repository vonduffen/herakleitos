"""Assemble all authored gold-set slices into committed JSONL files.

Sources:
  - items_structural.py  (hand-authored, 20)
  - _batch_[A-D].json    (authored via subagent, schema-validated here, 40)
  - items_tension.py, items_compression.py, items_consistency.py

Outputs (committed, decontamination-checked against training data downstream):
  structural.jsonl, tension.jsonl, compression.jsonl, consistency.jsonl
  discrimination.jsonl is built separately (build_discrimination.py).

Run:  python -m evals.goldset.build_goldset [--check]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from evals.goldset import items_compression, items_consistency, items_structural, items_tension

HERE = Path(__file__).resolve().parent

_STRUCT_KEYS = ("id", "domain", "task_type", "prompt", "checks", "strong", "kitsch")
_MOVES = (
    "identity-through-change",
    "unity-of-opposites",
    "process-primacy",
    "measure-and-exchange",
    "tension-as-structure",
    "perspectival-opposition",
)


def _validate_structural(it: dict) -> None:
    missing = set(_STRUCT_KEYS) - set(it)
    if missing:
        raise ValueError(f"{it.get('id')}: missing keys {missing}")
    n = len(it["checks"])
    if not 3 <= n <= 5:
        raise ValueError(f"{it['id']}: {n} checks (need 3-5)")
    # Every item must carry at least one check that guards against the
    # being-over-becoming trap: a check that penalizes reasoning in static
    # categories or positing an unchanging substrate/essence as the real answer.
    # It may be phrased as "avoids...", "does not...", "resists...", "rather
    # than a static X", "non-mystical", etc.
    guard_markers = (
        "avoid",
        "does not",
        "does-not",
        "resist",
        "rather than",
        "not a ",
        "not of ",
        "unchanging",
        "static",
        "non-mystical",
        "no cosmic",
        "being-over-becoming",
        "being-trap",
    )
    if not any(any(g in c.lower() for g in guard_markers) for c in it["checks"]):
        raise ValueError(f"{it['id']}: no being-over-becoming guard check")
    if not it["strong"].strip() or not it["kitsch"].strip():
        raise ValueError(f"{it['id']}: empty exemplar")


def load_structural() -> list[dict]:
    items = [dict(it) for it in items_structural.ITEMS]
    for path in sorted(HERE.glob("structural_batch_*.json")):
        items.extend(json.loads(path.read_text(encoding="utf-8")))
    for it in items:
        it.setdefault("checks", [])
        _validate_structural(it)
    ids = [it["id"] for it in items]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate structural ids")
    return [{k: it[k] for k in _STRUCT_KEYS} for it in items]


_TENSION_KEYS = (
    "id",
    "topic",
    "user_turns",
    "hold_track",
    "collapse_track",
    "collapse_turn",
    "collapse_mode",
)


def load_tension() -> list[dict]:
    items = [{k: it[k] for k in _TENSION_KEYS} for it in items_tension.ITEMS]
    batch = HERE / "tension_batch.json"
    if batch.exists():
        items.extend(
            {k: it[k] for k in _TENSION_KEYS}
            for it in json.loads(batch.read_text(encoding="utf-8"))
        )
    for it in items:
        n = len(it["user_turns"])
        if not (len(it["hold_track"]) == len(it["collapse_track"]) == n):
            raise ValueError(f"{it['id']}: track length mismatch")
        if not 1 <= it["collapse_turn"] <= n:
            raise ValueError(f"{it['id']}: collapse_turn out of range")
        if it["collapse_mode"] not in ("one_side", "vague", "evade"):
            raise ValueError(f"{it['id']}: bad collapse_mode")
    ids = [it["id"] for it in items]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate tension ids")
    return items


def _dump(records: list[dict]) -> str:
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records)


SLICES = {
    "structural.jsonl": load_structural,
    "tension.jsonl": load_tension,
    "compression.jsonl": lambda: list(items_compression.ITEMS),
    "consistency.jsonl": lambda: list(items_consistency.ITEMS),
}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)

    stale = False
    for name, builder in SLICES.items():
        records = builder()
        fresh = _dump(records)
        print(f"{name}: {len(records)} items")
        if args.check:
            path = HERE / name
            if not path.exists() or path.read_text(encoding="utf-8") != fresh:
                print(f"STALE: {name}", file=sys.stderr)
                stale = True
        else:
            (HERE / name).write_text(fresh, encoding="utf-8")

    if args.check:
        if stale:
            return 1
        print("check ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
