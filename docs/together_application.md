# Together AI Research Credits — application kit

Paste-ready answers for https://www.together.ai/research-credits-program-request
(fields vary; every commonly asked item is covered). Fill the [bracketed] personal
details before submitting.

---

## Applicant

- **Name:** [your name]
- **Email:** alexandre.dufourrichard@gmail.com
- **Affiliation:** Independent researcher
- **Links:** https://github.com/vonduffen/herakleitos , [dossier/artifact share link, optional]

## Project title

**HERAKLEITOS: Eval-first distillation of a reasoning style, with an
adversarial anti-pastiche gate**

## One-sentence summary

We distill a *style of reasoning* (Heraclitean: process-over-substance, unity
of opposites, tension held under pressure) into small open-weights models using
a six-dimension adversarial eval as a data gate, and test the claim that the
gate — not the distillation — is what transmits the style.

## Abstract (~150 words)

Style transfer in LLMs is usually evaluated by vibes, which rewards pastiche.
We built the evaluation first: a six-dimension rubric suite (discrimination
against forgeries, structural transfer to novel domains, anti-kitsch penalty,
adversarial tension-holding, compression, corpus consistency) calibrated on a
384-item gold set built from the Diels-Kranz fragments of Heraclitus — chosen
as a hard test persona because 2,500 years of imitations provide free
adversarial data. The pipeline is fully open-weights: a DeepSeek-family teacher
generates candidates, a Qwen-family judge gates them through the rubrics
(separation of powers against self-preference bias), and a small student is
fine-tuned on survivors. A zero-cost local proof of concept (Qwen3-8B teacher,
Phi-4 judge, Qwen3-1.7B student) already shows the hardest dimension —
tension-holding — scaling monotonically with gate-filtered data (0.50 → 0.63 →
0.78). Credits fund the production-scale run and the ablation that makes the
claim rigorous.

## What we will do with the credits (research plan)

1. **Gate ablation (the core experiment).** Train matched students on
   (a) gate-filtered data, (b) unfiltered data from the same teacher,
   (c) prompt-only baseline. If (a) > (b) cleanly across seeds, rubric-gated
   filtering — not raw distillation — is what transmits reasoning style.
2. **Production datagen:** 2,000 seeds x k=4 through `deepseek-ai/DeepSeek-V3.1`
   (teacher), gated by `Qwen/Qwen3-235B-A22B-Instruct-2507` (judge) running our
   six rubrics. Different families by design.
3. **Imitation-tier regeneration** for the discrimination benchmark (three
   difficulty tiers of style-faking negatives).
4. **Runtime-grader distillation data:** judge scores over candidate pools, to
   train the small best-of-N grader for the serving harness (the harness-gap
   metric across generations is the follow-on study).

## Models requested

- `deepseek-ai/DeepSeek-V3.1` (teacher — MIT)
- `Qwen/Qwen3-235B-A22B-Instruct-2507` (judge — Apache-2.0)
- Together fine-tuning service for 7-8B students (ablation arms), if credits
  permit; otherwise students train locally on Apple Silicon.

## Budget estimate

| Item | Est. cost |
|---|---|
| Production datagen: 8,000 teacher generations | ~$15 |
| Judge gate: ~24,000 rubric calls | ~$10 |
| Imitation tiers + runtime-grader scoring data | ~$15 |
| Ablation arms: 3 conditions x 3 seeds datagen variants | ~$60 |
| Fine-tuning jobs (3x3 small students) via Together FT | ~$150-250 |
| Headroom for retries, flywheel round 2 | remainder |
| **Total request** | **$500** |

## Timeline

- Weeks 1-2: production datagen + gate; ablation datasets frozen.
- Weeks 3-4: training runs, eval passes (frontier calibration funded
  separately), general-capability regression checks.
- Weeks 5-6: analysis, benchmark release, public write-up.

## What already exists (evidence of momentum)

- Committed monorepo: corpus (148 DK fragments, Greek + two public-domain
  translations, full provenance), 384-item gold set, six-dimension judge
  harness with position-bias mitigation and length-blinding, eval-gated
  datagen, CI with determinism + decontamination guards, 28 tests green.
- Zero-cost end-to-end PoC on a MacBook: 486 candidates, 79% gate acceptance
  in both rounds, LoRA students, composite 0.805 -> 0.853 -> 0.877 with
  tension-holding staircasing 0.500 -> 0.625 -> 0.781 as filtered data tripled.
- Config already points at Together serverless endpoints; the run starts the
  day credits land.

## Dissemination / acknowledgment

All original work is MIT-licensed and public: the eval suite and gold set
released as a benchmark, code open-sourced, results in a public write-up.
Together AI will be acknowledged in the repository, the benchmark card, and
any publication or post resulting from the work.

## Why Together

The project's design constraint is that frontier APIs may only *grade* —
all generation and judging in the training loop must run on permissively
licensed open-weights models. Together serves the exact checkpoints our
licensing audit cleared (DeepSeek-V3.1, MIT; Qwen3-235B, Apache-2.0) behind
one OpenAI-compatible API, which our harness already targets.
