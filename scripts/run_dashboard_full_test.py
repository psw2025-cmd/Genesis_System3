#!/usr/bin/env python3
"""
Dashboard full test orchestrator (production-grade = strict + guided).

Behavior:
- Runs each dashboard test step in SEQUENCE.
- If a step FAILS, it is recorded with:
  - reason (from the underlying test)
  - likely impact
  - recommended follow-up files/scripts to check
- Later steps may be marked SKIPPED if a prerequisite failed.
- At the end:
  - Prints a structured summary.
  - Writes a JSON report to proof/archive/DASHBOARD_FULL_TEST_YYYYMMDD_HHMMSS.json.
  - Exits with:
      0 if ALL steps passed,
      1 if ANY step failed (so you and CI can see it's not fully OK).

Usage (from repo root, with .venv activated):
  python scripts/run_dashboard_full_test.py
  python scripts/run_dashboard_full_test.py --no-playwright   # skip Playwright
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
PROOF_DIR = ROOT / "proof" / "archive"
PROOF_DIR.mkdir(parents=True, exist_ok=True)


def import_verify_module():
    """Import verify_dashboard_complete as a module."""
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        import verify_dashboard_complete as vdc  # type: ignore

        return vdc
    except Exception as e:  # pragma: no cover - defensive
        print(f"[ERROR] Could not import verify_dashboard_complete: {e}")
        return None


def run_playwright_step() -> Dict[str, Any]:
    """Run Playwright dashboard verification as a single step."""
    from subprocess import CalledProcessError, run

    script = ROOT / "tools" / "playwright_dashboard_verification.py"
    if not script.exists():
        return {
            "name": "Playwright Visual Verification",
            "status": "SKIPPED",
            "detail": "playwright_dashboard_verification.py not found",
            "impact": "Visual dashboard verification not run",
            "next_actions": [
                "Check that tools/playwright_dashboard_verification.py exists",
                "See docs/AGENT_DASHBOARD_VERIFICATION_PLAYWRIGHT.md",
            ],
        }

    print("\n[Playwright] Running visual verification ...")
    try:
        result = run([sys.executable, str(script)], cwd=str(ROOT))
        if result.returncode == 0:
            return {
                "name": "Playwright Visual Verification",
                "status": "PASS",
                "detail": "Playwright verification script completed successfully",
                "impact": "Basic visual/structural checks passed",
                "next_actions": [],
            }
        else:
            return {
                "name": "Playwright Visual Verification",
                "status": "FAIL",
                "detail": "Playwright verification reported issues (see console and proof/archive/dashboard_verification_*.json)",
                "impact": "Possible visual/dashboard issues (API docs, Streamlit, or React UI)",
                "next_actions": [
                    "Open proof/archive/dashboard_verification_*.json for details",
                    "Open screenshots under proof/archive/dashboard_screenshots_*",
                    "Fix backend/Streamlit/React issues shown, then rerun: python tools/playwright_dashboard_verification.py",
                ],
            }
    except CalledProcessError as e:  # pragma: no cover - defensive
        return {
            "name": "Playwright Visual Verification",
            "status": "FAIL",
            "detail": f"Playwright process error: {e}",
            "impact": "Visual verification did not complete",
            "next_actions": [
                "Ensure playwright is installed: pip install playwright && playwright install chromium",
                "Then rerun: python tools/playwright_dashboard_verification.py",
            ],
        }


def main():
    parser = argparse.ArgumentParser(
        description="Run all dashboard tests in sequence with structured failure reporting."
    )
    parser.add_argument("--no-playwright", action="store_true", help="Skip Playwright verification step.")
    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("  DASHBOARD FULL TEST (strict + guided)")
    print("=" * 70)
    print(f"Root: {ROOT}")

    vdc = import_verify_module()
    steps: List[Dict[str, Any]] = []
    any_fail = False

    if vdc is None:
        steps.append(
            {
                "name": "Import verify_dashboard_complete",
                "status": "FAIL",
                "detail": "Could not import scripts/verify_dashboard_complete.py",
                "impact": "Cannot run API/front-end dashboard verification tests",
                "next_actions": [
                    "Check that scripts/verify_dashboard_complete.py exists and has no syntax errors",
                    "Then rerun: python scripts/run_dashboard_full_test.py",
                ],
            }
        )
    else:
        # Step sequence: maps test function -> impact + next actions
        test_plan = [
            {
                "name": "Backend Running",
                "fn": getattr(vdc, "test_backend_running", None),
                "impact": "If this fails, no API or dashboard endpoint will work; all subsequent tests depend on backend.",
                "next_actions": [
                    "Start backend: use START_BACKEND_FOR_TESTING.bat or START_FULL_DASHBOARD_SYSTEM.bat",
                    "Then rerun: python scripts/verify_dashboard_complete.py",
                ],
            },
            {
                "name": "SSOT Endpoint",
                "fn": getattr(vdc, "test_ssot_endpoint", None),
                "impact": "State SSOT (/api/state) invalid; dashboard Overview/Signals/PaperTrading may show incorrect data.",
                "next_actions": [
                    "Inspect dashboard/backend/app.py SSOT code and runtime_state_store.py",
                    "Fix SSOT shape or state_store, then rerun: python scripts/verify_dashboard_complete.py",
                ],
            },
            {
                "name": "Synthetic Data Realism",
                "fn": getattr(vdc, "test_synthetic_data", None),
                "impact": "Synthetic option chain data may produce unrealistic IV; affects demo / market-closed behavior.",
                "next_actions": [
                    "Check synthetic_data_generator and IV bounds in scripts/verify_dashboard_complete.py",
                    "Adjust IV ranges or synthetic config, then rerun: python scripts/verify_dashboard_complete.py",
                ],
            },
            {
                "name": "Risk Limits Logic",
                "fn": getattr(vdc, "test_risk_limits", None),
                "impact": "Risk endpoints (/api/risk/portfolio, /api/risk/check-limits) may misbehave; Risk dashboard may be wrong.",
                "next_actions": [
                    "Inspect risk config and risk endpoints in dashboard/backend/app.py",
                    "Fix risk limit calculations and re-run: python scripts/verify_dashboard_complete.py",
                ],
            },
            {
                "name": "API Endpoints",
                "fn": getattr(vdc, "test_endpoints", None),
                "impact": "Core API endpoints (health, positions, pnl, qc, signal, risk, perf) may be down; multiple dashboard tabs impacted.",
                "next_actions": [
                    "Check logs under logs/ and outputs/health.json for errors",
                    "Fix failing endpoint handlers in dashboard/backend/app.py",
                    "Rerun: python scripts/verify_dashboard_complete.py",
                ],
            },
            {
                "name": "Frontend Pages",
                "fn": getattr(vdc, "test_frontend_pages", None),
                "impact": "One or more React routes (/, /overview, /trading, /signals, /risk, /ml, /alerts) may not load.",
                "next_actions": [
                    "Ensure Vite dev server is running (npm run dev in dashboard/frontend)",
                    "Check routing in dashboard/frontend/src/App.tsx",
                    "Rerun: python scripts/verify_dashboard_complete.py",
                ],
            },
            {
                "name": "Data Consistency",
                "fn": getattr(vdc, "test_consistency", None),
                "impact": "SSOT vs /api/health vs /api/positions vs /api/pnl mismatch; Overview/PaperTrading numbers inconsistent.",
                "next_actions": [
                    "Inspect SSOT and health JSON (outputs/health.json, SSOT state store)",
                    "Align PnL/positions logic across app.py and state store; rerun verify_dashboard_complete.py",
                ],
            },
        ]

        backend_ok = True
        for item in test_plan:
            name = item["name"]
            fn = item["fn"]
            impact = item["impact"]
            next_actions = item["next_actions"]

            if fn is None:
                steps.append(
                    {
                        "name": name,
                        "status": "SKIPPED",
                        "detail": "Test function not found in verify_dashboard_complete.py",
                        "impact": impact,
                        "next_actions": [
                            "Check scripts/verify_dashboard_complete.py for renamed or removed tests",
                            "Restore or adjust tests, then rerun run_dashboard_full_test.py",
                        ],
                    }
                )
                any_fail = True
                # If the Backend Running test itself is missing, treat backend as NOT OK
                # so dependent tests are skipped consistently.
                if name == "Backend Running":
                    backend_ok = False
                continue

            # If backend is not OK, skip tests that depend on it
            if not backend_ok and name != "Backend Running":
                steps.append(
                    {
                        "name": name,
                        "status": "SKIPPED",
                        "detail": "Skipped because Backend Running failed.",
                        "impact": impact,
                        "next_actions": next_actions,
                    }
                )
                continue

            print(f"\n[VERIFY] {name} ...")
            try:
                passed = bool(fn())
            except Exception as e:  # pragma: no cover - defensive
                passed = False
                detail = f"Exception while running test: {e}"
            else:
                detail = "See console output above."

            status = "PASS" if passed else "FAIL"
            steps.append(
                {
                    "name": name,
                    "status": status,
                    "detail": detail,
                    "impact": impact,
                    "next_actions": [] if passed else next_actions,
                }
            )
            if not passed:
                any_fail = True
                if name == "Backend Running":
                    backend_ok = False

    # Optional Playwright step
    if not args.no_playwright:
        steps.append(run_playwright_step())
        if steps[-1]["status"] == "FAIL":
            any_fail = True

    # Write JSON report
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = PROOF_DIR / f"DASHBOARD_FULL_TEST_{ts}.json"
    report = {
        "timestamp": datetime.now().isoformat(),
        "root": str(ROOT),
        "steps": steps,
        "overall_status": "PASS" if not any_fail else "FAIL",
    }
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Print summary
    print("\n" + "=" * 70)
    print("  DASHBOARD FULL TEST SUMMARY")
    print("=" * 70)
    for s in steps:
        print(f"[{s['status']}] {s['name']}: {s['detail']}")
        if s.get("next_actions") and s["status"] == "FAIL":
            print("   Next actions:")
            for a in s["next_actions"]:
                print(f"     - {a}")

    print(f"\nReport saved to: {report_path}")
    print(f"Overall status: {'PASS' if not any_fail else 'FAIL'}")
    print("=" * 70 + "\n")

    sys.exit(0 if not any_fail else 1)


if __name__ == "__main__":
    main()
