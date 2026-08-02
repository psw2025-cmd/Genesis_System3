import json

from dashboard.backend.runtime_state_store import RuntimeStateStore


def test_local_backend_remains_default_and_forces_paper(monkeypatch, tmp_path):
    monkeypatch.delenv("SYSTEM3_STATE_BACKEND", raising=False)
    store = RuntimeStateStore(tmp_path)

    store.update_state({"mode": "LIVE", "live_trading_enabled": True})
    state = store.get_state()

    assert state["mode"] == "PAPER"
    assert state["live_trading_enabled"] is False
    assert state["safety"]["execution_mode"] == "ANALYZER"
    assert json.loads((tmp_path / "runtime_state.json").read_text())["mode"] == "PAPER"
