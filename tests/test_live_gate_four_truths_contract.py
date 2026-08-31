from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "dashboard" / "frontend" / "src" / "components" / "LiveTradingGate.tsx"
APPROVAL_SERVICE = ROOT / "dashboard" / "backend" / "human_approval_service.py"
HUMAN_GATE = ROOT / "config" / "human_approval_gate.json"
KILL_SWITCH = ROOT / "config" / "kill_switch.json"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_live_gate_renders_four_independent_truths():
    text = _text(COMPONENT)
    for label in ("Execution Mode", "Owner Sign-off", "Technical Readiness", "LIVE Arming"):
        assert label in text
    assert 'fetch("/api/live-trading/gate")' in text
    assert 'fetch("/api/approval/status")' in text
    assert 'fetch("/api/health")' in text


def test_owner_signoff_comes_from_owner_approval_endpoint_not_legacy_live_arming_gate():
    text = _text(COMPONENT)
    assert "approval.human_approval === true" in text
    assert 'LEGACY_LIVE_ARMING_GATE = "human_approved"' in text
    assert "This is not the same as owner sign-off" in text
    assert "human approval is recorded, AND LIVE_TRADING_ENABLED" not in text


def test_existing_owner_approval_and_live_arming_remain_separate_and_safe():
    human = _text(HUMAN_GATE)
    kill = _text(KILL_SWITCH)
    service = _text(APPROVAL_SERVICE)

    assert '"approved": true' in human
    assert '"live_trading_env_flip_authorized": false' in human
    assert '"live_trading_approved": false' in kill
    assert '"human_approval": approved' in service
    assert '"live_trading_env_flip_authorized": bool(gate.get("live_trading_env_flip_authorized"))' in service


def test_ui_does_not_modify_or_offer_live_controls():
    text = _text(COMPONENT)
    assert "read-only" in text
    assert "protected Cloud Run operation enables LIVE" in text
    assert "setLive" not in text
    assert "toggle" not in text.lower()
