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
CLOUD = os.environ.get("SYSTEM3_API_BASE", "http://127.0.0.1:8000").rstrip("/")


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


def _is_server_alive(base_url: str) -> bool:
    try:
        import urllib.request
        with urllib.request.urlopen(f"{base_url}/api/health", timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False


def main() -> int:
    env = os.environ.copy()
    env["SYSTEM3_API_BASE"] = CLOUD

    server_proc = None
    started_server = False

    if not _is_server_alive(CLOUD) and ("127.0.0.1" in CLOUD or "localhost" in CLOUD):
        print(f"[PIPELINE-ORCHESTRATION] Local backend offline at {CLOUD}. Launching FastAPI backend...")
        try:
            server_proc = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "uvicorn",
                    "dashboard.backend.app:app",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "8000",
                    "--log-level",
                    "warning",
                ],
                cwd=ROOT,
                env=env,
            )
            import time
            for attempt in range(40):
                if _is_server_alive(CLOUD):
                    started_server = True
                    print(f"[PIPELINE-ORCHESTRATION] FastAPI backend ready on {CLOUD}")
                    break
                time.sleep(0.5)
            if not started_server:
                print(f"[PIPELINE-ORCHESTRATION] FastAPI backend startup timed out; proceeding with disk fallbacks.")
        except Exception as exc:
            print(f"[PIPELINE-ORCHESTRATION] Subprocess launch skipped: {exc}; proceeding with disk fallbacks.")

    steps = [
        ("scripts/system3_model_accuracy_tracker.py", ["--api-base", CLOUD]),
        ("scripts/system3_friction_expectancy_proof.py", []),
        ("scripts/system3_model_to_trade_gap_proof.py", []),
        ("scripts/websocket_tick_health_proof.py", []),
        ("scripts/system3_gate_evaluator.py", ["--sync-gates"]),
        ("scripts/system3_production_viability_bridge.py", []),
        ("scripts/system3_blocker_finder.py", ["--api-base", CLOUD]),
    ]
    try:
        for script, args in steps:
            path = ROOT / script
            if path.exists():
                subprocess.run([sys.executable, str(path)] + args, cwd=ROOT, env=env, timeout=600)
    finally:
        if server_proc:
            print("[PIPELINE-ORCHESTRATION] Terminating local FastAPI backend...")
            server_proc.terminate()
            try:
                server_proc.wait(timeout=5)
            except Exception:
                server_proc.kill()

    print("POST_MARKET_AUTO_PIPELINE_COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
