"""Phase 0 acceptance tests for the corpus (see build plan)."""

import pytest

from corpus import loader

pytestmark = pytest.mark.smoke


def test_fragment_counts():
    assert len(loader.genuine()) >= 120
    assert len(loader.disputed()) + len(loader.spurious()) >= 20


def test_no_empty_fields():
    for f in loader.fragments():
        assert f.dk_number.startswith("B"), f.dk_number
        assert f.greek.strip(), f"empty greek: {f.dk_number}"
        assert f.translations, f"no translations: {f.dk_number}"
        for t in f.translations:
            assert t.text.strip(), f"empty translation: {f.dk_number}"
            assert t.translator.strip()
        assert f.authenticity in ("genuine", "disputed", "spurious")


def test_dk_numbers_unique():
    nums = [f.dk_number for f in loader.fragments()]
    assert len(nums) == len(set(nums))


def test_curated_transcriptions_are_flagged():
    # Everything in the DK spurious tail was hand-transcribed and must carry
    # the needs_verification flag until checked against a critical edition.
    for f in loader.spurious():
        assert f.needs_verification, f.dk_number


def test_known_fragments_present():
    river = loader.by_dk("B12")
    assert "ποταμ" in river.greek
    assert river.authenticity == "genuine"
    logos = loader.by_dk("B1")
    assert "λόγου" in logos.greek
    assert any("river" in t.text.lower() for t in river.translations)


def test_contrast_corpus_loaded():
    assert len(loader.contrast("parmenides")) >= 15
    assert len(loader.contrast("platonic")) >= 3
    assert len(loader.contrast("stoic")) >= 3
    for p in loader.contrast():
        assert p.text.strip()
        assert p.category in ("parmenides", "platonic", "stoic")


def test_translations_coverage():
    # A healthy majority of fragments should carry two independent
    # public-domain translations.
    two = sum(1 for f in loader.fragments() if len(f.translations) >= 2)
    assert two >= 100
