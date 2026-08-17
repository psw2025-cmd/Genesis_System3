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
    assert SPEARMAN_DAYS_REQUIRED == 5
    assert SPEARMAN_THRESHOLD == 0.70


def test_alert_ui_separates_live_readiness_info_from_active_operational_alerts():
    text = (ROOT / "dashboard/frontend/src/components/AlertsTab.tsx").read_text(encoding="utf-8")

    assert "isLiveReadinessInfo" in text
    assert "liveReadinessInfo" in text
    assert "activeAlerts" in text
    assert "LIVE_GATE" in text
    assert "BLOCKED BY DESIGN" in text
    assert "live approval is not required for PAPER/ANALYZER operation" in text
    assert "`${activeAlerts.length} ACTIVE`" in text
    assert "`${alerts.length} ACTIVE`" not in text


def test_proof_gate_adapter_never_forces_failed_evaluator_gates_to_pass():
    payload = {
        "gates": {
            "ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS": {
                "pass": False,
                "days_recorded": 1,
                "days_required": 5,
                "latest_rho": 0.99,
                "threshold": 0.70,
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
