"""Offline state contract: absence of source evidence never means market CLOSED."""
import json

import pytest

from dashboard.backend.runtime_state_store import RuntimeStateStore


def test_initial_market_is_unknown(tmp_path):
    state = RuntimeStateStore(tmp_path).get_state()
    assert state["market"]["is_open"] is None
    assert "UNKNOWN" in state["market"]["reason"]


@pytest.mark.parametrize("source,expected", [(None, None), ("", None), ("stale", None),
                                             ("open", True), ("closed", False)])
def test_only_explicit_source_status_changes_market_state(tmp_path, monkeypatch, source, expected):
    store = RuntimeStateStore(tmp_path)
    monkeypatch.setattr(store, "_save_state", lambda: None)
    (tmp_path / "health.json").write_text(json.dumps({"market_status": source, "is_connected": True}))
    store.sync_from_files()
    state = store.get_state()
    assert state["market"]["is_open"] is expected
    assert state["broker"]["last_ok"] is None


def test_missing_health_clears_previous_open_claim(tmp_path, monkeypatch):
    store = RuntimeStateStore(tmp_path)
    monkeypatch.setattr(store, "_save_state", lambda: None)
    store.update_state({"market": {"is_open": True, "reason": "open"}})
    store.sync_from_files()
    assert store.get_state()["market"]["is_open"] is None
