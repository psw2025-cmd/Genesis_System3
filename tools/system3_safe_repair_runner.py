#!/usr/bin/env python3
"""Analyzer-safe repair runner.

Runs existing proof and repair scripts, then writes a compact report.
No secrets are printed. No order routes are called. No approval or history is fabricated.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "latest" / "safe_repair_runner"
API_BASE = os.environ.get("SYSTEM3_API_BASE", "https://genesis-system3-backend.onrender.com").rstrip("/")

ENDPOINTS = [
    "/api/health",
    "/api/state",
    "/api/status",
    "/api/broker/status",
    "/api/broker/dhan/status",
    "/api/broker/funds",
    "/api/broker/holdings",
    "/api/broker/positions/live",
    "/api/approval/status",
    "/api/kill-switch/status",
]

COMMANDS = [
    [sys.executable, "scripts/system3_gate_evaluator.py", "--sync-gates"],
    [sys.executable, "tools/system3_auto_coordinator.py", "--full", "--api-base", API_BASE],
    [sys.executable, "scripts/system3_model_accuracy_tracker.py", "--api-base", API_BASE],
    [sys.executable, "scripts/system3_option_visibility_audit.py", "--api-base", API_BASE],
    [sys.executable, "scripts/system3_friction_expectancy_proof.py"],
    [sys.executable, "scripts/websocket_tick_health_proof.py"],
    [sys.executable, "scripts/system3_blocker_finder.py", "--api-base", API_BASE],
    [sys.executable, "tools/system3_github_render_failure_tracker.py"],
]


def utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def env() -> Dict[str, str]:
    e = os.environ.copy()
    e["LIVE_TRADING_ENABLED"] = "0"
    e["SYSTEM3_LIVE_TRADING_ALLOWED"] = "0"
    e["ANALYZE_MODE"] = "1"
    e["SYSTEM3_API_BASE"] = API_BASE
    e["DASHBOARD_BASE_URL"] = API_BASE
    return e


def probe(endpoint: str) -> Dict[str, Any]:
    headers = {"User-Agent": "system3-safe-repair-runner"}
    key = os.environ.get("DASHBOARD_API_KEY")
    if key:
        headers["X-API-Key"] = key
    url = API_BASE + endpoint
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=25) as r:
            body = r.read(50000).decode("utf-8", errors="replace")
            parsed = None
            try:
                parsed = json.loads(body)
            except Exception:
                pass
            return {"endpoint": endpoint, "ok": 200 <= r.status < 400, "status": r.status, "json": parsed, "sample": body[:1000]}
    except urllib.error.HTTPError as ex:
        body = ex.read(50000).decode("utf-8", errors="replace") if hasattr(ex, "read") else ""
        return {"endpoint": endpoint, "ok": False, "status": ex.code, "sample": body[:1000]}
    except Exception as ex:
        return {"endpoint": endpoint, "ok": False, "status": 0, "error": type(ex).__name__ + ": " + str(ex)[:300]}


def run(cmd: List[str]) -> Dict[str, Any]:
    if len(cmd) > 1 and cmd[1].endswith(".py") and not (ROOT / cmd[1]).exists():
        return {"cmd": cmd, "passed": False, "skipped": True, "reason": "script_missing"}
    try:
        p = subprocess.run(cmd, cwd=ROOT, env=env(), text=True, capture_output=True, timeout=900)
        return {"cmd": cmd, "passed": p.returncode == 0, "exit_code": p.returncode, "stdout_tail": (p.stdout or "")[-2500:], "stderr_tail": (p.stderr or "")[-1500:]}
    except Exception as ex:
        return {"cmd": cmd, "passed": False, "exit_code": -1, "error": type(ex).__name__ + ": " + str(ex)[:300]}


def read_json(path: str) -> Dict[str, Any]:
    p = ROOT / path
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8", errors="replace"))
    except Exception as ex:
        return {"error": str(ex)}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    before = [probe(e) for e in ENDPOINTS]
    results = [run(c) for c in COMMANDS]
    after = [probe(e) for e in ENDPOINTS]
    gates = read_json("reports/latest/system3_auto_gates/summary.json")
    board = read_json("reports/latest/autopilot_proof_board/summary.json")
    visible = read_json("reports/latest/dashboard_visible_issue_tracker/summary.json")
    gh_render = read_json("reports/latest/github_render_failure_tracker/summary.json")

    failed_endpoints = [r for r in after if not r.get("ok")]
    failed_commands = [r for r in results if not r.get("passed") and not r.get("skipped")]
    status = "PASS" if not failed_endpoints and not failed_commands and gates.get("trade_ready") is True and visible.get("status") == "PASS" and gh_render.get("status") == "PASS" and board.get("status") == "PASS" else "BLOCKED"

    payload = {
        "generated_utc": utc(),
        "status": status,
        "api_base": API_BASE,
        "live_trading_enabled": False,
        "system_ready_for_live_trading": False,
        "order_routes_called": False,
        "secrets_printed": False,
        "endpoint_fail_count": len(failed_endpoints),
        "command_fail_count": len(failed_commands),
        "gates_passing": gates.get("gates_passing"),
        "gates_total": gates.get("gates_total"),
        "trade_ready": gates.get("trade_ready"),
        "analyzer_ready": gates.get("analyzer_ready"),
        "open_blockers": gates.get("open_blockers"),
        "technical_gates_still_required": gates.get("technical_gates_still_required"),
        "visible_ui_status": visible.get("status"),
        "visible_issue_count": visible.get("visible_issue_count"),
        "github_render_status": gh_render.get("status"),
        "autopilot_status": board.get("status"),
        "before": before,
        "after": after,
        "commands": results,
        "blocked_reasons": [],
    }
    if gates.get("trade_ready") is not True:
        payload["blocked_reasons"].append("technical trade_ready gates are not all PASS")
    if visible.get("status") != "PASS":
        payload["blocked_reasons"].append("automated dashboard visual proof is not PASS")
    if gh_render.get("status") != "PASS":
        payload["blocked_reasons"].append("GitHub plus Render failure tracker is not PASS")
    if board.get("status") != "PASS":
        payload["blocked_reasons"].append("autopilot proof board is not PASS")

    (OUT / "summary.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    lines = [
        "# System3 Safe Repair Runner",
        "",
        f"Generated UTC: `{payload['generated_utc']}`",
        f"Status: **{payload['status']}**",
        f"API base: `{API_BASE}`",
        "",
        "## Safety",
        "",
        "- live_trading_enabled: `false`",
        "- system_ready_for_live_trading: `false`",
        "- order_routes_called: `false`",
        "- secrets_printed: `false`",
        "",
        "## Gate summary",
        "",
        f"- Gates: `{payload['gates_passing']}/{payload['gates_total']}`",
        f"- Trade ready: `{payload['trade_ready']}`",
        f"- Analyzer ready: `{payload['analyzer_ready']}`",
        f"- Open blockers: `{payload['open_blockers']}`",
        f"- Technical gates still required: `{payload['technical_gates_still_required']}`",
        "",
        "## Proof summary",
        "",
        f"- Visible UI status: `{payload['visible_ui_status']}`",
        f"- Visible issue count: `{payload['visible_issue_count']}`",
        f"- GitHub/Render status: `{payload['github_render_status']}`",
        f"- Autopilot status: `{payload['autopilot_status']}`",
        "",
        "## Blocked reasons",
        "",
    ]
    lines += [f"- [ ] {x}" for x in payload["blocked_reasons"]] or ["- [x] none"]
    lines += ["", "## Endpoints after run", "", "| Endpoint | OK | Status |", "|---|---:|---:|"]
    for r in after:
        lines.append(f"| `{r.get('endpoint')}` | `{r.get('ok')}` | `{r.get('status')}` |")
    lines += ["", "## Commands", "", "| Command | PASS |", "|---|---:|"]
    for r in results:
        cmd = " ".join(str(x) for x in r.get("cmd") or [])
        lines.append(f"| `{cmd}` | `{r.get('passed')}` |")
    (OUT / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2)[:12000])
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
