"""Build the discrimination gold set from the corpus + imitation slots.

Real items (genuine / spurious / paraphrase) come straight from the corpus and
are fully deterministic. Imitation items at three quality tiers require an
open-weights model; they are produced separately by
``evals/goldset/gen_imitations.py`` and merged here if present.

Run:  python -m evals.goldset.build_discrimination [--check]

Output: evals/goldset/discrimination.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from corpus import loader

HERE = Path(__file__).resolve().parent
OUT = HERE / "discrimination.jsonl"
IMITATIONS = HERE / "imitations.jsonl"

_WORKING = "Herakleitos project (working translation, MIT)"


def _best_translation(f: loader.Fragment) -> loader.Translation:
    public = [t for t in f.translations if t.translator != _WORKING]
    return (public or list(f.translations))[0]


def build_real_items() -> list[dict]:
    items: list[dict] = []

    for f in loader.genuine():
        t = _best_translation(f)
        txt = t.text.strip()
        if len(txt.split()) < 4:
            continue
        if txt.startswith("("):  # editorial gloss (e.g. B3), not a translation
            continue
        items.append(
            {
                "text": txt,
                "label": "genuine",
                "source": f"DK {f.dk_number} / {t.translator} {t.year}",
                "tier": None,
                "dk_number": f.dk_number,
            }
        )

    for f in loader.spurious():
        t = _best_translation(f)
        txt = t.text.strip()
        if len(txt.split()) < 4:
            continue
        items.append(
            {
                "text": txt,
                "label": "spurious",
                "source": f"DK {f.dk_number} (spurious tail)",
                "tier": None,
                "dk_number": f.dk_number,
            }
        )

    # Disputed fragments are held out as a separate diagnostic slice: they are
    # genuine-adjacent but flagged, and we do not want them polluting the clean
    # genuine-vs-spurious accuracy number. Label them "disputed".
    for f in loader.disputed():
        t = _best_translation(f)
        txt = t.text.strip()
        if len(txt.split()) < 4:
            continue
        items.append(
            {
                "text": txt,
                "label": "disputed",
                "source": f"DK {f.dk_number} (disputed)",
                "tier": None,
                "dk_number": f.dk_number,
            }
        )

    for p in loader.contrast():
        if p.category not in ("platonic", "stoic"):
            continue
        items.append(
            {
                "text": p.text.strip()[:600],
                "label": "paraphrase",
                "source": f"{p.author} / {p.source}",
                "tier": None,
                "dk_number": None,
            }
        )

    # Some DK fragments were translated by Burnet as one joined text (e.g.
    # B84a/B84b, B110/B111, B82/B83), yielding identical translation strings.
    # Keep the first occurrence and fold the duplicate DK numbers into its
    # source so the discrimination set has no verbatim duplicates.
    deduped: list[dict] = []
    by_text: dict[str, dict] = {}
    for it in items:
        key = " ".join(it["text"].lower().split())
        if key in by_text:
            other = by_text[key]
            if it["dk_number"] and it["dk_number"] not in other["source"]:
                other["source"] += f" (+{it['dk_number']})"
            continue
        by_text[key] = it
        deduped.append(it)
    return deduped


def assemble() -> list[dict]:
    items = build_real_items()
    if IMITATIONS.exists():
        for line in IMITATIONS.read_text(encoding="utf-8").splitlines():
            if line.strip():
                items.append(json.loads(line))
    for idx, it in enumerate(items, 1):
        it["id"] = f"disc-{idx:04d}"
    # stable key order
    order = ["id", "text", "label", "tier", "source", "dk_number"]
    return [{k: it.get(k) for k in order} for it in items]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)

    items = assemble()
    fresh = "".join(json.dumps(it, ensure_ascii=False) + "\n" for it in items)

    from collections import Counter

    counts = Counter(it["label"] for it in items)
    print(f"discrimination items: {len(items)} {dict(counts)}")

    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != fresh:
            print("STALE: discrimination.jsonl differs from a fresh build", file=sys.stderr)
            return 1
        print("check ok")
        return 0

    OUT.write_text(fresh, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
