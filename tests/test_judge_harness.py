"""End-to-end wiring test for the judge harness, fully offline.

An "oracle" mock backend inspects the system prompt to tell which dimension it's
being asked about, and inspects the user content to return the gold-correct
answer. This exercises judge.py, calibrate.py, and report.py without any network
call, and proves that a real backend only needs to match the JSON schemas.
"""

import json

import pytest

from evals import calibrate, report
from evals.goldset import loader
from evals.judge import judge
from evals.judge.backends import MockBackend

pytestmark = pytest.mark.smoke

# Build lookup tables from the gold set so the oracle can answer correctly.
_STRUCT = {it.strong: it for it in loader.structural()}
_STRUCT_K = {it.kitsch: it for it in loader.structural()}
_DISC = {it.text: it for it in loader.discrimination()}
_CONS = {it.statement: it for it in loader.consistency()}


def _oracle(system: str, user: str) -> str:
    if "classify its provenance" in system.lower() or "provenance" in system.lower():
        text = user.split("Text:\n", 1)[-1].strip()
        it = _DISC.get(text)
        label = it.label if it else "imitation"
        # gold maps disputed/spurious/paraphrase to non-genuine
        out_label = "genuine" if label == "genuine" else (
            "paraphrase" if label == "paraphrase" else "spurious"
        )
        return json.dumps({"label": out_label, "confidence": 0.9, "rationale": "x"})

    if "heraclitean structure" in system.lower() or "binary checks" in system.lower():
        resp = user.split("Response:\n", 1)[-1].strip()
        it = _STRUCT.get(resp) or _STRUCT_K.get(resp)
        n = len(it.checks) if it else 4
        strong = resp in _STRUCT
        checks = [strong] * n
        return json.dumps({"checks": checks, "score": 5 if strong else 1, "rationale": "x"})

    if "anti-kitsch detector" in system.lower():
        resp = user.split("Text:\n", 1)[-1].strip()
        if resp in _STRUCT_K:
            return json.dumps({"flags": ["oracle_register"], "score": 1, "rationale": "x"})
        return json.dumps({"flags": [], "score": 5, "rationale": "x"})

    if "multi-turn dialogue" in system.lower() or "holds a genuine" in system.lower():
        # detect the collapse track by matching assistant lines
        for it in loader.tension():
            if it.collapse_track[0] in user and it.collapse_track[-1] in user:
                return json.dumps(
                    {
                        "collapse_turn": it.collapse_turn,
                        "collapse_mode": it.collapse_mode,
                        "score": 1,
                        "rationale": "x",
                    }
                )
        return json.dumps(
            {"collapse_turn": None, "collapse_mode": "none", "score": 5, "rationale": "x"}
        )

    if "compression" in system.lower():
        # "Response A" then "Response B" - prefer the shorter (compressed) one
        a = user.split("Response A:\n", 1)[-1].split("Response B:")[0].strip()
        b = user.split("Response B:\n", 1)[-1].strip()
        return json.dumps({"winner": "A" if len(a) < len(b) else "B", "rationale": "x"})

    if "core commitments" in system.lower():
        stmt = user.split("Statement:\n", 1)[-1].strip()
        it = _CONS.get(stmt)
        label = it.label if it else "compatible"
        return json.dumps(
            {"label": label, "violated_commitment": None, "rationale": "x"}
        )

    return json.dumps({"score": 3, "rationale": "fallback"})


@pytest.fixture
def oracle() -> MockBackend:
    return MockBackend(name="oracle", responder=_oracle)


def test_discrimination_oracle_perfect(oracle):
    res = calibrate.calibrate_discrimination(oracle, limit=None)
    assert res.metrics["acc_genuine_vs_spurious"] == pytest.approx(1.0)


def test_structural_oracle(oracle):
    res, scores = calibrate.calibrate_structural(oracle, limit=8)
    assert res.metrics["strong_beats_kitsch_rate"] == pytest.approx(1.0)
    assert res.metrics["mean_strong_score"] > res.metrics["mean_kitsch_score"]


def test_anti_kitsch_oracle(oracle):
    res = calibrate.calibrate_anti_kitsch(oracle, limit=8)
    assert res.metrics["kitsch_flag_recall"] == pytest.approx(1.0)
    assert res.metrics["strong_clean_rate"] == pytest.approx(1.0)


def test_tension_oracle_localizes_collapse(oracle):
    res = calibrate.calibrate_tension(oracle, limit=None)
    assert res.metrics["hold_not_flagged_rate"] == pytest.approx(1.0)
    assert res.metrics["collapse_localized_rate"] == pytest.approx(1.0)


def test_compression_oracle_prefers_compressed(oracle):
    res = calibrate.calibrate_compression(oracle, limit=None)
    assert res.metrics["tripwire_prefers_compressed"] == pytest.approx(1.0)


def test_consistency_oracle_perfect(oracle):
    res = calibrate.calibrate_consistency(oracle, limit=None)
    assert res.metrics["accuracy"] == pytest.approx(1.0)


def test_position_bias_mitigation_ties_on_disagreement():
    # A backend that always says "A wins" should yield "tie" after both orderings.
    always_a = MockBackend(responder=lambda s, u: json.dumps({"winner": "A"}))
    assert judge.compare_compression(always_a, "insight", "x", "y") == "tie"


def test_report_card_runs_offline(oracle):
    result = report.score_candidate(oracle, oracle, limit=3)
    assert 0.0 <= result["composite"] <= 1.0
    assert set(result["per_dimension"]) == set(
        ["discrimination", "structural_transfer", "anti_kitsch",
         "tension_holding", "compression", "corpus_consistency"]
    )


def test_composite_weighting():
    per_dim = dict.fromkeys(
        ["discrimination", "structural_transfer", "anti_kitsch",
         "tension_holding", "compression", "corpus_consistency"],
        1.0,
    )
    assert judge.composite(per_dim) == pytest.approx(1.0)
    per_dim["anti_kitsch"] = 0.0
    assert judge.composite(per_dim) == pytest.approx(0.85)
