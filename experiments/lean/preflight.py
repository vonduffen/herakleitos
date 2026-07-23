"""Preflight for the Lean run: keys present, endpoints answer, cost within cap.

Refuses to green-light if any required key is missing or the estimate exceeds
--cap. Run this before run_lean.sh; the runner calls it automatically.

  python -m experiments.lean.preflight --cap 200
"""

from __future__ import annotations

import argparse
import os
import sys
import tomllib

from evals.judge.backends import CONFIG_PATH, load_backend

# (backend, needed_for, required)
CHECKS = [
    ("teacher", "seed expansion + candidate generation (Together)", True),
    ("openweights_judge", "eval gate (Together)", True),
    ("frontier1", "calibration judge #1 (Anthropic)", False),
    ("frontier2", "calibration judge #2 (OpenAI)", False),
]

# Lean-tier volumes (mirrors docs/herakleitos_budget.xlsx, Lean column)
EST = {
    "seed expansion (~120 calls)": 120 * (900 * 0.60 + 900 * 1.70) / 1e6,
    "teacher generation (8k)": 8000 * (300 * 0.60 + 400 * 1.70) / 1e6,
    "gate judging (24k calls)": 24000 * (700 * 0.20 + 150 * 0.60) / 1e6,
    "frontier calibration (1.2k calls)": 1200 * (1500 * 12.0 + 200 * 50.0) / 1e6,
    "frontier report cards (400 calls)": 400 * (1500 * 12.0 + 200 * 50.0) / 1e6,
}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cap", type=float, default=200.0, help="hard budget cap in USD")
    ap.add_argument("--skip-live-check", action="store_true", help="keys only, no test calls")
    args = ap.parse_args(argv)

    cfg = tomllib.loads(CONFIG_PATH.read_text())["backends"]
    ok = True
    print("== key check ==")
    for name, purpose, required in CHECKS:
        env = cfg[name].get("api_key_env", "")
        present = bool(os.environ.get(env, ""))
        mark = "ok " if present else ("MISSING" if required else "absent (calibration deferred)")
        print(f"  {name:18s} {env:26s} {mark}   <- {purpose}")
        if required and not present:
            ok = False

    if ok and not args.skip_live_check:
        print("== live check (1 tiny call per required backend) ==")
        for name in ("teacher", "openweights_judge"):
            try:
                b = load_backend(name)
                out = b.complete("Reply with the single word: ok", "ping", max_tokens=8)
                print(f"  {name:18s} responds: {out.strip()[:40]!r}")
            except Exception as e:  # noqa: BLE001
                print(f"  {name:18s} FAILED: {e}")
                ok = False

    print("== cost estimate (before 25% contingency) ==")
    total = 0.0
    for item, cost in EST.items():
        frontier = "frontier" in item
        keyed = bool(
            os.environ.get(cfg["frontier1"].get("api_key_env", ""), "")
        ) and bool(os.environ.get(cfg["frontier2"].get("api_key_env", ""), ""))
        skip = frontier and not keyed
        note = "  (skipped: no frontier keys)" if skip else ""
        if not skip:
            total += cost
        print(f"  {item:38s} ${cost:7.2f}{note}")
    capped = total * 1.25
    print(f"  {'TOTAL with 25% contingency':38s} ${capped:7.2f}   (cap ${args.cap:.0f})")

    if capped > args.cap:
        print("PREFLIGHT: FAIL - estimate exceeds cap")
        return 1
    if not ok:
        print("PREFLIGHT: FAIL - missing keys or dead endpoint")
        return 1
    print("PREFLIGHT: GO")
    return 0


if __name__ == "__main__":
    sys.exit(main())
