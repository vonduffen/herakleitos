# Herakleitos

A pipeline for training a small model that reasons like Heraclitus — structurally
(unity of opposites, process over substance, tension held without premature
resolution), not stylistically (no river quotes, no oracle cosplay).

The eval suite is built first and gates everything downstream.

**Pipeline:** open-weights teacher generates candidate data → frontier-graded eval
gate filters it → distilled student delivers through a harness → student
trajectories loop back as new eval cases.

See `MODELS.md` for the model registry and the hard licensing/role constraints
(frontier APIs grade only; training-loop generation and judging use permissively
licensed open-weights models from different families).

## Layout

```
MODELS.md            # every model, role, license, ToS notes
corpus/              # DK fragments, translations, contrast corpus, loader
  sources/raw/       # committed raw downloads (Wikisource, Gutenberg, IA)
  build_corpus.py    # deterministic raw -> data build (python -m corpus.build_corpus)
  data/              # fragments.jsonl, contrast.jsonl (committed, rebuilt in CI)
  loader.py          # typed accessors
evals/
  goldset/           # calibration data (never enters training)  [Phase 1]
  judge/             # rubric prompts, judge backends, bias mitigations  [Phase 1]
datagen/             # seeds, generation, eval-gated filtering  [Phase 2]
training/            # SFT configs, runs, checkpoints metadata  [Phase 3]
harness/             # retrieval, dialectic, best-of-N, kitsch filter  [Phase 4]
flywheel/            # failure mining, eval rotation, provenance  [Phase 5]
tests/
```

## Setup

```
uv sync
uv run pytest
```

## Corpus status (Phase 0)

- 148 DK 22 B fragments (121 genuine / 14 disputed / 13 spurious), Greek text
  from the Diels-Kranz edition (el.wikisource), with Burnet 1920 and
  Patrick 1889 public-domain translations aligned via Bywater concordance.
- The DK spurious tail (B126b–B139) and a few gaps are hand-transcribed and
  flagged `needs_verification` in their notes: **verify against a critical
  edition before they are used in gold-set discrimination items.**
- Contrast corpus: Parmenides (DK 28 B, Greek + Burnet passages), Platonic
  discussions of Heraclitus (Jowett), Stoic paraphrase (Long's Marcus Aurelius).

All original work in this repository is MIT-licensed. Ancient texts and the
1889/1898/1920 translations are public domain.
