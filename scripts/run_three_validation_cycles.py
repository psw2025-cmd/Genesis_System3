#!/usr/bin/env python3
"""
Run three consecutive production validation cycles with backend up.
Exits 0 only if all three cycles pass; then generates proof pack.
"""
import os
import sys
import subprocess
import time
import requests
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")


def wait_for_backend(timeout_sec=60):
    for _ in range(timeout_sec):
        try:
            r = requests.get(f"{BACKEND_URL}/api/health", timeout=2)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


def main():
    print("Checking backend...")
    if not wait_for_backend():
        print("[ERROR] Backend not responding at", BACKEND_URL)
        print("Start backend first, e.g.: cd dashboard/backend && python -m uvicorn app:app --host 0.0.0.0 --port 8000")
        return 1

    print("[OK] Backend is up\n")
    passed_cycles = 0
    for cycle in range(1, 4):
        print(f"\n{'='*60}\nCYCLE {cycle}/3\n{'='*60}")
        try:
            result = subprocess.run(
                [sys.executable, str(ROOT / "production_grade_validation.py")],
                cwd=str(ROOT),
                timeout=120,
            )
        except subprocess.TimeoutExpired:
            print(f"[FAIL] Cycle {cycle} timed out after 120 seconds")
            return 1
        if result.returncode != 0:
            print(f"[FAIL] Cycle {cycle} did not pass")
            return 1
        passed_cycles += 1
        print(f"[OK] Cycle {cycle} PASSED")

    print("\n[OK] Three consecutive cycles PASSED. Generating proof pack...")
    try:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "generate_proof_pack.py")],
            cwd=str(ROOT),
            timeout=30,
        )
        if result.returncode != 0:
            print("[WARNING] Proof pack generation failed")
        else:
            print("[OK] Proof pack generated")
    except subprocess.TimeoutExpired:
        print("[WARNING] Proof pack generation timed out after 30 seconds")
    return 0


if __name__ == "__main__":
    sys.exit(main())
