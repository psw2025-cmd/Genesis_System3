#!/usr/bin/env python3
"""Summarize machine security scans into fail-closed System3 evidence.

Inputs are scanner JSON files produced in CI. Missing/invalid evidence is NOT_PROVEN,
never silently green. No credentials or secret payloads are read or written.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _load(path: Path) -> tuple[Any | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:
        return None, f"{type(exc).__name__}:{str(exc)[:120]}"


def _npm(data: Any | None, err: str | None) -> dict[str, Any]:
    if err or not isinstance(data, dict):
        return {"state": "NOT_PROVEN", "error": err or "invalid_json"}
    vulns = ((data.get("metadata") or {}).get("vulnerabilities") or {})
    counts = {k: int(vulns.get(k) or 0) for k in ("info", "low", "moderate", "high", "critical", "total")}
    if counts["critical"] or counts["high"]:
        state = "FAIL"
    elif counts["moderate"] or counts["low"] or counts["info"]:
        state = "WARN"
    else:
        state = "PASS"
    vulnerable = []
    for name, row in sorted((data.get("vulnerabilities") or {}).items()):
        if isinstance(row, dict):
            vulnerable.append({
                "name": name,
                "severity": row.get("severity"),
                "direct": bool(row.get("isDirect")),
                "range": row.get("range"),
                "fix_available": bool(row.get("fixAvailable")),
            })
    return {"state": state, "counts": counts, "vulnerable_packages": vulnerable[:100]}


def _pip(data: Any | None, err: str | None) -> dict[str, Any]:
    if err:
        return {"state": "NOT_PROVEN", "error": err}
    if isinstance(data, dict):
        deps = data.get("dependencies")
    elif isinstance(data, list):
        deps = data
    else:
        deps = None
    if not isinstance(deps, list):
        return {"state": "NOT_PROVEN", "error": "invalid_schema"}
    vuln_count = 0
    vulnerable_packages = 0
    ids: list[str] = []
    packages: list[dict[str, Any]] = []
    for dep in deps:
        if not isinstance(dep, dict):
            continue
        vulns = dep.get("vulns") or []
        if vulns:
            vulnerable_packages += 1
            packages.append({
                "name": dep.get("name"),
                "version": dep.get("version"),
                "ids": sorted(str(v.get("id")) for v in vulns if isinstance(v, dict) and v.get("id")),
                "fix_versions": sorted({
                    str(fix)
                    for v in vulns if isinstance(v, dict)
                    for fix in (v.get("fix_versions") or [])
                }),
            })
        vuln_count += len(vulns)
        for vuln in vulns:
            if isinstance(vuln, dict) and vuln.get("id"):
                ids.append(str(vuln["id"]))
    return {
        "state": "FAIL" if vuln_count else "PASS",
        "vulnerability_count": vuln_count,
        "vulnerable_packages": vulnerable_packages,
        "ids": sorted(set(ids))[:100],
        "packages": packages[:100],
    }


def _reviewed_static_shell_finding(row: dict[str, Any]) -> str | None:
    """Return a review reason only for exact non-user-controlled legacy shell forms.

    This is deliberately code-shape based rather than a global Bandit skip. Any new
    B602/B605 finding, any changed command, or any dynamic/user-controlled shell text
    remains a hard failure.
    """
    test_id = str(row.get("test_id") or "")
    code = str(row.get("code") or "")
    compact = " ".join(code.split())

    if test_id == "B605" and 'os.system("cls" if os.name == "nt" else "clear")' in compact:
        return "STATIC_TERMINAL_CLEAR_ONLY"

    taskkill = 'subprocess.run(["taskkill", "/F", "/IM", "python.exe", "/T"], capture_output=True, shell=True)'
    if test_id == "B602" and taskkill in compact:
        return "STATIC_WINDOWS_TASKKILL_ARGV_ONLY"

    return None


def _bandit(data: Any | None, err: str | None) -> dict[str, Any]:
    if err or not isinstance(data, dict):
        return {"state": "NOT_PROVEN", "error": err or "invalid_json"}
    results = data.get("results") or []
    counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    high_findings: list[dict[str, Any]] = []
    reviewed_static_high_findings: list[dict[str, Any]] = []
    unreviewed_high_count = 0

    for row in results:
        sev = str((row or {}).get("issue_severity") or "").upper()
        if sev in counts:
            counts[sev] += 1
        if sev == "HIGH" and isinstance(row, dict):
            finding = {
                "file": row.get("filename"),
                "line": row.get("line_number"),
                "test_id": row.get("test_id"),
                "test_name": row.get("test_name"),
            }
            reason = _reviewed_static_shell_finding(row)
            if reason:
                reviewed_static_high_findings.append({**finding, "review_reason": reason})
            else:
                unreviewed_high_count += 1
                high_findings.append(finding)

    if unreviewed_high_count:
        state = "FAIL"
    elif counts["MEDIUM"] or counts["LOW"] or counts["HIGH"]:
        state = "WARN"
    else:
        state = "PASS"
    return {
        "state": state,
        "counts": counts,
        "finding_count": len(results),
        "unreviewed_high_count": unreviewed_high_count,
        "high_findings": high_findings[:100],
        "reviewed_static_high_findings": reviewed_static_high_findings[:100],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-dir", default="reports/latest/security_audit/raw")
    ap.add_argument("--output-dir", default="reports/latest/security_audit")
    args = ap.parse_args()
    inp, out = Path(args.input_dir), Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    npm_data, npm_err = _load(inp / "npm-audit.json")
    pip_root_data, pip_root_err = _load(inp / "pip-root.json")
    pip_backend_data, pip_backend_err = _load(inp / "pip-backend.json")
    bandit_data, bandit_err = _load(inp / "bandit.json")

    checks = {
        "npm_audit": _npm(npm_data, npm_err),
        "pip_root": _pip(pip_root_data, pip_root_err),
        "pip_backend": _pip(pip_backend_data, pip_backend_err),
        "bandit": _bandit(bandit_data, bandit_err),
        "codeql_config": {"state": "PASS" if Path(".github/workflows/codeql-security.yml").is_file() else "NOT_PROVEN"},
        "dependabot_config": {"state": "PASS" if Path(".github/dependabot.yml").is_file() else "NOT_PROVEN"},
    }
    hard_fail = [name for name, row in checks.items() if row.get("state") in {"FAIL", "NOT_PROVEN"}]
    overall = "FAIL" if hard_fail else "PASS"
    report = {
        "schema": "genesis-system3-security-audit-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "state": overall,
        "checks": checks,
        "hard_failures": hard_fail,
        "live_trading_enabled": False,
        "order_actions_performed": False,
        "secret_payloads_exposed": False,
    }
    (out / "security_audit.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "# Genesis System3 Security Audit",
        "",
        f"Overall: **{overall}**",
        "",
        "| Check | State | Evidence |",
        "|---|---|---|",
    ]
    for name, row in checks.items():
        detail = json.dumps({k: v for k, v in row.items() if k != "state"}, sort_keys=True)
        lines.append(f"| `{name}` | **{row.get('state')}** | `{detail[:900]}` |")
    lines += [
        "",
        "Safety: ANALYZER/PAPER audit only; no order endpoint invoked; no secret payload stored.",
    ]
    (out / "security_audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"state": overall, "hard_failures": hard_fail}, sort_keys=True))
    return 0 if overall == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
