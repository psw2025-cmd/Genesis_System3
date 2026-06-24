#!/usr/bin/env python3
"""
Production Daily Cycle — single entry point for world-class automated operations.

Runs the full proof → gate → test → report chain with no human input.
Does NOT enable live trading.

Usage:
  python tools/production_daily_cycle.py
  python tools/production_daily_cycle.py --fast     # skip Playwright (CI/local)
  python tools/production_daily_cycle.py --deploy-check  # verify cloud APIs only
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "latest" / "production_daily_cycle"
CLOUD = os.environ.get(
    "SYSTEM3_API_BASE",
    "https://genesis-system3-backend.onrender.com",
).rstrip("/")


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _run(name: str, cmd: List[str], timeout: int = 600) -> Dict[str, Any]:
    env = os.environ.copy()
    env.setdefault("LIVE_TRADING_ENABLED", "0")
    env.setdefault("SYSTEM3_API_BASE", CLOUD)
    try:
        proc = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, timeout=timeout)
        ok = proc.returncode == 0
        return {
            "step": name,
            "passed": ok,
            "exit_code": proc.returncode,
            "stdout_tail": (proc.stdout or "")[-1500:],
            "stderr_tail": (proc.stderr or "")[-500:],
        }
    except subprocess.TimeoutExpired:
        return {"step": name, "passed": False, "exit_code": 124, "error": f"timeout after {timeout}s"}
    except Exception as exc:
        return {"step": name, "passed": False, "exit_code": -1, "error": str(exc)[:200]}


def _cloud_probe() -> Dict[str, Any]:
    import urllib.request

    endpoints = [
        "/api/state",
        "/api/auto_gates",
        "/api/scanner/equity_options",
        "/api/scanner/top_contract_gainers",
        "/api/accuracy_trend",
        "/api/portfolio/unified",
    ]
    out: Dict[str, Any] = {}
    for ep in endpoints:
        try:
            with urllib.request.urlopen(f"{CLOUD}{ep}", timeout=90) as resp:
                body = resp.read(8000).decode("utf-8", errors="replace")
                out[ep] = {"ok": resp.status == 200, "sample": body[:400]}
        except Exception as exc:
            out[ep] = {"ok": False, "error": str(exc)[:120]}
    return out


def build_steps(fast: bool, deploy_only: bool) -> List[Tuple[str, List[str], int]]:
    py = sys.executable
    if deploy_only:
        return []
    steps: List[Tuple[str, List[str], int]] = [
        ("ui_market_cross_verify", [py, "scripts/ui_market_cross_verify.py"], 300),
        ("pytest", [py, "-m", "pytest", "tests/", "-q", "--tb=no"], 300),
        ("post_market_pipeline", [py, "scripts/system3_post_market_auto_pipeline.py"], 600),
        ("gate_evaluator", [py, "scripts/system3_gate_evaluator.py", "--sync-gates"], 120),
        ("local_code_review", [py, "tools/local_code_review.py"], 300),
        ("dashboard_audit", [py, "tools/dashboard_full_audit.py"], 180),
        ("blocker_finder", [py, "scripts/system3_blocker_finder.py", "--api-base", CLOUD], 120),
    ]
    if not fast:
        from subprocess_helpers import playwright_test_cmd
        steps.append(("playwright", playwright_test_cmd(), 300))
    return steps


def main() -> int:
    parser = argparse.ArgumentParser(description="Production daily cycle")
    parser.add_argument("--fast", action="store_true", help="Skip Playwright")
    parser.add_argument("--deploy-check", action="store_true", help="Cloud API probe only")
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    steps_out: List[Dict[str, Any]] = []
    for name, cmd, timeout in build_steps(args.fast, args.deploy_check):
        print(f"Running {name}...")
        steps_out.append(_run(name, cmd, timeout))

    cloud = _cloud_probe()
    gates_path = ROOT / "reports" / "latest" / "system3_auto_gates" / "summary.json"
    gates: Dict[str, Any] = {}
    if gates_path.exists():
        try:
            gates = json.loads(gates_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    cloud_ok = all(v.get("ok") for v in cloud.values())
    steps_pass = sum(1 for s in steps_out if s.get("passed"))
    critical = [s for s in steps_out if not s.get("passed") and s["step"] in ("pytest", "gate_evaluator")]

    payload = {
        "generated_utc": _utc(),
        "mode": "deploy_check" if args.deploy_check else ("fast" if args.fast else "full"),
        "cloud_url": CLOUD,
        "cloud_probe": cloud,
        "cloud_all_ok": cloud_ok,
        "steps": steps_out,
        "steps_passed": steps_pass,
        "steps_total": len(steps_out),
        "gates_passing": gates.get("gates_passing"),
        "gates_total": gates.get("gates_total"),
        "trade_ready": gates.get("trade_ready", False),
        "analyzer_ready": gates.get("analyzer_ready", False),
        "open_blockers": gates.get("open_blockers", []),
        "live_trading_enabled": False,
        "production_grade": steps_pass == len(steps_out) and cloud_ok and not critical,
        "verdict": "PRODUCTION_CYCLE_OK" if not critical and cloud_ok else "PRODUCTION_CYCLE_PARTIAL",
    }
    (OUT / "summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    lines = [
        "# Production Daily Cycle",
        "",
        f"Verdict: **{payload['verdict']}**",
        f"Gates: **{gates.get('gates_passing', '?')}/{gates.get('gates_total', '?')}**",
        f"Cloud: **{'OK' if cloud_ok else 'PARTIAL'}**",
        "",
        "## Steps",
    ]
    for s in steps_out:
        lines.append(f"- {s['step']}: {'PASS' if s.get('passed') else 'FAIL'}")
    (OUT / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT / 'summary.md'}")
    return 0 if payload["production_grade"] or (not critical and cloud_ok) else 1


if __name__ == "__main__":
    raise SystemExit(main())
