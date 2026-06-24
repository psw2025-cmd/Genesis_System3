#!/usr/bin/env python3
"""
Local CI — replaces GitHub Actions on your laptop (no billing, no Codespaces).

Mirrors .github/workflows/ci.yml core gates + dashboard production audit.

Usage:
  python tools/local_ci_runner.py
  python tools/local_ci_runner.py --fast          # skip slow proof batch
  python tools/local_ci_runner.py --skip-audit    # static/compile only

Requires backend running for API audit:
  tools\\run_local_stack.bat --no-pause --no-open
"""

from __future__ import annotations

import argparse
import json
import os
import py_compile
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "latest" / "local_ci"
LOCAL = "http://127.0.0.1:8000"

os.environ.setdefault("SYSTEM3_LOCAL", "1")
os.environ.setdefault("SYSTEM3_API_BASE", LOCAL)
os.environ.setdefault("LIVE_TRADING_ENABLED", "0")
os.environ.setdefault("SYSTEM3_LIVE_TRADING_ALLOWED", "0")
os.environ.setdefault("SYSTEM3_REAL_ONLY", "1")
os.environ.setdefault("SYSTEM3_MODE", "analyzer")
os.environ.setdefault("ANALYZE_MODE", "1")


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _py() -> str:
    venv = ROOT / "venv" / "Scripts" / "python.exe"
    return str(venv) if venv.exists() else sys.executable


def _step(name: str, fn) -> Dict[str, Any]:
    try:
        fn()
        return {"step": name, "passed": True}
    except Exception as exc:
        return {"step": name, "passed": False, "error": str(exc)[:300]}


def _run_cmd(name: str, cmd: List[str], timeout: int = 300) -> Dict[str, Any]:
    try:
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout, env=os.environ.copy())
        return {
            "step": name,
            "passed": proc.returncode == 0,
            "exit_code": proc.returncode,
            "stdout_tail": (proc.stdout or "")[-800:],
            "stderr_tail": (proc.stderr or "")[-400:],
            "error": (proc.stderr or proc.stdout or f"exit {proc.returncode}")[-300:] if proc.returncode != 0 else None,
        }
    except subprocess.TimeoutExpired:
        return {"step": name, "passed": False, "error": f"timeout after {timeout}s"}
    except Exception as exc:
        return {"step": name, "passed": False, "error": str(exc)[:200]}


def _backend_up() -> bool:
    try:
        with urllib.request.urlopen(f"{LOCAL}/api/health", timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Local CI (GitHub Actions replacement)")
    parser.add_argument("--fast", action="store_true", help="Skip slow proof batch + arch gate")
    parser.add_argument("--skip-audit", action="store_true", help="Skip live API audit")
    parser.add_argument("--skip-arch", action="store_true", help="Skip root architecture gate")
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    py = _py()
    steps: List[Dict[str, Any]] = []

    # --- CI mirror: workflow policy (simplified) ---
    def workflow_policy():
        workflows = sorted((ROOT / ".github" / "workflows").glob("*.yml"))
        if not workflows:
            raise RuntimeError("no workflows found")
        # informational only — multiple workflows exist in repo history

    steps.append(_step("workflow_policy_info", workflow_policy))

    # --- root architecture gate (skipped in --fast — compares all local git changes) ---
    if not args.fast and not args.skip_arch:
        steps.append(_run_cmd("root_architecture_gate", [py, ".github/scripts/root_architecture_gate.py"], timeout=120))

    # --- py_compile critical scripts (ci.yml) ---
    compile_targets = [
        "system3_control_plane.py",
        "scripts/system3_full_repo_verification.py",
        "scripts/system3_master_proof_orchestrator.py",
        "dashboard/backend/app.py",
        ".github/scripts/root_architecture_gate.py",
    ]

    def compile_all():
        for rel in compile_targets:
            p = ROOT / rel
            if not p.exists():
                raise FileNotFoundError(rel)
            py_compile.compile(str(p), doraise=True)

    steps.append(_step("py_compile_critical", compile_all))

    # --- dashboard import smoke (subprocess — avoids startup hang in CI process) ---
    steps.append(
        _run_cmd(
            "dashboard_backend_import_smoke",
            [
                py,
                "-c",
                "import os; os.environ['LIVE_TRADING_ENABLED']='0'; "
                "import dashboard.backend.app as m; assert m.app is not None; print('ok')",
            ],
            timeout=90,
        )
    )

    # --- node syntax ---
    app_js = ROOT / "dashboard" / "app.js"
    if app_js.exists():
        steps.append(_run_cmd("node_check_app_js", ["node", "--check", str(app_js)], timeout=20))
    else:
        steps.append({"step": "node_check_app_js", "passed": False, "error": "app.js missing"})

    # --- issue proof batch (optional) ---
    if not args.fast:
        steps.append(
            _run_cmd(
                "issue_24_26_27_28_proof",
                [py, "scripts/system3_issue_24_26_27_28_proof_batch.py"],
                timeout=600,
            )
        )

    # --- pytest subset ---
    tests = (
        ["tests/test_system3_auto_gates.py"]
        if args.fast
        else ["tests/test_system3_auto_gates.py", "tests/test_equity_option_scanner.py"]
    )
    existing = [t for t in tests if (ROOT / t).exists()]
    if existing:
        steps.append(
            _run_cmd(
                "pytest_core", [py, "-m", "pytest", *existing, "-q", "--tb=short"], timeout=180 if args.fast else 300
            )
        )

    # --- local code review (slow — skip in --fast) ---
    if not args.fast:
        steps.append(_run_cmd("local_code_review", [py, "tools/local_code_review.py"], timeout=300))

    # --- dashboard production audit (needs running backend) ---
    if not args.skip_audit:
        if _backend_up():
            steps.append(
                _run_cmd(
                    "dashboard_production_audit",
                    [py, "scripts/dashboard_production_audit.py", "--base", LOCAL, "--fast"],
                    timeout=180,
                )
            )
        else:
            steps.append(
                {
                    "step": "dashboard_production_audit",
                    "passed": False,
                    "error": "backend not running — run tools\\run_local_stack.bat first",
                }
            )

    passed = sum(1 for s in steps if s.get("passed"))
    failed = [s for s in steps if not s.get("passed")]
    verdict = "LOCAL_CI_PASS" if not failed else "LOCAL_CI_FAIL"

    payload = {
        "generated_utc": _utc(),
        "mode": "fast" if args.fast else "full",
        "backend_url": LOCAL,
        "backend_up": _backend_up(),
        "github_replacement": True,
        "steps": steps,
        "passed": passed,
        "total": len(steps),
        "failed_steps": [s["step"] for s in failed],
        "verdict": verdict,
        "notes": [
            "Runs entirely on laptop — no GitHub Actions minutes",
            "Codespaces not required",
            "git push optional; commit locally with: git commit -am 'msg'",
        ],
    }

    (OUT / "summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    lines = [
        "# Local CI Report (GitHub Actions replacement)",
        "",
        f"Generated: `{payload['generated_utc']}`",
        f"Verdict: **{verdict}**",
        f"Steps: **{passed}/{len(steps)}** passed",
        f"Backend: **{'UP' if payload['backend_up'] else 'DOWN'}** at `{LOCAL}`",
        "",
        "## Steps",
    ]
    for s in steps:
        mark = "PASS" if s.get("passed") else "FAIL"
        err = f" — {s.get('error', s.get('stderr_tail', ''))[:120]}" if not s.get("passed") else ""
        lines.append(f"- {s['step']}: **{mark}**{err}")

    lines.extend(
        [
            "",
            "## Quick commands",
            "```bat",
            "tools\\run_local_stack.bat",
            "tools\\run_local_ci.bat",
            "tools\\run_local_all.bat",
            "```",
        ]
    )
    (OUT / "summary.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"Verdict: {verdict} ({passed}/{len(steps)})")
    print(f"Report: {OUT / 'summary.md'}")
    for s in failed:
        print(f"  FAIL: {s['step']}: {s.get('error', s.get('stderr_tail', ''))[:100]}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
