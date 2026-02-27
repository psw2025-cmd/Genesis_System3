"""Auto-run the full verification checklist (safe env) until it passes or max attempts reached.

This script calls `run_full_verification_with_env.bat` and captures each attempt's
output into `logs/inspector/verification_attempt_<timestamp>_<n>.log`.

Usage:
  .\venv\Scripts\python.exe tools\auto_verify_until_pass.py --attempts 3
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
import time
import argparse

ROOT = Path(__file__).resolve().parents[1]
INSPECTOR = ROOT / "logs" / "inspector"
INSPECTOR.mkdir(parents=True, exist_ok=True)


def run_attempt(attempt, timeout=600):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = INSPECTOR / f"verification_attempt_{ts}_{attempt}.log"
    cmd = [str(ROOT / "run_full_verification_with_env.bat")]
    print(f"Running attempt {attempt}, logging to {out_path}")
    with out_path.open("w", encoding="utf-8", newline="") as f:
        f.write(f"Attempt {attempt} started: {datetime.now().isoformat()}\n")
        try:
            proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout)
            f.write("--- STDOUT ---\n")
            f.write(proc.stdout or "")
            f.write("\n--- STDERR ---\n")
            f.write(proc.stderr or "")
            f.write(f"\nExit code: {proc.returncode}\n")
            return proc.returncode, out_path
        except subprocess.TimeoutExpired as e:
            f.write("\nTIMEOUT\n")
            return 124, out_path
        except Exception as e:
            f.write("\nERROR: " + str(e) + "\n")
            return 2, out_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempts", type=int, default=3)
    parser.add_argument("--pause", type=int, default=5, help="Seconds between attempts")
    args = parser.parse_args()

    for i in range(1, args.attempts + 1):
        code, logp = run_attempt(i)
        print(f"Attempt {i} finished with code {code} (log: {logp})")
        if code == 0:
            print("Verification succeeded on attempt", i)
            return 0
        if i < args.attempts:
            print(f"Waiting {args.pause}s before next attempt...")
            time.sleep(args.pause)

    print("All attempts finished. Verification did not pass.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
