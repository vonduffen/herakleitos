# Eval suite (Phase 1)

The eval suite is the core asset and gates everything downstream. It scores six
dimensions, each a **separate** rubric-anchored judge call (never one holistic
score). Weights: discrimination 0.25, structural transfer 0.25, anti-kitsch
0.15, tension holding 0.15, compression 0.10, corpus consistency 0.10.

## Layout

- `goldset/` — calibration data (**never enters training**; guarded by
  `evals/decontaminate.py`).
  - `discrimination.jsonl` (built from the corpus by `build_discrimination.py`)
  - `structural.jsonl`, `tension.jsonl`, `compression.jsonl`,
    `consistency.jsonl` (built by `build_goldset.py` from the `items_*.py`
    modules and the `structural_batch_*.json` / `tension_batch.json` sources)
  - `gen_imitations.py` — generates the three imitation tiers for the
    discrimination set (needs an **open-weights** endpoint; these are eval
    negatives, not training data).
- `judge/` — grading harness.
  - `rubrics.py` — per-dimension system prompts. Length-blinded; anti-kitsch
    clauses embedded in every dimension that could reward pastiche.
  - `backends.py` — pluggable OpenAI-/Anthropic-compatible backends + a
    schema-aware `MockBackend` for offline smoke. Config in `judge/config.toml`.
  - `judge.py` — per-dimension calls; pairwise compression with position-bias
    mitigation (grade both orderings).
  - `metrics.py` — accuracy, Cohen's kappa, Kendall's tau (stdlib only).
- `calibrate.py` — run a judge over the gold set; report per-dimension
  agreement + cross-judge Kendall tau between two frontier judges.
- `report.py` — score any candidate model endpoint; per-dimension + composite
  report card. Candidate and judge must be different families.
- `decontaminate.py` — reusable gold-set/training overlap check (shingle-based)
  + a CI self-check.

## Running (offline smoke, no endpoint)

```bash
uv run python -m evals.goldset.build_goldset          # rebuild gold set
uv run python -m evals.calibrate --backend mock --limit 5
uv run python -m evals.report --candidate mock --judge mock --limit 3
```

## Running for real (Phase 1 acceptance)

1. Set the two frontier judges and the open-weights endpoints in
   `judge/config.toml` (see the open decisions in the build plan) and export the
   API keys named there.
2. Generate the imitation tiers:
   `uv run python -m evals.goldset.gen_imitations --backend openweights_judge --n 60`
   then rebuild the discrimination set.
3. Calibrate each frontier judge and the cross-judge correlation:
   `uv run python -m evals.calibrate --backend frontier1 --compare frontier2`

## Phase 1 acceptance criteria (status)

| Criterion | Target | Status |
|---|---|---|
| Gold-set built, schema-validated, decontaminated | — | **done** (offline, CI-guarded) |
| Judge harness + metrics + bias mitigations | — | **done** (wired, offline-smoke-tested) |
| Discrimination items | ≥150 | 148 real; ≥150 after imitation tiers (endpoint) |
| Structural-transfer items | ≥60 | **60** |
| Tension dialogues | ≥40 | **40** (20 items × hold/collapse tracks) |
| Compression pairs | paired | **20** (15 tripwire + 5 distractors) |
| Consistency probes | ≥30 | **32** |
| Judge ≥90% genuine-vs-spurious, ≥80% vs imitation | acceptance | **pending frontier endpoint** |
| Compression tripwire: judge prefers compressed ≥80% | acceptance | **pending frontier endpoint** |
| Cross-judge ranking correlation ≥0.8 | acceptance | **pending two frontier endpoints** |
| Anti-kitsch flags ≥90% of kitsch exemplars | acceptance | **pending frontier endpoint** |

The four judge-performance criteria are the gate to Phase 2 and require the
frontier-endpoint decisions. Everything they depend on (data + harness) is built
and verified offline.
