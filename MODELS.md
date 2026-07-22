# Models registry

Every model used anywhere in this pipeline is recorded here with its role and license.

## Hard rules (from the build plan)

1. **Frontier API models grade only.** Their outputs must never enter training data, reward
   signals, or rejection-sampling loops. They are used exclusively for offline evaluation and
   gold-set validation (`evals/calibrate.py`, spot checks).
2. **All training-loop generation and judging uses permissively licensed open-weights models**
   (MIT / Apache-2.0). Verify the license of the exact checkpoint before wiring it in, and
   update the table below.
3. **Generation and judgment use different model families** (separation of powers against
   self-preference bias).

## Registry

Decisions locked 2026-07-22: frontier judges = **Anthropic + OpenAI**;
open-weights teacher/judge = **hosted API (Together AI)**.

| Model | Role | License | Verified | Notes |
|---|---|---|---|---|
| `claude-opus-4-8` (Anthropic API) | Offline grader #1 (calibration, spot checks) | Proprietary API | n/a | Grading only. Outputs never enter training data. ToS: outputs may not be used to train competing models — grading-only usage is the compliance boundary. |
| `gpt-5.2` (OpenAI API) | Offline grader #2 (cross-judge validation) | Proprietary API | n/a | Different provider than grader #1 ✓. Confirm the current GPT id against the account before first run. Same grading-only boundary. |
| `deepseek-ai/DeepSeek-V3.1` (via Together AI) | Teacher (datagen generation) | **MIT** | **2026-07-22** | LICENSE file in the weights repo is the standard MIT License (Copyright 2023 DeepSeek); the V3.1/V3.2 line uses MIT for code **and** weights (older V3 had a separate model license — do not use that one). Source: https://huggingface.co/deepseek-ai/DeepSeek-V3.1/raw/main/LICENSE |
| `Qwen/Qwen3-235B-A22B-Instruct-2507` (via Together AI) | Open-weights judge (datagen filter gate, runtime-grader distillation teacher) | **Apache-2.0** | **2026-07-22** | Different family from the teacher (Qwen vs DeepSeek), per rule 3 ✓. Source: https://huggingface.co/Qwen/Qwen3-235B-A22B-Instruct-2507 |
| Qwen3 8B/14B-class | Student (SFT target) | Apache-2.0 — **verify exact checkpoint before use** | PENDING (Phase 3) | Known risk: student shares a family with the open-weights judge. Mitigated by frontier offline grading (different families) gating all headline numbers; revisit if scores diverge from frontier grades. Pick the exact checkpoint at Phase 3. |
| Distilled runtime grader (ours, from open-weights judge scores) | Harness best-of-N scorer + kitsch filter | MIT (ours) | n/a | Phase 4. Distillation teacher must be the open-weights judge, never a frontier model. |

License re-verification: re-check the two open-weights LICENSE files at the start
of each flywheel cycle (providers occasionally re-license or rename checkpoints).

## Free local proof-of-concept (2026-07-22, zero-cost run)

Local stand-ins for the production endpoints, same roles and same rules
(teacher/judge different families; frontier grades only). All run via ollama /
mlx-lm on Apple Silicon.

| Model | PoC role | License | Verified | Notes |
|---|---|---|---|---|
| `qwen3:8b` (ollama) | Teacher (datagen) | Apache-2.0 | 2026-07-22 | https://huggingface.co/Qwen/Qwen3-8B |
| `phi4:14b` (ollama) | Open-weights judge (gate) | MIT | 2026-07-22 | Microsoft Phi family ≠ Qwen ✓. https://huggingface.co/microsoft/phi-4 . Replaced mistral:7b (Apache-2.0, verified same day) which produced valid JSON but weak judgments in a calibration probe. |
| Qwen3 1.7B/4B (mlx) | Student (LoRA SFT) | Apache-2.0 | 2026-07-22 (family) | Trained locally with mlx-lm. |
| Claude (this session) | Frontier grader, offline only | n/a | n/a | Rubric validation + PoC spot-grading. Nothing it writes enters training data. |

## Role → phase map

- **Phase 1 (eval suite):** frontier graders #1 and #2, offline only. Imitation-tier negatives
  for the discrimination gold set are generated with an open-weights model (teacher family is
  fine here — these are eval negatives, not training data).
- **Phase 2 (datagen):** open-weights teacher generates; open-weights judge (different family)
  filters. Frontier models only spot-check the accepted set, offline.
- **Phase 3 (training):** student SFT on Phase 2 data only.
- **Phase 4 (harness):** runtime grader distilled from the open-weights judge.
- **Phase 5 (flywheel):** same constraints as Phases 2–3; provenance field enforced in CI.
