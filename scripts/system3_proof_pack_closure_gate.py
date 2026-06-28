#!/usr/bin/env python3
"""System3 proof-pack closure gate.

Purpose
-------
Reads reports/latest proof artifacts and creates a deterministic closure report
for the exact blockers seen in proof pack 534. It does not log in to any broker,
does not place orders, does not read secrets, and does not enable live trading.

The gate separates:
- code/proof gaps that can be resolved by CI/local proof scripts, and
- manual runtime gaps that require a secure broker-enabled laptop/runtime.

Exit codes:
- 0: repository proof infrastructure is safe and closure report was written.
- 2: a safety invariant is broken.
- 3: required proof artifacts are missing or malformed.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports" / "latest"
OUT = REPORTS / "proof_pack_closure_gate"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(rel_path: str) -> dict[str, Any] | None:
    path = ROOT / rel_path
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as exc:
        return {"_json_error": repr(exc), "_path": rel_path}
    return data if isinstance(data, dict) else {"_json_error": "not_a_json_object", "_path": rel_path}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def safety_flags() -> dict[str, Any]:
    live_enabled_raw = os.environ.get("LIVE_TRADING_ENABLED", "0")
    live_allowed_raw = os.environ.get("SYSTEM3_LIVE_TRADING_ALLOWED", "0")
    analyze_raw = os.environ.get("ANALYZE_MODE", "1")
    live_enabled = live_enabled_raw not in {"", "0", "false", "False", "FALSE"}
    live_allowed = live_allowed_raw not in {"", "0", "false", "False", "FALSE"}
    analyze_mode = analyze_raw not in {"", "0", "false", "False", "FALSE"}
    return {
        "LIVE_TRADING_ENABLED": live_enabled_raw,
        "SYSTEM3_LIVE_TRADING_ALLOWED": live_allowed_raw,
        "ANALYZE_MODE": analyze_raw,
        "live_trading_enabled_truthy": live_enabled,
        "live_trading_allowed_truthy": live_allowed,
        "analyze_mode_truthy": analyze_mode,
        "safe": (not live_enabled and not live_allowed and analyze_mode),
    }


def bool_path(data: dict[str, Any] | None, *keys: str) -> bool | None:
    cur: Any = data
    for key in keys:
        if not isinstance(cur, dict) or key not in cur:
            return None
        cur = cur[key]
    return cur if isinstance(cur, bool) else None


def list_warnings(data: dict[str, Any] | None) -> list[str]:
    warnings = data.get("warnings") if isinstance(data, dict) else None
    return warnings if isinstance(warnings, list) else []


def main() -> int:
    flags = safety_flags()
    if not flags["safe"]:
        OUT.mkdir(parents=True, exist_ok=True)
        write_json(
            OUT / "summary.json",
            {
                "generated_utc": utc_now(),
                "status": "FAIL",
                "reason": "live_trading_safety_flags_not_safe",
                "safety_flags": flags,
            },
        )
        print("FAIL: live trading safety flags are not safe", file=sys.stderr)
        return 2

    required = {
        "pipeline": "reports/latest/full_trading_pipeline_readiness/09_pipeline_gate_summary.json",
        "matrix": "reports/latest/proof_status_matrix/proof_status_matrix.json",
        "blockers": "reports/latest/auto_recovery_blockers/auto_recovery_blockers.json",
        "lifecycle": "reports/latest/analyzer_paper_lifecycle_proof/summary.json",
        "dashboard_truth": "reports/latest/dashboard_truth_proof/summary.json",
        "dashboard_browser": "reports/latest/dashboard_browser_proof/summary.json",
        "endpoint_coverage": "reports/latest/dashboard_endpoint_coverage/endpoint_coverage_summary.json",
        "broker_validation": "reports/latest/broker_trader_validation/summary.json",
        "real_market_data": "reports/latest/real_market_data_proof/summary.json",
        "expectancy": "reports/latest/friction_expectancy/summary.json",
    }
    loaded = {name: load_json(path) for name, path in required.items()}
    missing = [path for name, path in required.items() if loaded[name] is None]
    malformed = [path for name, path in required.items() if isinstance(loaded[name], dict) and "_json_error" in loaded[name]]

    lifecycle = loaded["lifecycle"]
    lifecycle_ev = lifecycle.get("evidence", {}) if isinstance(lifecycle, dict) else {}
    lifecycle_real_market_proven = (
        isinstance(lifecycle, dict)
        and lifecycle.get("pass") is True
        and lifecycle_ev.get("dry_run") is False
        and lifecycle_ev.get("broker_connected") is True
        and lifecycle_ev.get("orders_trades_lifecycle_reconciled") is True
    )

    dashboard_browser = loaded["dashboard_browser"]
    dashboard_truth = loaded["dashboard_truth"]
    endpoint_coverage = loaded["endpoint_coverage"]
    browser_visual_proven = bool_path(dashboard_browser, "pass") is True or bool_path(dashboard_browser, "success") is True
    endpoint_coverage_complete = bool_path(endpoint_coverage, "endpoint_coverage_complete") is True
    dashboard_truth_closed = bool_path(dashboard_truth, "pass") is True and browser_visual_proven and endpoint_coverage_complete

    broker_validation = loaded["broker_validation"]
    broker_connected = bool_path(broker_validation, "broker_connected") is True
    broker_manual_required = not broker_connected

    expectancy = loaded["expectancy"]
    expectancy_real_backtest_done = isinstance(expectancy, dict) and expectancy.get("backtest_status") not in {None, "PENDING_LAPTOP_RUN"}

    closure_items = [
        {
            "blocker": "live_market_analyzer_paper_trade_not_proven",
            "status": "CLOSED" if lifecycle_real_market_proven else "MANUAL_RUNTIME_PROOF_REQUIRED",
            "safe_to_auto_fix": False,
            "why": "Requires market-day broker-connected analyzer/paper lifecycle with reconciled order/fill/exit/PnL proof.",
        },
        {
            "blocker": "full_signal_to_exit_pnl_lifecycle_not_proven",
            "status": "CLOSED" if lifecycle_real_market_proven else "MANUAL_RUNTIME_PROOF_REQUIRED",
            "safe_to_auto_fix": False,
            "why": "Cannot be honestly closed from dry-run or broker-offline CI evidence.",
        },
        {
            "blocker": "lifecycle_proof_broker_not_connected",
            "status": "CLOSED" if broker_connected else "MANUAL_BROKER_LOGIN_REQUIRED",
            "safe_to_auto_fix": False,
            "why": "Broker session/secrets must stay outside repo and CI logs.",
        },
        {
            "blocker": "browser_screenshot_truth_not_proven_in_ci",
            "status": "CLOSED" if dashboard_truth_closed else "PROOF_REQUIRED",
            "safe_to_auto_fix": True,
            "why": "Can be closed by generating dashboard browser proof and endpoint coverage artifacts in CI/local runner.",
        },
        {
            "blocker": "positive_costed_expectancy_not_proven",
            "status": "CLOSED" if expectancy_real_backtest_done else "LAPTOP_BHAVCOPY_RUN_REQUIRED",
            "safe_to_auto_fix": False,
            "why": "Requires real bhavcopy/costed backtest evidence; seed estimates do not prove edge.",
        },
    ]

    open_items = [item for item in closure_items if item["status"] != "CLOSED"]
    auto_closed = [item for item in closure_items if item["status"] == "CLOSED" and item["safe_to_auto_fix"]]
    manual_required = [item for item in open_items if not item["safe_to_auto_fix"]]

    summary = {
        "generated_utc": utc_now(),
        "status": "PASS_WITH_MANUAL_RUNTIME_ITEMS" if not missing and not malformed else "FAIL",
        "mode": "ANALYZER_PAPER_ONLY",
        "live_trading_enabled": False,
        "trade_ready": False,
        "safety_flags": flags,
        "required_artifacts": required,
        "missing_required_artifacts": missing,
        "malformed_required_artifacts": malformed,
        "closure_items": closure_items,
        "open_item_count": len(open_items),
        "auto_closed_count": len(auto_closed),
        "manual_runtime_required_count": len(manual_required),
        "broker_manual_required": broker_manual_required,
        "final_verdict": (
            "ARTIFACTS_MISSING_OR_MALFORMED"
            if missing or malformed
            else (
                "PROOF_INFRASTRUCTURE_READY_MANUAL_RUNTIME_PROOF_REQUIRED"
                if open_items
                else "ALL_PROOF_PACK_BLOCKERS_CLOSED_ANALYZER_ONLY"
            )
        ),
        "next_safe_command": "python scripts/paper_lifecycle_proof.py --force on broker-enabled market-day runtime; then run python scripts/system3_master_proof_orchestrator.py",
    }

    OUT.mkdir(parents=True, exist_ok=True)
    write_json(OUT / "summary.json", summary)

    md = [
        "# System3 Proof Pack Closure Gate",
        "",
        f"Generated UTC: `{summary['generated_utc']}`",
        "",
        f"- Status: `{summary['status']}`",
        f"- Final verdict: `{summary['final_verdict']}`",
        "- Live trading enabled: `False`",
        "- Trade ready: `False`",
        "",
        "## Closure items",
        "",
        "| Blocker | Status | Auto-fix safe | Why |",
        "|---|---|---:|---|",
    ]
    for item in closure_items:
        md.append(f"| `{item['blocker']}` | `{item['status']}` | `{item['safe_to_auto_fix']}` | {item['why']} |")
    md.extend(
        [
            "",
            "## Safe next command",
            "",
            "```powershell",
            "cd C:\\System3\\Genesis_System3",
            "$env:LIVE_TRADING_ENABLED='0'",
            "$env:SYSTEM3_LIVE_TRADING_ALLOWED='0'",
            "$env:ANALYZE_MODE='1'",
            "python scripts/paper_lifecycle_proof.py --force",
            "python scripts/system3_master_proof_orchestrator.py",
            "python scripts/system3_proof_pack_closure_gate.py",
            "```",
            "",
        ]
    )
    (OUT / "README.md").write_text("\n".join(md), encoding="utf-8")

    print(json.dumps({"status": summary["status"], "final_verdict": summary["final_verdict"], "open_item_count": len(open_items)}, indent=2))
    return 3 if missing or malformed else 0


if __name__ == "__main__":
    raise SystemExit(main())
