"""Eval: LIVE_GATE kill-switch text must not count as an Active operational alert."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def test_eval_live_gate_synth_uses_live_gate_type_not_system_alert():
    text = _text("dashboard/backend/app.py")
    assert '"LIVE_GATE"' in text
    assert "Live trading correctly BLOCKED" in text
    assert "alert_type" in text
    assert '"type": alert_type' in text
    assert '"code": code' in text
    assert "owner must set live_trading_approved=true in kill_switch.json" not in text


def test_eval_alerts_tab_filters_production_live_gate_payload_shape():
    helper = _text("dashboard/frontend/src/lib/alertTruth.ts")
    assert "export function isLiveReadinessInfo" in helper
    assert "OPS_LIVE_GATE" in helper
    assert "LIVE_GATE" in helper
    tab = _text("dashboard/frontend/src/components/AlertsTab.tsx")
    assert "from '../lib/alertTruth'" in tab
    assert "splitAlertStream" in tab
    assert "`${alerts.length} ACTIVE`" not in tab
