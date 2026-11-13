from dashboard.backend.phase1_safe_gates import gate_model_prediction, gate_model_state, public_url_for_runtime


def test_cloud_public_url_never_exposes_loopback():
    assert public_url_for_runtime("http://127.0.0.1:8000", on_cloud_run=True).startswith("https://genesis-system3-web-")
    assert public_url_for_runtime("http://localhost:8000", on_cloud_run=True).startswith("https://genesis-system3-web-")
    assert public_url_for_runtime("http://127.0.0.1:8000", on_cloud_run=False) == "http://127.0.0.1:8000"
    assert public_url_for_runtime("https://example.run.app", on_cloud_run=True) == "https://example.run.app"


def test_zero_models_fail_closed_even_if_row_claims_trade():
    row = {"symbol": "NIFTY", "model_loaded": True, "recommendation": "TRADE", "signal": "BUY_CE", "confidence_pct": 99.54}
    result = gate_model_prediction(row, loaded_model_count=0)
    assert result == {"symbol": "NIFTY", "model_loaded": False, "recommendation": "WAIT", "signal": "HOLD", "confidence_pct": 0.0}
    assert row["recommendation"] == "TRADE"


def test_missing_symbol_model_fails_closed_with_other_models_present():
    row = {"model_loaded": False, "recommendation": "TRADE", "confidence_pct": 83.96}
    result = gate_model_prediction(row, loaded_model_count=5)
    assert (result["recommendation"], result["confidence_pct"]) == ("WAIT", 0.0)


def test_state_zero_models_does_not_expose_trade_and_preserves_original():
    state = {"model": {"metrics": {"models_loaded": 0}}, "signals": {"confidence": 99.54, "last_signal": {"action": "TRADE", "signal": "BUY_CE"}}, "ml_predictions": [{"model_loaded": True, "recommendation": "TRADE", "confidence_pct": 99.54}]}
    result = gate_model_state(state)
    assert result["signals"]["last_signal"]["action"] == "WAIT"
    assert result["signals"]["confidence"] == 0.0
    assert result["ml_predictions"][0]["recommendation"] == "WAIT"
    assert state["signals"]["last_signal"]["action"] == "TRADE"
