#!/usr/bin/env python3
"""
System3 Secure Install + Credential Audit

Purpose:
- Verify dependency/install readiness.
- Verify required credential presence/format through secure env only.
- Never print secret values.
- Never call live order routes.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "latest" / "secure_install_credential_audit"

REQUIRED_SECRET_NAMES = [
    "DASHBOARD_API_KEY",
    "DHAN_CLIENT_ID",
    "DHAN_ACCESS_TOKEN",
]
OPTIONAL_SECRET_NAMES = [
    "DHAN_PIN",
    "DHAN_TOTP_SECRET",
    "WORKER_PUSH_TOKEN",
]

PY_IMPORTS = [
    "fastapi",
    "pydantic",
    "requests",
    "pytz",
]


def run(cmd: List[str], timeout: int = 45) -> Dict:
    try:
        p = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=timeout)
        return {
            "cmd": " ".join(cmd),
            "returncode": p.returncode,
            "ok": p.returncode == 0,
            "stdout_tail": p.stdout[-2000:],
            "stderr_tail": p.stderr[-2000:],
        }
    except Exception as exc:
        return {"cmd": " ".join(cmd), "ok": False, "error": f"{type(exc).__name__}: {str(exc)[:300]}"}


def secret_status(name: str) -> Dict:
    val = os.environ.get(name, "")
    present = bool(val)
    status = {
        "name": name,
        "present": present,
        "length": len(val) if present else 0,
        "format_warnings": [],
    }
    if present:
        if val.strip() != val:
            status["format_warnings"].append("leading_or_trailing_spaces")
        if name.endswith("TOKEN") and val.lower().startswith("bearer "):
            status["format_warnings"].append("has_bearer_prefix")
        if name in {"DHAN_ACCESS_TOKEN", "DASHBOARD_API_KEY"} and len(val) < 10:
            status["format_warnings"].append("suspiciously_short")
    return status


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    blockers: List[str] = []
    findings: List[str] = []
    todo: List[str] = []

    py = shutil.which("python") or sys.executable
    node = shutil.which("node")
    npm = shutil.which("npm")

    checks = {
        "python_path": py,
        "node_path": node,
        "npm_path": npm,
        "requirements_txt_exists": (ROOT / "requirements.txt").exists(),
        "package_json_exists": (ROOT / "dashboard" / "frontend" / "package.json").exists() or (ROOT / "package.json").exists(),
    }

    if py:
        findings.append("Python executable found.")
    else:
        blockers.append("Python executable not found.")
        todo.append("Install/setup Python in workflow/runtime.")
    if not node:
        blockers.append("Node executable not found.")
        todo.append("Install/setup Node for dashboard visual proof workflows.")
    else:
        findings.append("Node executable found.")

    import_results = []
    for mod in PY_IMPORTS:
        r = run([py, "-c", f"import {mod}; print('{mod}:OK')"], timeout=20) if py else {"ok": False, "error": "python_missing"}
        r["module"] = mod
        import_results.append(r)
        if not r.get("ok"):
            blockers.append(f"Python import failed: {mod}")
            todo.append(f"Install/fix Python dependency: {mod}")

    compile_targets = [
        "tools/system3_parallel_root_cause_audit.py",
        "tools/system3_workflow_failure_tracker.py",
        "tools/system3_todo_status_updater.py",
        "tools/system3_secure_install_credential_audit.py",
        "dashboard/backend/app.py",
    ]
    compile_results = []
    for rel in compile_targets:
        path = ROOT / rel
        if path.exists():
            r = run([py, "-m", "py_compile", rel], timeout=30) if py else {"ok": False, "error": "python_missing"}
            r["file"] = rel
            compile_results.append(r)
            if not r.get("ok"):
                blockers.append(f"Python compile failed: {rel}")
                todo.append(f"Fix Python compile error in {rel}")
        else:
            blockers.append(f"Expected audit/code file missing: {rel}")
            todo.append(f"Restore missing file: {rel}")

    required_secrets = [secret_status(x) for x in REQUIRED_SECRET_NAMES]
    optional_secrets = [secret_status(x) for x in OPTIONAL_SECRET_NAMES]
    for s in required_secrets:
        if not s["present"]:
            blockers.append(f"Required secret missing from workflow env: {s['name']}")
            todo.append(f"Add/verify required secret in secure store: {s['name']}")
        if s["format_warnings"]:
            blockers.append(f"Required secret format warning: {s['name']} -> {','.join(s['format_warnings'])}")
            todo.append(f"Fix secret format in secure store: {s['name']}")

    live_flags = {
        "LIVE_TRADING_ENABLED": os.environ.get("LIVE_TRADING_ENABLED", "0"),
        "SYSTEM3_LIVE_TRADING_ALLOWED": os.environ.get("SYSTEM3_LIVE_TRADING_ALLOWED", "0"),
        "ANALYZE_MODE": os.environ.get("ANALYZE_MODE", "1"),
    }
    if str(live_flags["LIVE_TRADING_ENABLED"]) not in {"0", "false", "False", ""}:
        blockers.append("LIVE_TRADING_ENABLED is not safely OFF in audit env.")
    if str(live_flags["SYSTEM3_LIVE_TRADING_ALLOWED"]) not in {"0", "false", "False", ""}:
        blockers.append("SYSTEM3_LIVE_TRADING_ALLOWED is not safely OFF in audit env.")

    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not blockers else "BLOCKED",
        "blocker_count": len(blockers),
        "blockers": blockers,
        "todo": todo,
        "findings": findings,
        "checks": checks,
        "python_import_results": import_results,
        "python_compile_results": compile_results,
        "required_secrets_redacted": required_secrets,
        "optional_secrets_redacted": optional_secrets,
        "live_safety_flags": live_flags,
        "secrets_printed": False,
        "live_order_routes_called": False,
        "production_grade_claim_allowed": False,
    }
    (OUT / "summary.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    md = [
        "# System3 Secure Install + Credential Audit",
        "",
        f"Generated UTC: `{payload['generated_utc']}`",
        f"Status: **{payload['status']}**",
        f"Blockers: `{payload['blocker_count']}`",
        "",
        "## Safety",
        "",
        "- Secrets printed: `false`",
        "- Live order routes called: `false`",
        "- Live trading remains blocked in audit env.",
        "",
        "## Blockers",
        "",
    ]
    md += [f"- {x}" for x in blockers] or ["- none"]
    md += ["", "## TODO", ""]
    md += [f"- [ ] {x}" for x in todo] or ["- [x] none"]
    md += ["", "## Required secrets redacted status", "", "| Secret | Present | Length | Format warnings |", "|---|---:|---:|---|"]
    for s in required_secrets + optional_secrets:
        md.append(f"| {s['name']} | {s['present']} | {s['length']} | {', '.join(s['format_warnings']) or '-'} |")
    (OUT / "summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps(payload, indent=2))
    return 0 if not blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
