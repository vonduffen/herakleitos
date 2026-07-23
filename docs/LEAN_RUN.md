# Lean tier runbook — the gate ablation

One command once keys exist. Budget: ~$16 API (Together) + ~$45 frontier
calibration (optional, runs only if keys present). Training is local ($0).
Hard cap enforced by preflight: $200.

## What only the human can do (once, ~10 minutes)

1. **Together** — create an account at api.together.ai, add a payment method
   or redeem credits, create an API key. Then:
   `export TOGETHER_API_KEY=...`
2. **(Optional now, needed for Phase 1 closure)** Anthropic + OpenAI API keys
   with a small credit balance ($25 each is ample):
   `export ANTHROPIC_API_KEY=...  OPENAI_API_KEY=...`
   Without these the run completes and skips frontier calibration.

Put them in the shell (or a `.env` you source) — never in any committed file.

## Run

```bash
./experiments/lean/run_lean.sh
```

Idempotent — re-run after any interruption; completed stages are skipped.

Stages: preflight (keys + live check + cost cap) → seed expansion to ~2,000
(teacher, deduped + gold-set decontaminated) → 8,000 candidates (k=4) →
eval gate (3 rubric calls each, Qwen3-235B) → **three ablation arms**:

| Arm | Data | Question it answers |
|---|---|---|
| A filtered | gate-accepted | the pipeline's claim |
| B unfiltered | size-matched random sample of all candidates | does the gate beat raw distillation? |
| R rejects | gate-rejected only | negative control — is the gate measuring anything? |

→ 6 local LoRA runs (3 arms × 2 seeds, mlx) → local eval of all arms + base
→ summary table. Prediction if the thesis holds: **R < B < A**, with B close
to A when acceptance is high (the rejects arm is the sharp control).

## Then (frontier, if keys present)

```bash
uv run python -m evals.calibrate --backend frontier1 --compare frontier2
```

This produces the four Phase 1 acceptance numbers (discrimination ≥90%,
imitation ≥80%, compression tripwire ≥80%, cross-judge τ ≥0.8, anti-kitsch
≥90%). If any fail, fix rubric wording before believing the ablation.

## Cost tripwires

- Preflight aborts if the estimate (with 25% contingency) exceeds `--cap 200`.
- All stages write incrementally; killing the run loses nothing.
- The Together dashboard shows live spend; the whole API bill should land
  around $16. If it's tracking materially above the estimate, stop and check
  token sizes in `experiments/lean/preflight.py`.
