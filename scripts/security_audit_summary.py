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
    return {"state": state, "counts": counts}


def _pip(data: Any | None, err: str | None) -> dict[str, Any]:
    if err or not isinstance(data, list):
        return {"state": "NOT_PROVEN", "error": err or "invalid_json"}
    vuln_count = 0
    vulnerable_packages = 0
    ids: list[str] = []
    for dep in data:
        vulns = dep.get("vulns") or [] if isinstance(dep, dict) else []
        if vulns:
            vulnerable_packages += 1
        vuln_count += len(vulns)
        for vuln in vulns:
            if isinstance(vuln, dict) and vuln.get("id"):
                ids.append(str(vuln["id"]))
    return {
        "state": "FAIL" if vuln_count else "PASS",
        "vulnerability_count": vuln_count,
        "vulnerable_packages": vulnerable_packages,
        "ids": sorted(set(ids))[:100],
    }


def _bandit(data: Any | None, err: str | None) -> dict[str, Any]:
    if err or not isinstance(data, dict):
        return {"state": "NOT_PROVEN", "error": err or "invalid_json"}
    results = data.get("results") or []
    counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    for row in results:
        sev = str((row or {}).get("issue_severity") or "").upper()
        if sev in counts:
            counts[sev] += 1
    if counts["HIGH"]:
        state = "FAIL"
    elif counts["MEDIUM"] or counts["LOW"]:
        state = "WARN"
    else:
        state = "PASS"
    return {"state": state, "counts": counts, "finding_count": len(results)}


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
        lines.append(f"| `{name}` | **{row.get('state')}** | `{detail[:500]}` |")
    lines += [
        "",
        "Safety: ANALYZER/PAPER audit only; no order endpoint invoked; no secret payload stored.",
    ]
    (out / "security_audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"state": overall, "hard_failures": hard_fail}, sort_keys=True))
    return 0 if overall == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
