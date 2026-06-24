#!/usr/bin/env python3
"""
Post-market auto pipeline — prediction validation + profit proofs + gate sync.
Runs after daily_gain_validate (15:35 IST). No human input required.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLOUD = os.environ.get("SYSTEM3_API_BASE", "https://genesis-system3-backend.onrender.com").rstrip("/")


def _run(script: str, extra: list[str] | None = None) -> bool:
    path = ROOT / script
    if not path.exists():
        return False
    cmd = [sys.executable, str(path)] + (extra or [])
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=600)
    print(f"[{'OK' if proc.returncode == 0 else 'WARN'}] {script}")
    if proc.stdout:
        print(proc.stdout[-1500:])
    return True


def main() -> int:
    env = os.environ.copy()
    env["SYSTEM3_API_BASE"] = CLOUD
    steps = [
        ("scripts/system3_model_accuracy_tracker.py", ["--api-base", CLOUD]),
        ("scripts/system3_friction_expectancy_proof.py", []),
        ("scripts/system3_model_to_trade_gap_proof.py", []),
        ("scripts/websocket_tick_health_proof.py", []),
        ("scripts/system3_gate_evaluator.py", ["--sync-gates"]),
        ("scripts/system3_production_viability_bridge.py", []),
        ("scripts/system3_blocker_finder.py", ["--api-base", CLOUD]),
    ]
    for script, args in steps:
        path = ROOT / script
        if path.exists():
            subprocess.run([sys.executable, str(path)] + args, cwd=ROOT, env=env, timeout=600)
    print("POST_MARKET_AUTO_PIPELINE_COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
