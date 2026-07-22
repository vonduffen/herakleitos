# Free local PoC — results (2026-07-22)

Full pipeline exercised end-to-end at zero cost on an M4 Pro (24 GB):

    teacher qwen3:8b (Apache-2.0, ollama)
      -> 126 candidates over 42 seeds (7 domains x 4 task types)
    judge phi4:14b (MIT, ollama; family-separated from teacher; replaced
      mistral:7b after a calibration probe showed weak judgments)
      -> eval gate: 100/126 accepted (79%)
         rejections: 12 consistency, 11 structural, 3 too-short, 0 kitsch,
         0 gold-set contamination, 0 near-dups
    student mlx-community/Qwen3-1.7B-4bit + LoRA (mlx_lm, 240 iters, ~5 min)
      -> train loss 2.29 -> 0.31, val ~0.92
    eval evals/report.py, --limit 8, judge_local (phi4)

| dimension           | base  | tuned | delta  |
|---------------------|-------|-------|--------|
| structural_transfer | 0.844 | 0.844 | +0.000 |
| anti_kitsch         | 1.000 | 1.000 | +0.000 |
| tension_holding     | 0.500 | 0.625 | +0.125 |
| corpus_consistency  | 0.875 | 1.000 | +0.125 |
| **composite**       | 0.805 | 0.853 | +0.048 |

Caveats (honest scale): n=8 per slice, one seed, no CIs — directional only.
Base model scores high already (instruction-following + a strong system prompt),
so ceiling effects compress the visible delta; gains landed exactly in the two
dimensions with headroom. Frontier spot-grade (Claude, offline): tuned outputs
structurally correct, zero kitsch, register wordier/more abstract than gold
"strong" exemplars; local judge slightly lenient but directionally aligned.

Robustness fixes the PoC forced into the harness (kept for production):
- strip_thinking() for reasoning-mode models (Qwen3 <think> blocks)
- //-comment-tolerant JSON parsing (Phi-4 annotates its JSON)
- retry-with-temperature-nudge on unparseable judge replies
