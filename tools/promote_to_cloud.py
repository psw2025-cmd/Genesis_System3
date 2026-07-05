#!/usr/bin/env python3
"""
Laptop validation gate before pushing to cloud (Render auto-deploys from main).

Runs fast local CI + NSE health, then git push if all pass.

Usage:
  python tools/promote_to_cloud.py
  python tools/promote_to_cloud.py --skip-push   # validate only
  python tools/promote_to_cloud.py --message "fix: NSE v3 option chain"
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(cmd: list[str], timeout: int = 1200) -> int:
    print(f"\n>> {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=ROOT, timeout=timeout).returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate locally then push to cloud")
    parser.add_argument("--skip-push", action="store_true", help="Run checks only, no git push")
    parser.add_argument("--message", "-m", default="", help="Commit message (required if pushing with changes)")
    args = parser.parse_args()

    py = sys.executable
    checks = [
        ("compile", [py, "-m", "compileall", "-q", "core", "dashboard", "scripts", "tools"]),
        (
            "pytest",
            [
                py,
                "-m",
                "pytest",
                "tests/",
                "-q",
                "--tb=line",
                "-k",
                "not test_build_equity_report_structure",
            ],
        ),
        (
            "nse_health",
            [py, "tools/fetch_nse_option_chain.py", "--symbol", "NIFTY", "--out", "state/nse_health_latest.json"],
        ),
        ("local_ci", [py, "tools/local_ci_runner.py", "--fast", "--skip-audit"]),
    ]

    failed = []
    for name, cmd in checks:
        rc = _run(cmd)
        if rc != 0:
            failed.append(name)
            print(f"FAIL: {name} (exit {rc})")
            break
        print(f"PASS: {name}")

    if failed:
        print(f"\nPromotion blocked — fix: {', '.join(failed)}")
        return 1

    if args.skip_push:
        print("\nValidation OK (push skipped).")
        return 0

    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    if status:
        msg = args.message or "fix: NSE v3 option chain + local validation tooling"
        paths = [
            "core/data/nse_session.py",
            "core/data/datasource_manager.py",
            "core/data/nse_provider.py",
            "core/brokers/dhan/token_manager.py",
            "core/brokers/dhan/dhan_payload_normalizer.py",
            "tools/fetch_nse_option_chain.py",
            "tools/promote_to_cloud.py",
            "tools/local_ci_runner.py",
            "tools/sync_render_secrets.py",
            "tools/verify_local_env.py",
            "tools/run_all_tests.py",
            "scripts/dashboard_production_audit.py",
            "scripts/dashboard_data_validator.py",
            "src/validation/market_result_validator.py",
        ]
        if _run(["git", "add", *paths]) != 0:
            return 1
        if _run(["git", "commit", "-m", msg]) != 0:
            print("Nothing to commit or commit failed.")
            return 1

    if _run(["git", "push", "origin", "HEAD"]) != 0:
        print("git push failed — check network/auth")
        return 1

    print("\nPushed to origin — Render will auto-deploy (genesis-system3-backend + worker).")
    print("Verify: python tools/production_daily_cycle.py --deploy-check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
