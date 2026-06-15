#!/usr/bin/env python3
"""
System3 Blocker Finder.

Read-only verification tool. It does not modify runtime logic, broker settings,
.env files, credentials, live trading flags, or order routes.

Outputs:
- reports/latest/system3_blocker_report.json
- reports/latest/system3_blocker_report.md
"""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Blocker:
    blocker_id: str
    severity: str
    area: str
    title: str
    evidence: str
    required_action: str
    status: str = "OPEN"


REPORT_FILES = [
    "reports/latest/markdown_inventory.md",
    "reports/latest/documentation_contradictions.md",
    "reports/latest/option_strike_visibility.md",
    "reports/latest/option_strike_visibility.json",
    "reports/latest/model_accuracy_report.md",
    "reports/latest/model_accuracy_report.json",
]

ACTIVE_CONTROL_DOCS = [
    "SYSTEM3_MASTER_TRACKER.md",
    "SYSTEM3_BLOCKER_REGISTER.md",
    "docs/control_plane/SYSTEM3_CURRENT_RUNTIME_TRUTH.md",
    "docs/control_plane/SYSTEM3_SIGNAL_TO_TRADE_CONTROL.md",
    "docs/control_plane/SYSTEM3_MODEL_ACCURACY_REGISTER.md",
    "docs/control_plane/SYSTEM3_AGENT_RUNBOOK.md",
    "docs/control_plane/SYSTEM3_DOCUMENTATION_CONTROL_PLANE.md",
]


class SafeJson:
    @staticmethod
    def loads_file(path: Path) -> Optional[Any]:
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            return None

    @staticmethod
    def fetch(url: str, timeout: int = 8) -> Tuple[Optional[Any], Optional[str]]:
        try:
            with urllib.request.urlopen(url, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
            return json.loads(raw), None
        except urllib.error.HTTPError as exc:
            return None, f"HTTP_ERROR_{exc.code}: {exc.reason}"
        except Exception as exc:
            return None, f"FETCH_ERROR: {type(exc).__name__}: {exc}"


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def read_text(path: Path, limit: int = 200_000) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except Exception:
        return ""


def get_nested(data: Any, dotted: str, default: Any = None) -> Any:
    cur = data
    for part in dotted.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return default
    return cur


def load_runtime_state(root: Path, api_base: Optional[str]) -> Tuple[Optional[Dict[str, Any]], Optional[str], str]:
    if api_base:
        api_base = api_base.rstrip("/")
        data, err = SafeJson.fetch(f"{api_base}/api/state")
        if isinstance(data, dict):
            return data, None, f"api:{api_base}/api/state"
        return None, err, f"api:{api_base}/api/state"

    candidates = [
        root / "state" / "runtime_state.json",
        root / "outputs" / "state.json",
        root / "outputs" / "runtime_state.json",
        root / "dashboard" / "backend" / "state.json",
    ]
    for p in candidates:
        data = SafeJson.loads_file(p)
        if isinstance(data, dict):
            return data, None, str(p.relative_to(root))
    return None, "No local runtime state JSON found. Pass --api-base to check live endpoints.", "local-files"


def load_broker_status(api_base: Optional[str]) -> Tuple[Optional[Dict[str, Any]], Optional[str], str]:
    if not api_base:
        return None, "No --api-base supplied for /api/broker/status", "not-requested"
    api_base = api_base.rstrip("/")
    data, err = SafeJson.fetch(f"{api_base}/api/broker/status")
    if isinstance(data, dict):
        return data, None, f"api:{api_base}/api/broker/status"
    return None, err, f"api:{api_base}/api/broker/status"


def detect_false_broker_alert(state: Dict[str, Any], broker: Optional[Dict[str, Any]]) -> Optional[Blocker]:
    state_broker_connected = bool(get_nested(state, "broker.connected", False))
    broker_connected = bool(broker.get("connected")) if isinstance(broker, dict) else state_broker_connected
    alerts = state.get("alerts") or []
    has_disconnect = False
    latest = ""
    if isinstance(alerts, list):
        for alert in alerts[:10]:
            if isinstance(alert, dict) and "BROKER_DISCONNECTED" in json.dumps(alert, ensure_ascii=False):
                has_disconnect = True
                latest = json.dumps(alert, ensure_ascii=False)[:300]
                break
    if broker_connected and state_broker_connected and has_disconnect:
        return Blocker(
            "SYS3-BLK-001",
            "HIGH",
            "Broker/alerts",
            "False BROKER_DISCONNECTED alert while broker is connected",
            f"state.broker.connected={state_broker_connected}, broker.status.connected={broker_connected}, latest_alert={latest}",
            "Patch alert generation to use canonical broker status, 3-failure threshold, dedupe, and recovery clear.",
        )
    return None


def detect_safety(state: Optional[Dict[str, Any]], broker: Optional[Dict[str, Any]]) -> List[Blocker]:
    blockers: List[Blocker] = []
    mode = get_nested(state, "mode", None) if state else None
    live_enabled = get_nested(state, "broker.live_trading_enabled", None) if state else None
    order_allowed = get_nested(state, "broker.order_placement_allowed", None) if state else None
    if broker:
        live_enabled = broker.get("live_trading_enabled", live_enabled)
        order_allowed = broker.get("order_placement_allowed", order_allowed)
    if mode and str(mode).upper() not in {"PAPER", "ANALYZER", "ANALYZE"}:
        blockers.append(Blocker("SYS3-BLK-SAFETY-001", "CRITICAL", "Safety", "Runtime mode is not PAPER/ANALYZER", f"mode={mode}", "Stop and restore PAPER/ANALYZER mode."))
    if live_enabled is True:
        blockers.append(Blocker("SYS3-BLK-SAFETY-002", "CRITICAL", "Safety", "Live trading appears enabled", f"live_trading_enabled={live_enabled}", "Disable live trading immediately."))
    if order_allowed is True:
        blockers.append(Blocker("SYS3-BLK-SAFETY-003", "CRITICAL", "Safety", "Order placement appears allowed", f"order_placement_allowed={order_allowed}", "Block order placement immediately."))
    return blockers


def detect_missing_reports(root: Path) -> List[Blocker]:
    blockers: List[Blocker] = []
    missing = [p for p in REPORT_FILES if not (root / p).exists()]
    if missing:
        blockers.append(Blocker(
            "SYS3-BLK-007",
            "HIGH",
            "Control plane",
            "Required proof reports are missing",
            ", ".join(missing),
            "Run markdown inventory, option visibility audit, and model accuracy tracker.",
        ))
    return blockers


def detect_missing_active_docs(root: Path) -> List[Blocker]:
    missing = [p for p in ACTIVE_CONTROL_DOCS if not (root / p).exists()]
    if not missing:
        return []
    return [Blocker(
        "SYS3-BLK-DOC-001",
        "HIGH",
        "Documentation",
        "Required active control documents missing",
        ", ".join(missing),
        "Create/restore missing active control documents before patching runtime.",
    )]


def detect_dashboard_hardcoded(root: Path) -> List[Blocker]:
    app_js = root / "dashboard" / "app.js"
    text = read_text(app_js)
    evidence_terms = []
    for term in ["proof", "8/8", "Paper Lifecycle", "ML Accuracy", "PASS", "PEND"]:
        if term in text:
            evidence_terms.append(term)
    if {"PASS", "PEND"}.issubset(set(evidence_terms)) and "Paper Lifecycle" in evidence_terms:
        return [Blocker(
            "SYS3-BLK-002",
            "HIGH",
            "Dashboard truth",
            "Dashboard proof gates may contain static/hard-coded pass-pending contradiction",
            f"dashboard/app.js contains terms: {', '.join(evidence_terms)}",
            "Replace/label static proof matrix with backend/runtime report-driven proof gates.",
        )]
    return []


def detect_option_visibility(root: Path) -> List[Blocker]:
    outputs = [
        root / "reports" / "latest" / "option_strike_visibility.json",
        root / "reports" / "latest" / "option_strike_visibility.md",
    ]
    if all(p.exists() for p in outputs):
        return []
    return [Blocker(
        "SYS3-BLK-003",
        "CRITICAL",
        "Option visibility",
        "PE/CE expiry/strike/token visibility report missing",
        "reports/latest/option_strike_visibility.md/json not found",
        "Run scripts/system3_option_visibility_audit.py and verify every signal maps or is blocked with reason.",
    )]


def detect_model_accuracy(root: Path) -> List[Blocker]:
    outputs = [
        root / "reports" / "latest" / "model_accuracy_report.json",
        root / "reports" / "latest" / "model_accuracy_report.md",
    ]
    if all(p.exists() for p in outputs):
        return []
    return [Blocker(
        "SYS3-BLK-005",
        "HIGH",
        "Model accuracy",
        "Model accuracy proof report missing",
        "reports/latest/model_accuracy_report.md/json not found",
        "Run scripts/system3_model_accuracy_tracker.py; require prediction-before-move and actual outcome proof.",
    )]


def write_markdown(path: Path, summary: Dict[str, Any], blockers: List[Blocker]) -> None:
    sev_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
    blockers = sorted(blockers, key=lambda b: (sev_order.get(b.severity, 9), b.blocker_id))
    lines = [
        "# System3 Blocker Report",
        "",
        f"Generated UTC: `{summary['generated_at_utc']}`",
        "",
        "## Summary",
        "",
        f"- **Total blockers**: `{summary['total_blockers']}`",
        f"- **Critical blockers**: `{summary['severity_counts'].get('CRITICAL', 0)}`",
        f"- **High blockers**: `{summary['severity_counts'].get('HIGH', 0)}`",
        f"- **Safety status**: `{summary['safety_status']}`",
        "",
        "## Blockers",
        "",
        "| ID | Severity | Area | Title | Evidence | Required Action |",
        "|---|---:|---|---|---|---|",
    ]
    if blockers:
        for b in blockers:
            evidence = b.evidence.replace("|", "/")[:500]
            action = b.required_action.replace("|", "/")[:500]
            lines.append(f"| `{b.blocker_id}` | `{b.severity}` | `{b.area}` | {b.title} | {evidence} | {action} |")
    else:
        lines.append("| `NONE` | `INFO` | `All` | No blocker detected by this static scan | Runtime proof still required | Continue PAPER proof cycle |")
    lines.extend([
        "",
        "## Non-Negotiable Reminder",
        "",
        "- Do not enable live trading.",
        "- Do not touch credentials or `.env`.",
        "- Do not mark trade-ready until PE/CE strike/token and model outcome reports exist.",
        "- Do not use old FINAL/COMPLETE docs as current truth.",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="System3 blocker finder")
    parser.add_argument("--root", default=None, help="Repo root. Defaults to script parent repo root.")
    parser.add_argument("--api-base", default=os.environ.get("SYSTEM3_API_BASE"), help="Optional live base URL, e.g. https://...render.com")
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else repo_root_from_script()
    reports = root / "reports" / "latest"
    reports.mkdir(parents=True, exist_ok=True)

    blockers: List[Blocker] = []
    state, state_err, state_source = load_runtime_state(root, args.api_base)
    broker, broker_err, broker_source = load_broker_status(args.api_base)

    blockers.extend(detect_missing_active_docs(root))
    blockers.extend(detect_missing_reports(root))
    blockers.extend(detect_dashboard_hardcoded(root))
    blockers.extend(detect_option_visibility(root))
    blockers.extend(detect_model_accuracy(root))
    blockers.extend(detect_safety(state, broker))

    if state:
        false_alert = detect_false_broker_alert(state, broker)
        if false_alert:
            blockers.append(false_alert)
    else:
        blockers.append(Blocker(
            "SYS3-BLK-RUNTIME-001",
            "MEDIUM",
            "Runtime truth",
            "Runtime state not available to blocker finder",
            state_err or "No state loaded",
            "Run with --api-base or provide local runtime state output.",
        ))

    severity_counts: Dict[str, int] = {}
    for b in blockers:
        severity_counts[b.severity] = severity_counts.get(b.severity, 0) + 1
    safety_blocked = any(b.severity == "CRITICAL" and b.area == "Safety" for b in blockers)
    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "api_base": args.api_base,
        "state_source": state_source,
        "state_error": state_err,
        "broker_source": broker_source,
        "broker_error": broker_err,
        "total_blockers": len(blockers),
        "severity_counts": severity_counts,
        "safety_status": "BLOCKED" if safety_blocked else "PAPER_SAFETY_NOT_BLOCKED_BY_STATIC_SCAN",
    }
    data = {"summary": summary, "blockers": [asdict(b) for b in blockers]}
    write_json(reports / "system3_blocker_report.json", data)
    write_markdown(reports / "system3_blocker_report.md", summary, blockers)

    print("SYSTEM3_BLOCKER_FINDER_COMPLETE")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 1 if safety_blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
