"""PAPER-only scanner truth guards; no network or broker orders."""
from datetime import datetime, timedelta, timezone
from dashboard.backend.contract_gain_scanner import scan_segment_contracts, merge_market_top_reports, scan_all_segments_from_chains

def _contract(**overrides):
    today = datetime.now(timezone(timedelta(hours=5, minutes=30))).date()
    row = {"option_type": "CE", "trading_symbol": "NIFTY-CE", "expiry_date": (today + timedelta(days=7)).isoformat(), "ltp": 12, "previous_close": 6, "volume": 100}
    row.update(overrides)
    return row

def test_rejects_expired_contract_even_when_gain_is_high():
    today = datetime.now(timezone(timedelta(hours=5, minutes=30))).date()
    result = scan_segment_contracts([_contract(expiry_date=(today - timedelta(days=1)).isoformat())], "NIFTY")
    assert result["contracts_scored"] == 0
    assert result["top_ce"] is None

def test_rejects_missing_expiry_and_invalid_volume():
    rows = [_contract(expiry_date=None), _contract(volume="bad")]
    result = scan_segment_contracts(rows, "NIFTY")
    assert result["contracts_scored"] == 0

def test_valid_row_is_ranked_without_false_live_proof():
    result = scan_segment_contracts([_contract()], "NIFTY")
    assert result["contracts_scored"] == 1
    row = result["top_ce"]
    assert row["data_provenance"] == "UNVERIFIED"
    assert "LIVE" not in row["market_match_note"]
    assert row["gain_pct"] == 100.0

def test_no_mutation_and_default_expiry():
    row = _contract(expiry_date=None)
    original = dict(row)
    today = datetime.now(timezone(timedelta(hours=5, minutes=30))).date()
    result = scan_segment_contracts([row], "NIFTY", default_expiry=(today + timedelta(days=7)).isoformat())
    assert result["contracts_scored"] == 1
    assert row == original

def test_nonfinite_prices_and_gains_are_not_ranked():
    for invalid in (float("nan"), float("inf"), float("-inf")):
        result = scan_segment_contracts([_contract(ltp=invalid)], "NIFTY")
        assert result["contracts_scored"] == 0
        result = scan_segment_contracts([_contract(previous_close=invalid)], "NIFTY")
        assert result["contracts_scored"] == 0

def test_valid_pe_and_ce_both_ranked():
    result = scan_segment_contracts([_contract(), _contract(option_type="PE", trading_symbol="NIFTY-PE")], "NIFTY")
    assert result["contracts_scored"] == 2
    assert result["top_ce"]["option_type"] == "CE"
    assert result["top_pe"]["option_type"] == "PE"

def test_merge_rejects_expired_and_nonfinite_stale_rows():
    today = datetime.now(timezone(timedelta(hours=5, minutes=30))).date()
    valid = dict(_contract(), underlying="NIFTY", gain_pct=100.0)
    expired = dict(_contract(expiry_date=(today - timedelta(days=1)).isoformat()), underlying="NIFTY", gain_pct=99999.0)
    nan_row = dict(_contract(trading_symbol="NIFTY-PE", option_type="PE"), underlying="NIFTY", gain_pct=float("nan"))
    result = merge_market_top_reports(
        {"market_top_table": [expired, nan_row], "chains_fetched": []},
        {"market_top_table": [valid], "chains_fetched": []},
    )
    assert len(result["market_top_table"]) == 1
    assert result["market_top_table"][0]["gain_pct"] == 100.0

def test_merge_rejects_missing_expiry_and_invalid_gain():
    valid = dict(_contract(), underlying="NIFTY", gain_pct=42.0)
    missing = dict(_contract(expiry_date=None), underlying="NIFTY", gain_pct=999.0)
    invalid = dict(_contract(trading_symbol="NIFTY-PE", option_type="PE"), underlying="NIFTY", gain_pct="broken")
    result = merge_market_top_reports(
        {"market_top_table": [missing, invalid]},
        {"market_top_table": [valid]},
    )
    assert [row["gain_pct"] for row in result["market_top_table"]] == [42.0]

def test_malformed_contract_items_do_not_crash_or_hide_valid_ce():
    result = scan_segment_contracts([None, "bad", 123, [], _contract()], "NIFTY")
    assert result["contracts_scored"] == 1
    assert result["top_ce"]["gain_pct"] == 100.0

def test_negative_volume_is_never_ranked_even_without_volume_floor():
    result = scan_segment_contracts([_contract(volume=-1), _contract(option_type="PE", trading_symbol="NIFTY-PE", volume=0)], "NIFTY", min_volume=0)
    assert result["contracts_scored"] == 1
    assert result["top_ce"] is None
    assert result["top_pe"] is not None

def test_nonobject_chain_payload_is_reported_without_crashing():
    result = scan_all_segments_from_chains({"NIFTY": "bad", "BANKNIFTY": None})
    assert result["contracts_scored_total"] == 0
    assert result["by_underlying"]["NIFTY"]["status"] == "INVALID_CHAIN_PAYLOAD"
    assert result["by_underlying"]["BANKNIFTY"]["top_ce"] is None

def test_nonlist_contracts_payload_is_not_iterated_as_valid_rows():
    result = scan_all_segments_from_chains({"NIFTY": {"contracts": {"CE": _contract()}}})
    assert result["contracts_scored_total"] == 0
    assert result["by_underlying"]["NIFTY"]["status"] == "INVALID_CONTRACTS_PAYLOAD"

def test_top_level_malformed_chain_collection_fails_closed():
    for payload in (None, [], "bad", 123):
        result = scan_all_segments_from_chains(payload)
        assert result["contracts_scored_total"] == 0
        assert result["underlyings_scanned"] == 0
        assert result["market_wide"]["top_ce"] is None
        assert result["market_wide"]["top_pe"] is None
