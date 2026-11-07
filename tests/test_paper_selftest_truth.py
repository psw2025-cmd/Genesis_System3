"""Self-test must execute probes and label limited evidence honestly."""
import json

from dashboard.backend.paper_pipeline_v8 import run_self_test


def test_paper_selftest_executes_isolated_probes(tmp_path, monkeypatch):
    for key in ("LIVE_TRADING_ENABLED", "SYSTEM3_LIVE_TRADING_ALLOWED",
                "LIVE_ORDER_AUTHORITY", "REAL_BROKER_ORDERS",
                "AUTO_EXECUTE_TRADES", "USE_LIVE_EXECUTION_ENGINE"):
        monkeypatch.setenv(key, "0")
    result = run_self_test(tmp_path)
    assert result["status"] == "PASS"
    assert result["scope"] == "ISOLATED_OFFLINE_STRUCTURAL_ONLY"
    assert result["full_market_replay_verified"] is False
    assert result["production_ui_verified"] is False
    assert result["real_broker_orders"] == 0
    assert len(result["checks"]) == 4
    assert all(c["passed"] for c in result["checks"])
    assert json.loads((tmp_path / "selftest.json").read_text())["status"] == "PASS"


def test_paper_selftest_fails_when_live_execution_enabled(tmp_path, monkeypatch):
    monkeypatch.setenv("LIVE_ORDER_AUTHORITY", "1")
    result = run_self_test(tmp_path)
    assert result["status"] == "FAIL"
    assert any(c["name"] == "live_execution_environment_disabled"
               and c["passed"] is False for c in result["checks"])
