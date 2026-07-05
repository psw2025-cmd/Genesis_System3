#!/usr/bin/env python3
"""
Run Dashboard Browser Proof — scheduler-callable wrapper around the
Playwright spec at tools/playwright-setup/verify_all_ui_tabs.spec.ts.

The job scheduler (core/engine/system3_phase82_job_scheduler.py) only
knows how to invoke "python -m module" or "python script.py" — it has
no native Node/npx job type. This script bridges that: it shells out to
npm/npx, captures the result, and writes a scheduler-friendly
SUCCESS/FAILED status plus a copy of the Playwright JSON summary into
reports/latest/ so paper_day_proof_pack.py's item 6 can eventually read
a real result here instead of being permanently UNVERIFIABLE.

Requires Node.js + npm to be present in the runtime image (the
dashboard/backend/Dockerfile already installs nodejs/npm for the
frontend build step, so this should be available in the same container
— but if Node is missing for any reason, this script fails loudly with
a clear NODE_NOT_AVAILABLE reason rather than silently no-op'ing).

Usage:
    python scripts/run_dashboard_browser_proof.py
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLAYWRIGHT_DIR = ROOT / "tools" / "playwright-setup"
RESULTS_FILE = ROOT / "reports" / "latest" / "ui_route_verification" / "tab_results.json"
OUT_FILE = ROOT / "reports" / "latest" / "dashboard_browser_proof" / "status.json"
OUT_FILE.parent.mkdir(parents=True, exist_ok=True)


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> int:
    print("=" * 70)
    print("DASHBOARD BROWSER PROOF (Playwright wrapper)")
    print("=" * 70)

    npm = shutil.which("npm")
    npx = shutil.which("npx")
    if not npm or not npx:
        result = {"status": "NODE_NOT_AVAILABLE", "generated_at": _utc(),
                  "detail": f"npm={npm} npx={npx} — Node.js not found in this runtime image."}
        OUT_FILE.write_text(json.dumps(result, indent=2))
        print(json.dumps(result, indent=2))
        return 1

    # Ensure deps installed (idempotent; npm ci is fast on a warm cache)
    install = subprocess.run(
        [npm, "ci"], cwd=PLAYWRIGHT_DIR, capture_output=True, text=True, timeout=300,
    )
    if install.returncode != 0:
        result = {"status": "NPM_INSTALL_FAILED", "generated_at": _utc(),
                  "stderr_tail": install.stderr[-1500:]}
        OUT_FILE.write_text(json.dumps(result, indent=2))
        print(json.dumps(result, indent=2))
        return 1

    # Install just the chromium browser binary Playwright needs
    browser_install = subprocess.run(
        [npx, "playwright", "install", "--with-deps", "chromium"],
        cwd=PLAYWRIGHT_DIR, capture_output=True, text=True, timeout=300,
    )
    if browser_install.returncode != 0:
        result = {"status": "BROWSER_INSTALL_FAILED", "generated_at": _utc(),
                  "stderr_tail": browser_install.stderr[-1500:]}
        OUT_FILE.write_text(json.dumps(result, indent=2))
        print(json.dumps(result, indent=2))
        return 1

    test_run = subprocess.run(
        [npx, "playwright", "test", "--config=playwright.ui-verify.config.ts"],
        cwd=PLAYWRIGHT_DIR, capture_output=True, text=True, timeout=180,
    )
    print(test_run.stdout[-3000:])
    if test_run.returncode != 0:
        print(test_run.stderr[-1500:])

    overall_pass = None
    tab_summary = None
    if RESULTS_FILE.exists():
        try:
            tab_summary = json.loads(RESULTS_FILE.read_text())
            overall_pass = tab_summary.get("overallPass")
        except Exception:
            pass

    status = "PASS" if (test_run.returncode == 0 and overall_pass) else "FAIL"
    result = {
        "status": status,
        "generated_at": _utc(),
        "playwright_exit_code": test_run.returncode,
        "overall_pass_from_spec": overall_pass,
        "stderr_tail": test_run.stderr[-800:] if test_run.returncode != 0 else None,
    }
    OUT_FILE.write_text(json.dumps(result, indent=2))
    print(f"\nFinal status: {status}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
