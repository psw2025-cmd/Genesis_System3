#!/usr/bin/env python3
"""Multi-agent production coordination — proof-only, no live trading.

SYSTEM3_TEMPORAL_TRUTH_V1: this coordinator may collect fresh API truth, but stored
reports remain historical. It must never convert HTTP 200 or reports/latest into a
current semantic UI/production-readiness PASS.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports" / "latest" / "production_grade_readiness"
DEFAULT_GCP_URL = "https://genesis-system3-web-doq2wplepa-el.a.run.app"
BASE_URL = os.environ.get(
    "SYSTEM3_PUBLIC_BACKEND_URL", os.environ.get("BACKEND_URL", DEFAULT_GCP_URL)
).rstrip("/")

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def get_python_executable() -> str:
    venv_exe = ROOT / "venv" / "Scripts" / "python.exe"
    if not venv_exe.exists():
        venv_exe = ROOT / "venv" / "bin" / "python"
    return str(venv_exe) if venv_exe.exists() else sys.executable


py_exe = get_python_executable()

AGENT_RUNS = [
    (
        "gate_orchestrator",
        [py_exe, "scripts/system3_master_proof_orchestrator.py"],
        "reports/latest/proof_status_matrix/proof_status_matrix.json",
    ),
    ("dashboard_audit", [py_exe, "tools/dashboard_full_audit.py"], "reports/latest/dashboard_full_audit/summary.json"),
    (
        "broker_validation",
        [py_exe, "tools/broker_trader_validation.py"],
        "reports/latest/broker_trader_validation/summary.json",
    ),
    (
        "audit_reports",
        [py_exe, "tools/generate_audit_reports.py"],
        "reports/latest/dhan_option_chain_schema_audit/summary.json",
    ),
    ("human_approval", [py_exe, "tools/record_human_approval.py"], "reports/latest/human_approval_gate/summary.json"),
    (
        "control_plane",
        [py_exe, "system3_control_plane.py", "proofs"],
        "reports/latest/system3_master_control_plane/system3_master_control_plane.json",
    ),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run_cmd(cmd: List[str]) -> Dict[str, Any]:
    try:
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=300)
        return {
            "exit_code": proc.returncode,
            "stdout_tail": proc.stdout[-1200:],
            "stderr_tail": proc.stderr[-600:],
            "passed": proc.returncode == 0,
        }
    except Exception as exc:
        return {"exit_code": -1, "error": str(exc)[:200], "passed": False}


def _artifact_metadata(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"exists": False, "evidence_class": "HISTORICAL_EVIDENCE"}
    stat = path.stat()
    return {
        "exists": True,
        "evidence_class": "HISTORICAL_EVIDENCE",
        "mtime_utc": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        "temporal_note": "Stored evidence is historical; path/name latest does not make it current.",
    }


def probe_live_endpoints() -> Dict[str, Any]:
    import urllib.request

    endpoints = [
        "/api/state",
        "/api/health",
        "/api/broker/status",
        "/api/paper",
        "/api/portfolio/unified",
        "/api/broker/holdings",
        "/api/broker/positions/live",
        "/api/broker/funds",
        "/api/broker/truth",
        "/api/trader/requirements",
        "/api/approval/status",
        "/api/trades/history",
    ]
    results: Dict[str, Any] = {}
    for ep in endpoints:
        url = f"{BASE_URL}{ep}"
        observed = utc_now()
        try:
            with urllib.request.urlopen(url, timeout=60) as resp:
                body = resp.read(4000).decode("utf-8", errors="replace")
                results[ep] = {
                    "observed_at_utc": observed,
                    "status": resp.status,
                    "ok": resp.status == 200,
                    "sample": body[:500],
                    "evidence_class": "REQUEST_SCOPED_LIVE_API",
                }
        except Exception as exc:
            results[ep] = {
                "observed_at_utc": observed,
                "status": 0,
                "ok": False,
                "error": str(exc)[:200],
                "evidence_class": "REQUEST_SCOPED_LIVE_API",
            }
    return results


def _json_sample(live: Dict[str, Any], endpoint: str) -> Dict[str, Any]:
    try:
        value = json.loads(live.get(endpoint, {}).get("sample", "{}"))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def main() -> int:
    REPORTS.mkdir(parents=True, exist_ok=True)
    capture_started = utc_now()

    agent_results = []
    for agent_id, cmd, evidence in AGENT_RUNS:
        evidence_path = ROOT / evidence
        run = run_cmd(cmd)
        agent_results.append(
            {
                "id": agent_id,
                "evidence": evidence,
                "stored_evidence": _artifact_metadata(evidence_path),
                "run_attempted": True,
                "run_passed": run["passed"],
                "run_detail": run,
                "current_runtime_truth_authority": False,
            }
        )

    live = probe_live_endpoints()
    state_data = _json_sample(live, "/api/state")
    broker_data = _json_sample(live, "/api/broker/status")
    health_data = _json_sample(live, "/api/health")
    broker_connected = broker_data.get("connected") is True

    # Historical gate files may guide investigation, but never become current runtime truth.
    gates_path = ROOT / "reports" / "latest" / "system3_auto_gates" / "summary.json"
    historical_gate_advisory: Dict[str, Any] = _artifact_metadata(gates_path)
    if gates_path.exists():
        try:
            gates = json.loads(gates_path.read_text(encoding="utf-8"))
            historical_gate_advisory["technical_gates_still_required_at_observation"] = list(
                gates.get("technical_gates_still_required") or []
            )
            historical_gate_advisory["recommended_auto_actions_at_observation"] = list(
                gates.get("recommended_auto_actions") or []
            )
        except Exception:
            historical_gate_advisory["parse_error"] = True

    blockers = [
        "LIVE_TRADING_DISABLED_BY_DESIGN",
        "FULL_REQUEST_SCOPED_LIVE_UI_LIFECYCLE_NOT_PROVEN_BY_THIS_COORDINATOR",
        "SEMANTIC_UI_READINESS_NOT_PROVEN_BY_HTTP_200",
    ]
    if not broker_connected:
        blockers.append("BROKER_CONNECTED_NOW_NOT_PROVEN")
    if not live.get("/api/health", {}).get("ok"):
        blockers.append("HEALTH_ENDPOINT_NOW_NOT_OK")

    capture_finished = utc_now()
    payload = {
        "schema": "system3-multi-agent-coordination-v2",
        "policy": "SYSTEM3_TEMPORAL_TRUTH_V1",
        "evidence_class": "REQUEST_SCOPED_LIVE_API",
        "capture_started_at_utc": capture_started,
        "capture_finished_at_utc": capture_finished,
        "captured_at_utc": capture_finished,
        "max_age_seconds": 300,
        "mode": "ANALYZER_PAPER_ONLY",
        "live_trading_enabled": False,
        "production_ready_for_real_money": False,
        "cloud_url": BASE_URL,
        "source_authority": "GCP_PRODUCTION_PUBLIC_URL",
        "agents": agent_results,
        "historical_gate_advisory": historical_gate_advisory,
        "live_endpoint_probe": live,
        "broker_connected": broker_connected,
        "broker_error": broker_data.get("error"),
        "health_status": health_data.get("status"),
        "data_source": state_data.get("data_source"),
        "readiness_ladder": {
            "api_transport_observed": any(v.get("ok") for v in live.values()),
            "broker_connected_observed": broker_connected,
            "semantic_dashboard_production_grade": False,
            "full_live_ui_lifecycle_current": False,
            "real_money_ready": False,
        },
        "blockers": list(dict.fromkeys(blockers)),
        "next_exact_actions": [
            "Run fresh request-scoped scripts/gcp_live_ui_snapshot.py against GCP production",
            "Inspect semantic_attention plus screenshots/visible text for all 22 live tabs",
            "Correlate any UI issue with fresh API/log evidence before fixing",
        ],
        "safety": {
            "read_only_capture": True,
            "mutation_endpoints_called": False,
            "order_endpoints_called": False,
            "secret_values_exposed": False,
        },
        "interpretation": {
            "reports_latest_is_current_truth": False,
            "http_200_is_semantic_ui_pass": False,
            "stored_artifacts_are_historical": True,
        },
    }

    with open(REPORTS / "summary.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    md_lines = [
        "# Production Grade Readiness — Multi-Agent Coordination",
        "",
        f"Captured UTC: `{payload['captured_at_utc']}`",
        "",
        "**Verdict: CURRENT API TRUTH PARTIAL — FULL LIVE UI LIFECYCLE REQUIRED**",
        "",
        "Stored reports listed below are historical evidence, not current runtime truth.",
        "",
        "## Agents run",
    ]
    for a in agent_results:
        md_lines.append(f"- **{a['id']}**: {'PASS' if a['run_passed'] else 'FAIL'} — historical output `{a['evidence']}`")
    md_lines.extend(
        [
            "",
            "## Fresh production API probes",
            *[f"- `{ep}`: {'OK' if v.get('ok') else 'FAIL'} at `{v.get('observed_at_utc')}`" for ep, v in live.items()],
            "",
            "## Current-proof blockers",
            *[f"- {b}" for b in payload["blockers"]],
            "",
            "## Next actions",
            *[f"- {x}" for x in payload["next_exact_actions"]],
        ]
    )
    with open(REPORTS / "summary.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print(f"Wrote {REPORTS / 'summary.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
