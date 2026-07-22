#!/bin/zsh
# PoC round 2: full local pipeline at 180-seed scale. Zero API cost.
# generate (k=2, qwen3:8b) -> filter (phi4:14b gate) -> SFT data -> LoRA train.
set -e
cd "$(dirname "$0")/.."
export OLLAMA_API_KEY=local

echo "=== [1/4] generate: 180 seeds x k=2 ==="
uv run python -m datagen.generate --backend teacher_local --k 2 \
    --out datagen/out/candidates_r2.jsonl

echo "=== [2/4] filter: phi4 eval gate ==="
uv run python -m datagen.filter --in datagen/out/candidates_r2.jsonl \
    --backend judge_local --out datagen/out/accepted_r2.jsonl

echo "=== [3/4] prepare SFT data ==="
uv run python -m training.prepare_sft --in datagen/out/accepted_r2.jsonl \
    --outdir training/data_r2

echo "=== [4/4] LoRA train (round 2 adapter) ==="
/Users/m4/miniconda3/bin/mlx_lm lora --model mlx-community/Qwen3-1.7B-4bit \
    --train --data training/data_r2 --iters 400 --batch-size 2 --num-layers 12 \
    --adapter-path training/adapters/poc2 --steps-per-report 50 --steps-per-eval 100

echo "=== POC2 CHAIN DONE ==="
