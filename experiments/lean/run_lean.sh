#!/bin/zsh
# LEAN TIER — the gate ablation, end to end.
# Paid stages: seed expansion, generation, gating (Together). Training is LOCAL
# (mlx, $0). Frontier calibration runs only if both frontier keys are present.
# Idempotent: completed stages are skipped on re-run (checks output files).
set -e
cd "$(dirname "$0")/../.."
export OLLAMA_API_KEY=${OLLAMA_API_KEY:-local}
OUT=datagen/out/lean
mkdir -p "$OUT"

echo "=== [0/7] preflight (hard cap: \$200) ==="
uv run python -m experiments.lean.preflight --cap 200

echo "=== [1/7] seed expansion -> ~2,000 seeds ==="
[ -s "$OUT/seeds.jsonl" ] || uv run python -m datagen.expand_seeds \
    --backend teacher --target 2000 --out "$OUT/seeds.jsonl"

echo "=== [2/7] teacher generation: 2,000 seeds x k=4 = 8,000 candidates ==="
[ -s "$OUT/candidates.jsonl" ] || uv run python -m datagen.generate \
    --backend teacher --k 4 --seeds-file "$OUT/seeds.jsonl" \
    --out "$OUT/candidates.jsonl"

echo "=== [3/7] eval gate (Qwen3-235B, 3 rubric calls per candidate) ==="
[ -s "$OUT/accepted.jsonl" ] || uv run python -m datagen.filter \
    --in "$OUT/candidates.jsonl" --backend openweights_judge \
    --teacher-backend teacher --out "$OUT/accepted.jsonl"

echo "=== [4/7] ablation sets: arm A (filtered) vs arm B (unfiltered, size-matched) ==="
uv run python -m experiments.lean.make_ablation_sets \
    --candidates "$OUT/candidates.jsonl" --accepted "$OUT/accepted.jsonl" \
    --outdir training/lean

echo "=== [5/7] local LoRA training: 3 arms x 2 seeds (mlx, \$0) ==="
for arm in arm_A_filtered arm_B_unfiltered arm_R_rejects; do
  for s in 17 43; do
    ADIR="training/adapters/lean_${arm}_s${s}"
    [ -s "$ADIR/adapters.safetensors" ] || \
      /Users/m4/miniconda3/bin/mlx_lm lora --model mlx-community/Qwen3-1.7B-4bit \
        --train --data "training/lean/$arm" --iters 600 --batch-size 2 \
        --num-layers 12 --seed "$s" --adapter-path "$ADIR" \
        --steps-per-report 100 --steps-per-eval 200
  done
done

echo "=== [6/7] local eval of all arms (phi4 judge; frontier pass is separate) ==="
for arm in base arm_A_filtered_s17 arm_A_filtered_s43 arm_B_unfiltered_s17 arm_B_unfiltered_s43 arm_R_rejects_s17 arm_R_rejects_s43; do
  REP="$OUT/report_${arm}.json"
  [ -s "$REP" ] && continue
  pkill -f "mlx_lm server" 2>/dev/null || true; sleep 2
  if [ "$arm" = "base" ]; then
    /Users/m4/miniconda3/bin/mlx_lm server --model mlx-community/Qwen3-1.7B-4bit --port 8080 &
  else
    /Users/m4/miniconda3/bin/mlx_lm server --model mlx-community/Qwen3-1.7B-4bit \
      --adapter-path "training/adapters/lean_${arm}" --port 8080 &
  fi
  for i in $(seq 1 30); do curl -s http://localhost:8080/v1/models >/dev/null && break; sleep 3; done
  uv run python -m evals.report --candidate student_local --judge judge_local \
      --limit 12 --json --out "$REP" || echo "eval failed for $arm"
done
pkill -f "mlx_lm server" 2>/dev/null || true

echo "=== [7/7] summary ==="
uv run python - <<'EOF'
import json, glob
rows=[]
for p in sorted(glob.glob("datagen/out/lean/report_*.json")):
    d=json.load(open(p))
    rows.append((p.split("report_")[-1][:-5], d["generative_composite"], d["generative_dimensions"]))
print(f"{'arm':28s} {'composite':>9s}   tension")
for name,comp,dims in rows:
    print(f"{name:28s} {comp:9.3f}   {dims.get('tension_holding',float('nan')):.3f}")
EOF
echo "=== LEAN RUN DONE — frontier calibration next if keys present:"
echo "    uv run python -m evals.calibrate --backend frontier1 --compare frontier2"
