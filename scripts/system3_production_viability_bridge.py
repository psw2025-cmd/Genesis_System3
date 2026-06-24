#!/usr/bin/env python3
"""System3 Production Viability Bridge.

Builds production-grade blocker reports from available live truth bridge and proof files.
Read-only. No secrets. No orders. No live trading.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

TRUTH_BRIDGE = Path("reports/latest/system3_truth_bridge/latest.json")
OUT_DIR = Path("reports/latest/production_viability_bridge")

INPUTS = {
    "pipeline": Path("reports/latest/full_trading_pipeline_readiness/09_pipeline_gate_summary.json"),
    "proof_matrix": Path("reports/latest/proof_status_matrix/proof_status_matrix.json"),
    "lifecycle_summary": Path("reports/latest/analyzer_paper_lifecycle_proof/summary.json"),
    "lifecycle_raw": Path("reports/latest/analyzer_paper_lifecycle_proof/LIFECYCLE_20260614_142129.json"),
    "fresh_data": Path("reports/latest/fresh_data_automation_proof/summary.json"),
    "model": Path("reports/latest/model_training_load_proof/summary.json"),
    "dashboard_truth": Path("reports/latest/dashboard_truth_proof/summary.json"),
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"_ok": False, "_missing": True, "_path": str(path)}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"_ok": False, "_path": str(path), "_error": f"{type(exc).__name__}: {exc}"}


def add(items: List[Dict[str, Any]], severity: str, code: str, message: str, proof=None, action=""):
    items.append({"severity": severity, "code": code, "message": message, "proof": proof or {}, "action": action})


def sev_counts(items: List[Dict[str, Any]]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for item in items:
        out[item["severity"]] = out.get(item["severity"], 0) + 1
    return out


def highest(items: List[Dict[str, Any]]) -> str:
    order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
    if not items:
        return "NONE"
    return max((i["severity"] for i in items), key=lambda x: order.get(x, 0))


def analyze(truth: Dict[str, Any], inputs: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    blockers: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []

    live = truth.get("live", {}) if isinstance(truth, dict) else {}
    state = live.get("state", {}).get("data", {}) if live.get("state", {}).get("ok") else {}
    health = live.get("health", {}).get("data", {}) if live.get("health", {}).get("ok") else {}

    pipeline = inputs.get("pipeline", {})
    matrix = inputs.get("proof_matrix", {})
    lifecycle = inputs.get("lifecycle_summary", {})
    lifecycle_evidence = lifecycle.get("evidence", {}) if isinstance(lifecycle.get("evidence"), dict) else {}
    lifecycle_raw = inputs.get("lifecycle_raw", {})
    fresh = inputs.get("fresh_data", {})
    fresh_ev = fresh.get("evidence", {}) if isinstance(fresh.get("evidence"), dict) else {}
    model = inputs.get("model", {})
    model_ev = model.get("evidence", {}) if isinstance(model.get("evidence"), dict) else {}
    dash = inputs.get("dashboard_truth", {})
    dash_ev = dash.get("evidence", {}) if isinstance(dash.get("evidence"), dict) else {}

    if pipeline.get("trade_ready") is not True:
        add(
            blockers,
            "CRITICAL",
            "TRADE_READY_FALSE",
            "Full pipeline readiness is false.",
            {"verdict": pipeline.get("verdict"), "blockers": pipeline.get("blockers")},
            "Keep live disabled; clear pipeline blockers.",
        )

    if (
        lifecycle_evidence.get("full_lifecycle_proven") is not True
        or lifecycle_evidence.get("lifecycle_proof_dry_run") is True
    ):
        add(
            blockers,
            "CRITICAL",
            "REAL_MARKET_PAPER_LIFECYCLE_MISSING",
            "Real market paper lifecycle is not proven.",
            lifecycle_evidence,
            "Run market-session analyzer paper lifecycle proof.",
        )

    if (
        lifecycle_raw.get("dry_run") is True
        or lifecycle_raw.get("signal", {}).get("instrument_token") == "DRY_RUN_TOKEN"
    ):
        add(
            blockers,
            "CRITICAL",
            "RAW_LIFECYCLE_DRY_RUN",
            "Raw lifecycle proof is simulation/dry-run.",
            {
                "market_status": lifecycle_raw.get("market_status"),
                "instrument_token": lifecycle_raw.get("signal", {}).get("instrument_token"),
            },
            "Do not mark production ready from dry-run proof.",
        )

    if fresh_ev.get("fresh_broker_live_data_proven") is not True:
        add(
            blockers,
            "HIGH",
            "FRESH_BROKER_DATA_NOT_PROVEN",
            "Fresh broker live data proof is missing.",
            {"reason": fresh_ev.get("reason_fresh_broker_live_data_not_proven")},
            "Run secure runtime broker freshness proof.",
        )

    if model_ev.get("promotion_allowed") is not True:
        add(
            blockers,
            "HIGH",
            "MODEL_PROMOTION_BLOCKED",
            "Model promotion is blocked.",
            {"promotion_allowed": model_ev.get("promotion_allowed")},
            "Require policy + validation proof before promotion.",
        )

    if dash_ev.get("browser_visual_truth_proven") is not True:
        add(
            warnings,
            "MEDIUM",
            "BROWSER_TRUTH_NOT_PROVEN",
            "Browser screenshot truth is not proven.",
            {},
            "Run browser screenshot proof.",
        )
    if dash_ev.get("api_db_report_reconciliation_proven") is not True:
        add(
            warnings,
            "MEDIUM",
            "API_DB_REPORT_RECON_NOT_PROVEN",
            "API/DB/report reconciliation is not proven.",
            {},
            "Run dashboard truth reconciliation.",
        )

    # WebSocket/tick health gate: block production until explicit proof file exists and passes.
    tick_health_path = Path("reports/latest/websocket_tick_health/summary.json")
    tick_health = read_json(tick_health_path)
    if tick_health.get("pass") is not True:
        add(
            blockers,
            "HIGH",
            "WEBSOCKET_TICK_HEALTH_NOT_PROVEN",
            "WebSocket tick health is not proven.",
            {"path": str(tick_health_path), "found": tick_health_path.exists()},
            "Implement/prove tick stream, last tick age, reconnect count and REST fallback state.",
        )

    # REST polling/sync interval concern from live health/state.
    refresh_interval = health.get("refresh_interval") or state.get("refresh_interval")
    if refresh_interval is not None:
        try:
            if float(refresh_interval) >= 5:
                add(
                    blockers,
                    "HIGH",
                    "REST_POLLING_INTERVAL_TOO_SLOW_FOR_OPTIONS",
                    "Dashboard/runtime refresh interval is too slow for intraday options execution.",
                    {"refresh_interval_sec": refresh_interval},
                    "Use WebSocket tick stream for signal/execution timing; keep REST for fallback and audit only.",
                )
        except Exception:
            pass
    else:
        add(
            warnings,
            "MEDIUM",
            "REFRESH_INTERVAL_UNKNOWN",
            "Refresh interval is not visible in live proof.",
            {},
            "Expose refresh/tick latency in truth bridge.",
        )

    # Friction/expectancy gate requires dedicated proof file.
    friction_path = Path("reports/latest/friction_expectancy/summary.json")
    friction = read_json(friction_path)
    if friction.get("pass") is not True:
        add(
            blockers,
            "HIGH",
            "FRICTION_EXPECTANCY_NOT_PROVEN_POSITIVE",
            "Positive expectancy after brokerage, charges, spread and slippage is not proven.",
            {"path": str(friction_path), "found": friction_path.exists()},
            "Generate costed expectancy report from paper/live-like trade ledger.",
        )
    else:
        ev = friction.get("evidence", {}) if isinstance(friction.get("evidence"), dict) else {}
        if ev.get("net_expectancy_after_costs", 0) <= 0:
            add(
                blockers,
                "CRITICAL",
                "NEGATIVE_EXPECTANCY_AFTER_COSTS",
                "Strategy expectancy after all costs is non-positive.",
                ev,
                "Quarantine strategy until costed expectancy is positive.",
            )

    execution_path = Path("reports/latest/execution_quality/summary.json")
    execution = read_json(execution_path)
    if execution.get("pass") is not True:
        add(
            blockers,
            "HIGH",
            "EXECUTION_QUALITY_NOT_PROVEN",
            "Execution quality/slippage/spread proof is missing.",
            {"path": str(execution_path), "found": execution_path.exists()},
            "Generate entry/exit delay, spread paid and slippage proof.",
        )

    chain_path = Path("reports/latest/option_chain_integrity/summary.json")
    chain = read_json(chain_path)
    if chain.get("pass") is not True:
        add(
            blockers,
            "HIGH",
            "OPTION_CHAIN_INTEGRITY_NOT_PROVEN",
            "Spot/chain/Greeks synchronization proof is missing.",
            {"path": str(chain_path), "found": chain_path.exists()},
            "Prove spot, option chain and Greeks timestamps are synchronized before signals.",
        )

    model_gap_path = Path("reports/latest/model_to_trade_gap/summary.json")
    model_gap = read_json(model_gap_path)
    if model_gap.get("pass") is not True:
        add(
            blockers,
            "HIGH",
            "MODEL_TO_TRADE_GAP_NOT_PROVEN",
            "Prediction hit rate is not proven to translate into net trade profitability.",
            {"path": str(model_gap_path), "found": model_gap_path.exists()},
            "Compare forecast hit rate vs trade win rate and net expectancy.",
        )

    # Strategy quarantine decision.
    quarantined = bool(blockers)
    summary = {
        "production_live_ready": False,
        "paper_analyzer_allowed": True,
        "strategy_quarantined_for_live": quarantined,
        "highest_severity": highest(blockers + warnings),
        "blocker_count": len(blockers),
        "warning_count": len(warnings),
        "severity_counts": sev_counts(blockers + warnings),
    }
    return {"summary": summary, "blockers": blockers, "warnings": warnings}


def write_md(report: Dict[str, Any], path: Path) -> None:
    summary = report["summary"]
    lines = [
        "# System3 Production Viability Bridge",
        "",
        f"Generated UTC: `{report['generated_utc']}`",
        "",
        "## Summary",
        "",
        "| Field | Value |",
        "|---|---|",
    ]
    for k, v in summary.items():
        lines.append(f"| `{k}` | `{v}` |")
    lines += ["", "## Blockers", "", "| Severity | Code | Message | Action |", "|---|---|---|---|"]
    for item in report["blockers"]:
        lines.append(f"| {item['severity']} | `{item['code']}` | {item['message']} | {item.get('action','')} |")
    if not report["blockers"]:
        lines.append("| NONE | - | No blockers found | - |")
    lines += ["", "## Warnings", "", "| Severity | Code | Message | Action |", "|---|---|---|---|"]
    for item in report["warnings"]:
        lines.append(f"| {item['severity']} | `{item['code']}` | {item['message']} | {item.get('action','')} |")
    if not report["warnings"]:
        lines.append("| NONE | - | No warnings found | - |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    truth = read_json(TRUTH_BRIDGE)
    inputs = {name: read_json(path) for name, path in INPUTS.items()}
    analysis = analyze(truth, inputs)
    report = {"generated_utc": now(), "truth_bridge_found": TRUTH_BRIDGE.exists(), "inputs": inputs, **analysis}
    (OUT_DIR / "latest.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    write_md(report, OUT_DIR / "summary.md")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
