from __future__ import annotations

import json
from pathlib import Path

from dashboard.backend.auto_gates_service import _proof_gates_from_payload
from scripts.system3_gate_evaluator import SPEARMAN_DAYS_REQUIRED, SPEARMAN_THRESHOLD

ROOT = Path(__file__).resolve().parents[1]


def test_owner_approval_and_live_latch_are_distinct_and_live_stays_off():
    owner = json.loads((ROOT / "config/human_approval_gate.json").read_text(encoding="utf-8"))
    kill = json.loads((ROOT / "config/kill_switch.json").read_text(encoding="utf-8"))

    assert owner["approved"] is True
    assert owner["live_trading_env_flip_authorized"] is False
    assert kill["live_trading_approved"] is False
    assert "min_validation_days" not in kill
    assert "min_ml_accuracy_rho" not in kill


def test_spearman_gate_threshold_is_evidence_based_not_kill_switch_override():
    assert SPEARMAN_DAYS_REQUIRED == 3
    assert SPEARMAN_THRESHOLD == 0.10


def test_alert_ui_separates_live_readiness_info_from_active_operational_alerts():
    helper = (ROOT / "dashboard/frontend/src/lib/alertTruth.ts").read_text(encoding="utf-8")
    text = (ROOT / "dashboard/frontend/src/components/AlertsTab.tsx").read_text(encoding="utf-8")

    assert "export function isLiveReadinessInfo" in helper
    assert "OPS_LIVE_GATE" in helper
    assert "LIVE_GATE" in helper
    assert "splitAlertStream" in text
    assert "from '../lib/alertTruth'" in text
    assert "liveReadinessInfo" in text
    assert "activeAlerts" in text
    assert "BLOCKED BY DESIGN" in text
    assert "live approval is not required for PAPER/ANALYZER operation" in text
    assert "`${activeAlerts.length} ACTIVE`" in text
    assert "`${alerts.length} ACTIVE`" not in text


def _is_live_readiness_info(alert: dict) -> bool:
    """Mirrors dashboard/frontend/src/lib/alertTruth.ts for leak-payload contracts."""
    type_ = str(alert.get("type") or alert.get("category") or "").upper()
    code = str(alert.get("code") or "").upper()
    ident = str(alert.get("id") or "").upper()
    title = str(alert.get("title") or "").upper()
    message = str(alert.get("message") or alert.get("detail") or "").upper()
    if type_ == "LIVE_GATE" or code == "LIVE_GATE":
        return True
    if ident == "OPS_LIVE_GATE" or "LIVE_GATE" in ident:
        return True
    if "LIVE TRADING CORRECTLY BLOCKED" in title:
        return True
    if "LIVE_TRADING_APPROVED" in message and "HUMAN_APPROVED" in message:
        return True
    if "LIVE REMAINS BLOCKED BY DESIGN" in message:
        return True
    return False


def test_production_live_gate_leak_payload_is_not_an_active_operational_alert():
    leaked = {
        "id": "OPS_LIVE_GATE",
        "type": "system_alert",
        "severity": "info",
        "title": "Live trading correctly BLOCKED",
        "message": (
            "human_approved=NOT APPROVED — owner must set live_trading_approved=true "
            "in kill_switch.json; validation_days=1 validation days (need ≥10); "
            "ml_accuracy_rho=Avg Spearman ρ=0.200 (need ≥0.70)"
        ),
    }
    fixed = {
        "id": "OPS_LIVE_GATE",
        "type": "LIVE_GATE",
        "code": "LIVE_GATE",
        "severity": "INFO",
        "title": "Live trading correctly BLOCKED",
        "message": (
            "Live remains blocked by design in PAPER/ANALYZER. "
            "Live approval is not required for paper operation."
        ),
    }
    broker = {
        "id": "OPS_BROKER",
        "type": "system_alert",
        "severity": "HIGH",
        "title": "Broker disconnected",
        "message": "DHAN_REQUEST_REJECTED_906",
    }
    assert _is_live_readiness_info(leaked) is True
    assert _is_live_readiness_info(fixed) is True
    assert _is_live_readiness_info(broker) is False
    active = [row for row in (leaked, fixed, broker) if not _is_live_readiness_info(row)]
    assert active == [broker]


def test_proof_gate_adapter_never_forces_failed_evaluator_gates_to_pass():
    payload = {
        "gates": {
            "ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS": {
                "pass": False,
                "days_recorded": 1,
                "days_required": 3,
                "latest_rho": 0.99,
                "threshold": 0.10,
            },
            "POSITIVE_NET_EXPECTANCY_AFTER_COSTS": {
                "pass": False,
                "net_expectancy_after_costs": 10.0,
                "win_rate": 0.9,
            },
            "REAL_PAPER_LIFECYCLE_MARKET_DAY_PROOF": {
                "pass": False,
                "full_lifecycle_proven": False,
            },
            "WEBSOCKET_TICK_HEALTH_PROVEN": {
                "pass": False,
                "last_tick_age_sec": None,
                "refresh_interval_sec": 1,
            },
            "MODEL_ACCURACY_REPORT_PRESENT": {"pass": False},
            "OPTION_STRIKE_VISIBILITY_PROVEN": {"pass": False},
            "EQUITY_FO_ELIGIBILITY_PROVEN": {"pass": False},
        }
    }

    adapted = _proof_gates_from_payload(payload)
    assert len(adapted) == 7
    assert all(row["pass"] is False for row in adapted)
    assert all(row["ok"] is False for row in adapted)
    assert all(row["status"] == "COLLECTING" for row in adapted)
