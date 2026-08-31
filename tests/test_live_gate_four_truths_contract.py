from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "dashboard" / "frontend" / "src" / "components" / "LiveTradingGate.tsx"
APPROVAL_SERVICE = ROOT / "dashboard" / "backend" / "human_approval_service.py"
HUMAN_GATE = ROOT / "config" / "human_approval_gate.json"
KILL_SWITCH = ROOT / "config" / "kill_switch.json"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_live_gate_renders_four_independent_truths_from_canonical_sources():
    text = _text(COMPONENT)
    for label in ("Execution Mode", "Owner Sign-off", "Technical Readiness", "LIVE Arming"):
        assert label in text
    assert 'fetch("/api/auto_gates")' in text
    assert 'fetch("/api/approval/status")' in text
    assert 'fetch("/api/health")' in text
    assert 'fetch("/api/live-trading/gate")' not in text


def test_owner_signoff_and_live_arming_are_not_inferred_from_each_other():
    text = _text(COMPONENT)
    assert "approval.human_approval === true" in text
    assert "approval.live_trading_env_flip_authorized === true" in text
    assert "independent of owner development/PAPER sign-off" in text
    assert "owner sign-off and LIVE arming are never inferred from each other" in text


def test_technical_readiness_uses_canonical_auto_gate_denominator():
    text = _text(COMPONENT)
    assert "autoGates.gates_passing" in text
    assert "autoGates.gates_total" in text
    assert "autoGates.production_live_ready" in text
    assert "Canonical Technical Readiness Gates" in text
    assert "open_blockers" in text


def test_existing_owner_approval_and_live_arming_remain_separate_and_safe():
    human = _text(HUMAN_GATE)
    kill = _text(KILL_SWITCH)
    service = _text(APPROVAL_SERVICE)

    assert '"approved": true' in human
    assert '"live_trading_env_flip_authorized": false' in human
    assert '"live_trading_approved": false' in kill
    assert '"human_approval": approved' in service
    assert '"live_trading_env_flip_authorized": bool(gate.get("live_trading_env_flip_authorized"))' in service


def test_ui_is_read_only_and_does_not_offer_live_mutation_controls():
    text = _text(COMPONENT)
    assert "read-only" in text
    assert "protected runtime LIVE enablement remain separate controls" in text
    assert "setLive" not in text
    assert "toggle" not in text.lower()
