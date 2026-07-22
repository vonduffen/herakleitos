"""Grading harness: per-dimension judge calls over gold-set items.

Absolute mode grades one response; pairwise mode grades two orderings and
averages (position-bias mitigation). All judge outputs are strict JSON.
"""

from __future__ import annotations

import json
import re
from typing import Any

from evals.judge import rubrics
from evals.judge.backends import Backend


def strip_thinking(raw: str) -> str:
    """Remove reasoning-mode blocks some open-weights models emit (e.g. Qwen3's
    <think>...</think>) so downstream parsing sees only the final answer."""
    return re.sub(r"<think>.*?</think>", "", raw, flags=re.S).strip()


def _parse_json(raw: str) -> dict[str, Any]:
    """Parse a judge reply, tolerating stray code fences and thinking blocks."""
    raw = strip_thinking(raw)
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw)
    m = re.search(r"\{.*\}", raw, flags=re.S)
    if not m:
        raise ValueError(f"no JSON object in judge reply: {raw[:200]!r}")
    return json.loads(m.group(0))


def classify_provenance(backend: Backend, text: str) -> dict[str, Any]:
    user = f"Text:\n{text}"
    return _parse_json(backend.complete(rubrics.SYSTEMS["discrimination"], user))


def score_structural(
    backend: Backend, prompt: str, checks: list[str], response: str
) -> dict[str, Any]:
    numbered = "\n".join(f"{i + 1}. {c}" for i, c in enumerate(checks))
    user = f"Task prompt:\n{prompt}\n\nBinary checks:\n{numbered}\n\nResponse:\n{response}"
    out = _parse_json(backend.complete(rubrics.SYSTEMS["structural_transfer"], user))
    got = out.get("checks", [])
    if len(got) != len(checks):
        raise ValueError(f"judge returned {len(got)} checks, expected {len(checks)}")
    return out


def score_anti_kitsch(backend: Backend, response: str) -> dict[str, Any]:
    return _parse_json(backend.complete(rubrics.SYSTEMS["anti_kitsch"], f"Text:\n{response}"))


def score_tension(backend: Backend, dialogue: list[dict[str, str]]) -> dict[str, Any]:
    lines = []
    a_idx = 0
    for turn in dialogue:
        if turn["role"] == "assistant":
            a_idx += 1
            lines.append(f"ASSISTANT (turn {a_idx}): {turn['text']}")
        else:
            lines.append(f"USER: {turn['text']}")
    user = "Dialogue:\n" + "\n".join(lines)
    return _parse_json(backend.complete(rubrics.SYSTEMS["tension_holding"], user))


def compare_compression(backend: Backend, insight: str, a: str, b: str) -> str:
    """Pairwise with position-bias mitigation: grade both orderings.

    Returns "A" or "B" (referring to the caller's ordering) if both orderings
    agree, else "tie".
    """

    def one(x: str, y: str) -> str:
        user = f"The shared insight:\n{insight}\n\nResponse A:\n{x}\n\nResponse B:\n{y}"
        return _parse_json(backend.complete(rubrics.SYSTEMS["compression"], user))["winner"]

    first = one(a, b)
    second = one(b, a)
    second_flipped = "A" if second == "B" else "B"
    if first == second_flipped:
        return first
    return "tie"


def check_consistency(backend: Backend, statement: str) -> dict[str, Any]:
    return _parse_json(
        backend.complete(rubrics.SYSTEMS["consistency"], f"Statement:\n{statement}")
    )


def composite(per_dimension: dict[str, float]) -> float:
    """Weighted composite over normalized [0,1] per-dimension scores."""
    total = 0.0
    for dim, weight in rubrics.WEIGHTS.items():
        if dim not in per_dimension:
            raise KeyError(f"missing dimension {dim}")
        v = per_dimension[dim]
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"{dim} score {v} not in [0,1]")
        total += weight * v
    return total
