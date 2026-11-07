"""PAPER-only scanner truth guards; no network or broker orders."""
from datetime import datetime, timedelta, timezone
from dashboard.backend.contract_gain_scanner import scan_segment_contracts

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
