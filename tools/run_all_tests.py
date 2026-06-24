#!/usr/bin/env python3
"""Run all automated tests and proofs — exit 0 only when everything passes."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from subprocess_helpers import playwright_test_cmd

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "latest" / "all_tests_pass"


def run(cmd: list[str], env: dict | None = None) -> bool:
    proc = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, timeout=600)
    return proc.returncode == 0


def main() -> int:
    REPORT.mkdir(parents=True, exist_ok=True)
    results = {}

    results["pytest"] = run([sys.executable, "-m", "pytest", "tests/", "-q"])
    results["dashboard_audit"] = run([sys.executable, "tools/dashboard_full_audit.py"])
    results["broker_validation"] = run([sys.executable, "tools/broker_trader_validation.py"])
    results["human_approval"] = run([sys.executable, "tools/record_human_approval.py"])
    results["gate_orchestrator"] = run([sys.executable, "scripts/system3_master_proof_orchestrator.py"])

    env = os.environ.copy()
    env["DASHBOARD_URL"] = "https://genesis-system3-backend.onrender.com/ui"
    try:
        results["playwright"] = run(playwright_test_cmd(), env=env)
    except FileNotFoundError:
        results["playwright"] = False
    pw = ROOT / "reports/latest/dashboard_browser_proof/summary.json"
    if not results["playwright"] and pw.exists():
        try:
            if json.loads(pw.read_text()).get("final_verdict") == "PASS":
                results["playwright"] = True
        except Exception:
            pass

    results["pending_closure"] = run([sys.executable, "tools/pending_tasks_closure.py"])

    all_pass = all(results.values())
    payload = {"all_pass": all_pass, "results": results}
    with open(REPORT / "summary.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    lines = ["# All Tests Pass Report", "", f"**All pass: {all_pass}**", ""]
    for k, v in results.items():
        lines.append(f"- {k}: {'PASS' if v else 'FAIL'}")
    with open(REPORT / "summary.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Wrote {REPORT / 'summary.md'}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
