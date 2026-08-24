#!/usr/bin/env python3
"""Evaluate Dhan rotator reliability from the sanitized full-cloud audit.

This is a read-only evidence gate. A healthy broker session does not erase recent
rotation failures. Conversely, audit-wide log-category counts are not attributed
to the bounded recent execution window and therefore cannot by themselves turn
successful recent executions into a reliability failure.

No secret payload or broker order endpoint is accessed.
"""
from __future__ import annotations

import json
import os
from collections import Counter
from pathlib import Path
from typing import Any

SOURCE = Path(os.getenv("SYSTEM3_CLOUD_AUDIT_JSON", "reports/latest/full_cloud_audit/full_cloud_audit.json"))
OUT = Path(os.getenv("SYSTEM3_ROTATOR_RELIABILITY_DIR", "reports/latest/rotator_reliability"))
WINDOW = max(3, min(20, int(os.getenv("SYSTEM3_ROTATOR_RELIABILITY_WINDOW", "10"))))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    try:
        audit = json.loads(SOURCE.read_text(encoding="utf-8"))
    except Exception as exc:
        report = {"state": "NOT_PROVEN", "error": type(exc).__name__, "secret_payloads_accessed": False}
        (OUT / "rotator_reliability.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        return 2

    rotator = audit.get("rotator") or {}
    rows = [r for r in (rotator.get("recent_executions") or []) if isinstance(r, dict)][:WINDOW]
    failed = [r for r in rows if int(r.get("failedCount") or 0) > 0]
    succeeded = [r for r in rows if int(r.get("succeededCount") or 0) > 0]
    terminal = len(failed) + len(succeeded)
    success_rate = (len(succeeded) / terminal) if terminal else None
    creators = Counter(str(r.get("creator") or "UNKNOWN") for r in rows)
    log_cats = (((audit.get("logs") or {}).get("rotator_job") or {}).get("categories") or {})

    # The full-cloud audit currently aggregates rotator log categories over a
    # broader 7-day/500-entry query. Those counts do not carry execution-name
    # attribution, so using them as blockers creates false failures when the
    # bounded recent execution window is 100% successful. Preserve the counts
    # as diagnostics until an execution-attributed log contract is available.
    audit_wide_log_diagnostics = {
        "dhan_auth": int(log_cats.get("dhan_auth") or 0),
        "timeout": int(log_cats.get("timeout") or 0),
        "restart_or_crash": int(log_cats.get("restart_or_crash") or 0),
        "rate_limit_text": int(log_cats.get("rate_limit_text") or 0),
    }

    blockers: list[str] = []
    if not (rotator.get("job_read_ok") and rotator.get("scheduler_read_ok") and rotator.get("execution_list_read_ok")):
        blockers.append("rotator_metadata_not_proven")
    if terminal < 3:
        blockers.append("insufficient_terminal_execution_sample")
    if failed:
        blockers.append(f"recent_failed_executions={len(failed)}")

    state = "PASS" if not blockers else "FAIL"
    report: dict[str, Any] = {
        "schema": "genesis-system3-rotator-reliability-v2",
        "state": state,
        "window": WINDOW,
        "executions_examined": len(rows),
        "terminal_executions": terminal,
        "failed_executions": len(failed),
        "succeeded_executions": len(succeeded),
        "success_rate": round(success_rate, 4) if success_rate is not None else None,
        "creator_counts": dict(creators),
        "failed_execution_names": [str(r.get("name")) for r in failed],
        "latest_execution": rows[0].get("name") if rows else None,
        "latest_execution_failed": bool(rows and int(rows[0].get("failedCount") or 0) > 0),
        "audit_wide_log_diagnostics": audit_wide_log_diagnostics,
        "log_scope": "audit_wide_unattributed_to_recent_execution_window",
        "log_signatures_block_reliability": False,
        "blockers": blockers,
        "broker_health_is_not_rotator_reliability": True,
        "secret_payloads_accessed": False,
        "order_actions_performed": False,
        "live_trading_enabled": False,
    }
    (OUT / "rotator_reliability.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md = [
        "# Dhan Rotator Reliability", "", f"State: **{state}**", "",
        f"- Window: `{WINDOW}`", f"- Terminal executions: `{terminal}`",
        f"- Successes: `{len(succeeded)}`", f"- Failures: `{len(failed)}`",
        f"- Success rate: `{report['success_rate']}`", f"- Creators: `{dict(creators)}`", "",
        "## Blockers", "",
    ]
    md += [f"- {b}" for b in blockers] or ["- none"]
    md += [
        "", "## Audit-wide log diagnostics (non-blocking until execution-attributed)", "",
        *[f"- {k}: `{v}`" for k, v in audit_wide_log_diagnostics.items()],
        "", "Broker health does not override rotator reliability. LIVE remains OFF/LOCKED.", "",
    ]
    (OUT / "rotator_reliability.md").write_text("\n".join(md), encoding="utf-8")
    print("ROTATOR_RELIABILITY " + json.dumps({
        "state": state,
        "success_rate": report["success_rate"],
        "failures": len(failed),
        "blockers": blockers,
        "audit_wide_log_diagnostics": audit_wide_log_diagnostics,
    }, sort_keys=True))
    return 0 if state == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
