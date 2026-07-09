from dashboard.backend.middleware.memory_guard import _blocked_chain_payload, _chain_response_is_dhan_only


def test_dhan_chain_payload_allowed():
    payload = {
        "underlying": "BANKNIFTY",
        "spot": 58417,
        "contracts": [{"source": "dhan", "strike": 58400, "option_type": "CE", "ltp": 100, "oi": 1}],
        "total_contracts": 1,
        "data_source": "dhan",
        "source_priority": "dhan_p0_live",
        "status": "MARKET_OPEN",
        "stale": False,
    }

    assert _chain_response_is_dhan_only(payload) is True


def test_csv_fallback_chain_payload_blocked():
    payload = {
        "underlying": "BANKNIFTY",
        "spot": 58417,
        "contracts": [{"source": "csv", "strike": 58400, "option_type": "CE", "ltp": 100, "oi": 1}],
        "total_contracts": 224,
        "data_source": "csv_fallback",
        "source_priority": "csv_fallback_after_live_fetch_failed",
        "status": "STALE_CSV_FALLBACK",
        "stale": True,
    }

    assert _chain_response_is_dhan_only(payload) is False
    blocked = _blocked_chain_payload(payload)
    assert blocked["status"] == "NO_DHAN_DATA"
    assert blocked["blocked"] is True
    assert blocked["contracts"] == []
    assert blocked["spot"] == 0
    assert blocked["data_source"] == "dhan"


def test_synthetic_chain_payload_blocked():
    payload = {
        "underlying": "NIFTY",
        "spot": 25000,
        "contracts": [{"source": "synthetic", "strike": 25000, "option_type": "PE", "ltp": 1, "oi": 1}],
        "total_contracts": 1,
        "data_source": "synthetic",
        "source_priority": "synthetic",
        "status": "MARKET_CLOSED",
        "stale": False,
    }

    assert _chain_response_is_dhan_only(payload) is False


def test_empty_dhan_payload_blocked_not_displayed_as_real():
    payload = {
        "underlying": "FINNIFTY",
        "spot": 0,
        "contracts": [],
        "total_contracts": 0,
        "data_source": "dhan",
        "source_priority": "dhan_only_no_fallback",
        "status": "NO_DHAN_DATA",
        "stale": False,
    }

    assert _chain_response_is_dhan_only(payload) is False
