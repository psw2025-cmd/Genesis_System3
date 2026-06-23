#!/usr/bin/env python3
"""System3 Truth Bridge.

Creates one GitHub-readable truth snapshot from:
- public live dashboard API endpoints
- repo proof JSON files already committed
- safety/readiness contradictions

Read-only. No broker secrets. No orders. No live trading.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_BASE_URL = "https://genesis-system3-backend.onrender.com"
DEFAULT_UNDERLYINGS = "NIFTY,BANKNIFTY,FINNIFTY,MIDCPNIFTY"

PROOF_FILES = {
    "full_trading_pipeline_readiness": "reports/latest/full_trading_pipeline_readiness/09_pipeline_gate_summary.json",
    "proof_status_matrix": "reports/latest/proof_status_matrix/proof_status_matrix.json",
    "dashboard_truth_proof": "reports/latest/dashboard_truth_proof/summary.json",
    "fresh_data_automation_proof": "reports/latest/fresh_data_automation_proof/summary.json",
    "analyzer_paper_lifecycle_proof": "reports/latest/analyzer_paper_lifecycle_proof/summary.json",
    "analyzer_paper_lifecycle_raw": "reports/latest/analyzer_paper_lifecycle_proof/LIFECYCLE_20260614_142129.json",
    "model_training_load_proof": "reports/latest/model_training_load_proof/summary.json",
    "live_current_issues": "reports/latest/live_current_issue_check/issues.json",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def s(value) -> str:
    return "" if value is None else str(value).strip().lower()


def read_json(path: Path):
    if not path.exists():
        return {"ok": False, "missing": True, "path": str(path)}
    try:
        return {"ok": True, "path": str(path), "data": json.loads(path.read_text(encoding="utf-8"))}
    except Exception as exc:
        return {"ok": False, "path": str(path), "error": f"{type(exc).__name__}: {exc}"}


def http_json(url: str, timeout: int = 30):
    try:
        req = Request(url, headers={"User-Agent": "System3TruthBridge/1.0"})
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return {"ok": True, "url": url, "status_code": resp.status, "data": json.loads(raw)}
    except HTTPError as exc:
        return {"ok": False, "url": url, "status_code": exc.code, "error": str(exc)}
    except URLError as exc:
        return {"ok": False, "url": url, "error": str(exc)}
    except Exception as exc:
        return {"ok": False, "url": url, "error": f"{type(exc).__name__}: {exc}"}


def collect_live(base_url: str, underlyings: list[str]) -> dict:
    base_url = base_url.rstrip("/")
    targets = {
        "state": f"{base_url}/api/state",
        "health": f"{base_url}/api/health",
        "broker_status": f"{base_url}/api/broker/status",
        "debug_state_source": f"{base_url}/api/debug/state_source",
        "underlyings": f"{base_url}/api/underlyings",
        "qc": f"{base_url}/api/qc",
    }
    for u in underlyings:
        targets[f"chain_{u}"] = f"{base_url}/api/chain/{u}"
    return {name: http_json(url) for name, url in targets.items()}


def collect_proofs(repo_root: Path) -> dict:
    return {name: read_json(repo_root / rel) for name, rel in PROOF_FILES.items()}


def add_issue(issues, severity, code, message, proof=None, action=None):
    issues.append({
        "severity": severity,
        "code": code,
        "message": message,
        "proof": proof or {},
        "action": action or "",
    })


def analyze_live(live: dict) -> list[dict]:
    issues = []
    for name, ep in live.items():
        if not ep.get("ok"):
            add_issue(issues, "HIGH", "LIVE_ENDPOINT_FAILED", f"Live endpoint failed: {name}", {"endpoint": name, "error": ep.get("error"), "status_code": ep.get("status_code")}, "Check Render endpoint/service logs.")

    state = live.get("state", {}).get("data", {}) if live.get("state", {}).get("ok") else {}
    health = live.get("health", {}).get("data", {}) if live.get("health", {}).get("ok") else {}
    broker = live.get("broker_status", {}).get("data", {}) if live.get("broker_status", {}).get("ok") else {}

    broker_state = state.get("broker", {})
    market_state = state.get("market", {})
    state_broker_connected = broker_state.get("connected")
    direct_broker_connected = broker.get("connected")
    health_broker_status = health.get("broker_status")
    market_open = market_state.get("is_open")
    state_ds = state.get("data_source")
    health_ds = health.get("data_source")
    alerts = state.get("alerts", []) if isinstance(state.get("alerts"), list) else []
    alert_codes = [a.get("code") for a in alerts if isinstance(a, dict)]

    if state_broker_connected is True and s(health_broker_status) not in ("connected", "ok"):
        add_issue(issues, "HIGH", "BROKER_STATE_HEALTH_MISMATCH", "State says broker connected but health does not.", {"state_broker_connected": state_broker_connected, "health_broker_status": health_broker_status})
    if direct_broker_connected is True and state_broker_connected is False:
        add_issue(issues, "HIGH", "BROKER_DIRECT_STATE_MISMATCH", "Direct broker endpoint connected but state not connected.", {"direct_broker_connected": direct_broker_connected, "state_broker_connected": state_broker_connected})
    if state_broker_connected is True and "BROKER_DISCONNECTED" in alert_codes:
        add_issue(issues, "HIGH", "FALSE_BROKER_DISCONNECTED", "False broker disconnected alert active while broker is connected.", {"alert_codes": alert_codes})
    if s(state_ds) == "synthetic" and state_broker_connected is True and market_open is False:
        add_issue(issues, "MEDIUM", "BAD_CLOSED_MARKET_DATA_SOURCE", "Closed market + connected broker should not be labelled SYNTHETIC.", {"state_data_source": state_ds})
    if state_ds and health_ds and s(state_ds) != s(health_ds):
        allowed = {("broker_connected_market_closed", "live"), ("broker_live", "live"), ("broker_live", "real")}
        if (s(state_ds), s(health_ds)) not in allowed:
            add_issue(issues, "MEDIUM", "DATA_SOURCE_MISMATCH", "State and health data_source labels differ.", {"state_data_source": state_ds, "health_data_source": health_ds})
    if s(state.get("mode")) == "live" or broker_state.get("live_trading_enabled") is True or broker_state.get("order_placement_allowed") is True:
        add_issue(issues, "CRITICAL", "LIVE_SAFETY_BREACH", "Live mode/order placement appears enabled.", {"mode": state.get("mode"), "live_trading_enabled": broker_state.get("live_trading_enabled"), "order_placement_allowed": broker_state.get("order_placement_allowed")})

    for name, ep in live.items():
        if not name.startswith("chain_") or not ep.get("ok"):
            continue
        data = ep.get("data", {})
        total = data.get("total_contracts") or len(data.get("contracts") or [])
        if state_broker_connected is True and s(data.get("status")) == "not_ready":
            add_issue(issues, "HIGH", "CHAIN_NOT_READY_WITH_BROKER", f"{name} says NOT_READY while broker is connected.", {"chain_status": data.get("status"), "message": data.get("message")})
        if market_open is True and int(total or 0) == 0:
            add_issue(issues, "HIGH", "ZERO_CHAIN_CONTRACTS_MARKET_OPEN", f"{name} has zero contracts while market is open.", {"total_contracts": total})
    return issues


def analyze_proofs(proofs: dict) -> list[dict]:
    issues = []
    fpr = proofs.get("full_trading_pipeline_readiness", {}).get("data", {})
    if fpr and fpr.get("trade_ready") is not True:
        add_issue(issues, "CRITICAL", "TRADE_READY_FALSE", "Full trading pipeline is not trade ready.", {"verdict": fpr.get("verdict"), "blockers": fpr.get("blockers")}, "Run real market analyzer paper lifecycle and fresh broker data proof.")

    matrix = proofs.get("proof_status_matrix", {}).get("data", {})
    if matrix and matrix.get("trade_ready") is not True:
        add_issue(issues, "HIGH", "PROOF_MATRIX_INCOMPLETE", "Proof matrix still says not trade ready.", {"verdict": matrix.get("verdict")})
    for row in matrix.get("rows", []) if isinstance(matrix.get("rows"), list) else []:
        if row.get("status") == "PASS_WITH_WARNINGS":
            add_issue(issues, "MEDIUM", "PROOF_GATE_WARNING", f"Proof gate warning: {row.get('name')}", {"warnings": row.get("warnings")})

    fresh = proofs.get("fresh_data_automation_proof", {}).get("data", {})
    ev = fresh.get("evidence", {}) if isinstance(fresh.get("evidence"), dict) else {}
    if ev and ev.get("fresh_broker_live_data_proven") is not True:
        add_issue(issues, "HIGH", "FRESH_BROKER_DATA_NOT_PROVEN", "Fresh broker live data is not proven in proof pack.", {"reason": ev.get("reason_fresh_broker_live_data_not_proven")})

    dash = proofs.get("dashboard_truth_proof", {}).get("data", {})
    dev = dash.get("evidence", {}) if isinstance(dash.get("evidence"), dict) else {}
    if dev.get("browser_visual_truth_proven") is not True:
        add_issue(issues, "MEDIUM", "BROWSER_VISUAL_TRUTH_MISSING", "Browser/screenshot truth is not proven.", {})
    if dev.get("api_db_report_reconciliation_proven") is not True:
        add_issue(issues, "MEDIUM", "API_DB_REPORT_RECON_MISSING", "API/DB/report reconciliation is not proven.", {})

    life = proofs.get("analyzer_paper_lifecycle_proof", {}).get("data", {})
    lev = life.get("evidence", {}) if isinstance(life.get("evidence"), dict) else {}
    if lev.get("full_lifecycle_proven") is not True or lev.get("lifecycle_proof_dry_run") is True:
        add_issue(issues, "CRITICAL", "REAL_PAPER_LIFECYCLE_NOT_PROVEN", "Real market analyzer paper lifecycle is not proven.", {"full_lifecycle_proven": lev.get("full_lifecycle_proven"), "dry_run": lev.get("lifecycle_proof_dry_run")})

    raw = proofs.get("analyzer_paper_lifecycle_raw", {}).get("data", {})
    if raw.get("dry_run") is True or raw.get("signal", {}).get("instrument_token") == "DRY_RUN_TOKEN":
        add_issue(issues, "CRITICAL", "RAW_LIFECYCLE_IS_DRY_RUN", "Raw lifecycle proof is dry-run/simulation.", {"market_status": raw.get("market_status"), "instrument_token": raw.get("signal", {}).get("instrument_token")})

    model = proofs.get("model_training_load_proof", {}).get("data", {})
    mev = model.get("evidence", {}) if isinstance(model.get("evidence"), dict) else {}
    if mev.get("promotion_allowed") is not True:
        add_issue(issues, "HIGH", "MODEL_PROMOTION_BLOCKED", "Model promotion is blocked by policy/proof.", {"promotion_allowed": mev.get("promotion_allowed")})

    return issues


def summarize(snapshot: dict) -> dict:
    state = snapshot.get("live", {}).get("state", {}).get("data", {}) if snapshot.get("live", {}).get("state", {}).get("ok") else {}
    health = snapshot.get("live", {}).get("health", {}).get("data", {}) if snapshot.get("live", {}).get("health", {}).get("ok") else {}
    issues = snapshot.get("issues", [])
    counts = {}
    for issue in issues:
        counts[issue["severity"]] = counts.get(issue["severity"], 0) + 1
    return {
        "generated_utc": snapshot.get("generated_utc"),
        "mode": state.get("mode"),
        "market_open": state.get("market", {}).get("is_open"),
        "state_data_source": state.get("data_source"),
        "health_data_source": health.get("data_source"),
        "broker_connected": state.get("broker", {}).get("connected"),
        "alerts_count": len(state.get("alerts", [])) if isinstance(state.get("alerts"), list) else None,
        "issue_count": len(issues),
        "issue_counts_by_severity": counts,
        "live_trading_enabled": state.get("broker", {}).get("live_trading_enabled"),
        "order_placement_allowed": state.get("broker", {}).get("order_placement_allowed"),
    }


def write_md(snapshot: dict, path: Path) -> None:
    lines = ["# System3 Truth Bridge", "", f"Generated UTC: `{snapshot['generated_utc']}`", "", "## Summary", "", "| Field | Value |", "|---|---|"]
    for key, val in snapshot["summary"].items():
        lines.append(f"| `{key}` | `{val}` |")
    lines += ["", "## Issues", ""]
    if not snapshot["issues"]:
        lines.append("No issues detected by bridge rules.")
    else:
        lines += ["| Severity | Code | Message |", "|---|---|---|"]
        for issue in snapshot["issues"]:
            lines.append(f"| {issue['severity']} | `{issue['code']}` | {issue['message']} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=os.environ.get("SYSTEM3_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--underlyings", default=os.environ.get("SYSTEM3_UNDERLYINGS", DEFAULT_UNDERLYINGS))
    parser.add_argument("--out-dir", default="reports/latest/system3_truth_bridge")
    args = parser.parse_args()

    repo_root = Path.cwd()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    underlyings = [x.strip().upper() for x in args.underlyings.split(",") if x.strip()]

    live = collect_live(args.base_url, underlyings)
    proofs = collect_proofs(repo_root)
    snapshot = {
        "generated_utc": utc_now(),
        "base_url": args.base_url.rstrip("/"),
        "underlyings": underlyings,
        "purpose": "GitHub-readable single source of truth for live dashboard and proof status.",
        "live": live,
        "proofs": proofs,
    }
    snapshot["issues"] = analyze_live(live) + analyze_proofs(proofs)
    snapshot["summary"] = summarize(snapshot)

    (out_dir / "latest.json").write_text(json.dumps(snapshot, indent=2, sort_keys=True), encoding="utf-8")
    write_md(snapshot, out_dir / "summary.md")
    print(json.dumps(snapshot["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
