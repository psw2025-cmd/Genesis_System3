#!/usr/bin/env python3
"""System3 Windows self-hosted full-system proof board.

Produces visible paper/HTML/JSON proof from a Windows self-hosted GitHub runner.
This is proof-only. It never enables live trading and never calls order routes.
"""
from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "latest" / "windows_self_hosted_full_system_proof"
BASE_URL = os.environ.get("DASHBOARD_BASE_URL") or os.environ.get("SYSTEM3_API_BASE") or "https://genesis-system3-backend.onrender.com"
BASE_URL = BASE_URL.rstrip("/")

PROOF_COMMANDS = [
    [sys.executable, "scripts/system3_gate_evaluator.py", "--sync-gates"],
    [sys.executable, "tools/system3_auto_coordinator.py", "--full"],
    [sys.executable, "tools/system3_github_render_failure_tracker.py"],
    [sys.executable, "tools/dashboard_visible_issue_tracker.mjs"],
    [sys.executable, "tools/system3_autopilot_proof_board.py"],
]

HTTP_ENDPOINTS = [
    "/api/health",
    "/api/state",
    "/api/status",
    "/api/broker/status",
    "/api/broker/dhan/status",
    "/api/broker/funds",
    "/api/broker/holdings",
    "/api/broker/positions",
    "/api/scanner/top_contract_gainers",
    "/api/simulation/live/state",
]

REPORTS = {
    "system3_auto_gates": ROOT / "reports/latest/system3_auto_gates/summary.json",
    "github_render_failure_tracker": ROOT / "reports/latest/github_render_failure_tracker/summary.json",
    "dashboard_visible_issue_tracker": ROOT / "reports/latest/dashboard_visible_issue_tracker/summary.json",
    "autopilot_proof_board": ROOT / "reports/latest/system3_autopilot_proof_board/summary.json",
    "safe_repair_runner": ROOT / "reports/latest/safe_repair_runner/summary.json",
    "market_session_proof_runner": ROOT / "reports/latest/market_session_proof_runner/summary.json",
}


def utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def ensure_safety_env() -> None:
    os.environ["LIVE_TRADING_ENABLED"] = "0"
    os.environ["SYSTEM3_LIVE_TRADING_ALLOWED"] = "0"
    os.environ["ANALYZE_MODE"] = "1"


def run_command(cmd: List[str], timeout: int = 240) -> Dict[str, Any]:
    started = time.time()
    result: Dict[str, Any] = {"cmd": cmd, "started_utc": utc()}
    try:
        if cmd[0].endswith("node") or cmd[0] == "node":
            actual = cmd
        elif cmd[1].endswith(".mjs"):
            actual = ["node", cmd[1], *cmd[2:]]
        else:
            actual = cmd
        p = subprocess.run(actual, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        result.update({
            "actual_cmd": actual,
            "returncode": p.returncode,
            "ok": p.returncode == 0,
            "stdout_tail": (p.stdout or "")[-4000:],
            "stderr_tail": (p.stderr or "")[-4000:],
        })
    except FileNotFoundError as exc:
        result.update({"ok": False, "returncode": None, "error": f"missing executable: {exc}"})
    except subprocess.TimeoutExpired as exc:
        result.update({"ok": False, "returncode": None, "error": f"timeout after {timeout}s", "stdout_tail": (exc.stdout or "")[-2000:] if isinstance(exc.stdout, str) else "", "stderr_tail": (exc.stderr or "")[-2000:] if isinstance(exc.stderr, str) else ""})
    except Exception as exc:
        result.update({"ok": False, "returncode": None, "error": str(exc)})
    result["elapsed_sec"] = round(time.time() - started, 2)
    result["finished_utc"] = utc()
    return result


def probe(endpoint: str) -> Dict[str, Any]:
    url = f"{BASE_URL}{endpoint}"
    headers = {"User-Agent": "System3-Windows-SelfHosted-Proof/1.0"}
    key = os.environ.get("DASHBOARD_API_KEY", "").strip()
    if key:
        headers["X-API-Key"] = key
    req = urllib.request.Request(url, headers=headers, method="GET")
    started = time.time()
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:  # nosec B310 - configured dashboard URL
            body = resp.read(2000).decode("utf-8", "replace")
            return {"endpoint": endpoint, "url": url, "ok": 200 <= resp.status < 300, "status": resp.status, "elapsed_sec": round(time.time() - started, 2), "body_preview": body[:1000]}
    except urllib.error.HTTPError as exc:
        preview = ""
        try:
            preview = exc.read(1000).decode("utf-8", "replace")
        except Exception:
            pass
        return {"endpoint": endpoint, "url": url, "ok": False, "status": exc.code, "elapsed_sec": round(time.time() - started, 2), "body_preview": preview}
    except Exception as exc:
        return {"endpoint": endpoint, "url": url, "ok": False, "status": None, "elapsed_sec": round(time.time() - started, 2), "error": str(exc)}


def read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"exists": False, "path": str(path)}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            data["exists"] = True
            data["path"] = str(path)
            return data
        return {"exists": True, "path": str(path), "value": data}
    except Exception as exc:
        return {"exists": True, "path": str(path), "parse_error": str(exc)}


def report_status(name: str, data: Dict[str, Any]) -> str:
    if not data.get("exists"):
        return "MISSING"
    raw = str(data.get("status") or data.get("final_status") or data.get("verdict") or "UNKNOWN").upper()
    if raw in {"PASS", "PASSED", "GREEN", "OK"}:
        return "PASS"
    if raw in {"FAIL", "FAILED", "BLOCKED", "RED", "ERROR"}:
        return "BLOCKED"
    return raw


def build_html(payload: Dict[str, Any]) -> str:
    statuses = payload["status_table"]
    rows = "\n".join(
        f"<tr><td>{r['name']}</td><td class='{r['status'].lower()}'>{r['status']}</td><td>{r.get('detail','')}</td></tr>"
        for r in statuses
    )
    blockers = "".join(f"<li>{b}</li>" for b in payload.get("blockers", [])) or "<li>None</li>"
    endpoints = "\n".join(
        f"<tr><td>{p['endpoint']}</td><td class={'pass' if p.get('ok') else 'blocked'}>{p.get('status')}</td><td>{p.get('elapsed_sec')}</td><td><pre>{(p.get('error') or p.get('body_preview') or '')[:300]}</pre></td></tr>"
        for p in payload.get("http_probes", [])
    )
    return f"""<!doctype html>
<html><head><meta charset='utf-8'><title>System3 Windows Self-Hosted Full Proof</title>
<style>
body{{font-family:Segoe UI,Arial,sans-serif;background:#0f172a;color:#e5e7eb;margin:24px}}
h1{{margin-bottom:4px}} .meta{{color:#94a3b8}} table{{border-collapse:collapse;width:100%;margin:16px 0;background:#111827}}
td,th{{border:1px solid #334155;padding:9px;text-align:left;vertical-align:top}} th{{background:#1e293b}}
.pass{{color:#22c55e;font-weight:800}} .blocked,.fail,.missing{{color:#ef4444;font-weight:800}} .pending,.unknown{{color:#f59e0b;font-weight:800}}
.card{{border:1px solid #334155;border-radius:14px;padding:14px;margin:14px 0;background:#111827}} pre{{white-space:pre-wrap;margin:0;color:#cbd5e1}}
</style></head><body>
<h1>System3 Windows Self-Hosted Full System Proof</h1>
<div class='meta'>Generated: {payload['generated_utc']} | Runner OS: {payload['runner']['platform']} | Base URL: {payload['base_url']}</div>
<div class='card'><b>Final status:</b> <span class='{payload['status'].lower()}'>{payload['status']}</span><br>
<b>Live trading enabled:</b> false | <b>Order routes called:</b> false | <b>Analyzer mode:</b> true</div>
<h2>Status board</h2><table><tr><th>Area</th><th>Status</th><th>Detail</th></tr>{rows}</table>
<h2>Blockers</h2><div class='card'><ul>{blockers}</ul></div>
<h2>HTTP proof probes</h2><table><tr><th>Endpoint</th><th>Status</th><th>Seconds</th><th>Preview</th></tr>{endpoints}</table>
</body></html>"""


def main() -> int:
    ensure_safety_env()
    OUT.mkdir(parents=True, exist_ok=True)

    commands = []
    for cmd in PROOF_COMMANDS:
        if not (ROOT / cmd[1]).exists():
            commands.append({"cmd": cmd, "ok": False, "returncode": None, "error": "script missing"})
            continue
        commands.append(run_command(cmd))

    probes = [probe(e) for e in HTTP_ENDPOINTS]
    reports = {name: read_json(path) for name, path in REPORTS.items()}

    status_table: List[Dict[str, str]] = []
    blockers: List[str] = []

    for item in commands:
        status = "PASS" if item.get("ok") else "BLOCKED"
        name = " ".join(item.get("cmd", []))
        status_table.append({"name": name, "status": status, "detail": item.get("error") or f"rc={item.get('returncode')} elapsed={item.get('elapsed_sec')}s"})
        if status != "PASS":
            blockers.append(f"Command blocked: {name} — {item.get('error') or item.get('stderr_tail') or item.get('returncode')}")

    for item in probes:
        status = "PASS" if item.get("ok") else "BLOCKED"
        status_table.append({"name": f"HTTP {item['endpoint']}", "status": status, "detail": str(item.get("status") or item.get("error") or "")})
        if status != "PASS":
            blockers.append(f"HTTP blocked: {item['endpoint']} — {item.get('status') or item.get('error')}")

    for name, data in reports.items():
        status = report_status(name, data)
        status_table.append({"name": f"Report {name}", "status": status, "detail": str(data.get("path"))})
        if status != "PASS":
            blockers.append(f"Report not PASS: {name} — {status}")

    final = "PASS" if not blockers else "BLOCKED"
    payload = {
        "generated_utc": utc(),
        "status": final,
        "base_url": BASE_URL,
        "runner": {"platform": platform.platform(), "machine": platform.machine(), "python": sys.version.split()[0]},
        "safety": {"live_trading_enabled": False, "system3_live_trading_allowed": False, "analyze_mode": True, "order_routes_called": False},
        "commands": commands,
        "http_probes": probes,
        "reports": reports,
        "status_table": status_table,
        "blockers": blockers,
    }

    (OUT / "summary.json").write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    md_rows = "\n".join(f"| {r['name']} | {r['status']} | {r.get('detail','')} |" for r in status_table)
    md = f"# System3 Windows Self-Hosted Full System Proof\n\nGenerated: `{payload['generated_utc']}`\n\nFinal status: **{final}**\n\nSafety: live trading OFF, analyzer mode ON, order routes not called.\n\n## Status board\n\n| Area | Status | Detail |\n|---|---|---|\n{md_rows}\n\n## Blockers\n\n" + "\n".join(f"- {b}" for b in blockers)
    (OUT / "summary.md").write_text(md, encoding="utf-8")
    (OUT / "index.html").write_text(build_html(payload), encoding="utf-8")
    print(json.dumps({"status": final, "out": str(OUT), "blocker_count": len(blockers)}, indent=2))
    return 0 if final == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
