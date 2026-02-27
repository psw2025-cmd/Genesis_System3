#!/usr/bin/env python3
"""
Run-All failure reporter: writes proof/archive/RUN_ALL_FAIL_*.json and prints
reason, impact, and next actions. Called by Run-All.bat when a step fails.

Reads env vars (set by Run-All.bat):
  RUN_ALL_FAIL_STEP   - Step name (e.g. "Step 3: Create venv")
  RUN_ALL_FAIL_REASON - Why it failed
  RUN_ALL_FAIL_IMPACT - What is affected
  RUN_ALL_FAIL_NEXT   - Semicolon-separated next actions (files/scripts to run)

Usage: set env vars then: python scripts/run_all_report_fail.py
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROOF = ROOT / "proof" / "archive"
PROOF.mkdir(parents=True, exist_ok=True)


def main():
    step = os.environ.get("RUN_ALL_FAIL_STEP", "Unknown step")
    reason = os.environ.get("RUN_ALL_FAIL_REASON", "No reason provided")
    impact = os.environ.get("RUN_ALL_FAIL_IMPACT", "Run cannot continue until fixed.")
    next_raw = os.environ.get("RUN_ALL_FAIL_NEXT", "Fix the step and rerun Run-All.bat")
    next_actions = [s.strip() for s in next_raw.split(";") if s.strip()]

    report = {
        "timestamp": datetime.now().isoformat(),
        "failed_step": step,
        "reason": reason,
        "impact": impact,
        "next_actions": next_actions,
    }
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = PROOF / f"RUN_ALL_FAIL_{ts}.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("")
    print("=" * 70)
    print("  RUN-ALL FAILED (strict mode - fix before proceeding)")
    print("=" * 70)
    print(f"[FAIL] {step}")
    print(f"Reason: {reason}")
    print(f"Impact: {impact}")
    print("Next actions (run in sequence after fixing):")
    for i, a in enumerate(next_actions, 1):
        print(f"  {i}. {a}")
    print(f"\nReport saved: {report_path}")
    print("=" * 70)
    print("")
    sys.exit(1)


if __name__ == "__main__":
    main()
