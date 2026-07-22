import pytest

from evals import decontaminate as dc

pytestmark = pytest.mark.smoke


def test_self_check_passes():
    assert dc.self_check() == 0


def test_contaminated_detects_verbatim_copy():
    gold = ["You cannot step into the same river twice, for fresh waters flow on."]
    train = [
        "Here is a thought: you cannot step into the same river twice, for fresh "
        "waters flow on. Discuss.",
        "An unrelated sentence about compilers and type systems entirely.",
    ]
    hits = dc.contaminated(train, gold, threshold=0.4)
    assert (0, 0) in hits
    assert all(t != 1 for t, _ in hits)


def test_overlap_ratio_bounds():
    assert dc.overlap_ratio("identical text here", "identical text here") == pytest.approx(1.0)
    assert dc.overlap_ratio("totally different alpha", "unrelated beta gamma phrase") < 0.2


def test_normalize_strips_punctuation_and_case():
    assert dc.normalize("The  WAY up, and DOWN!") == "the way up and down"
