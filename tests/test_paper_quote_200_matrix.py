"""200 actual PAPER quote scenarios: 10 source labels x 20 premiums.

This is offline input-validation coverage, not 200 bugs or market-day replay.
"""
import json
import pytest
from dashboard.backend.paper_pipeline_v8 import _load_chain_quote, BLOCK_NO_LIVE_QUOTE

SOURCES = ["dhan", "csv", "synthetic", "manual", "unknown", "", "DHAN",
           "dhan_fallback", "nse", "yahoo"]
PREMIUMS = [
    (100, True), (0, False), (-1, False), (None, False),
    ("nan", False), ("inf", False), ("-inf", False),
    ("", False), ("bad", False), ("1e309", False),
    (0.01, True), (9999.5, True), ("101.5", True),
    ("-0.01", False), ("0", False), ("Infinity", False),
    (float("nan"), False), (float("inf"), False),
    (1, True), ("2.5", True),
]

@pytest.mark.parametrize("source", SOURCES)
@pytest.mark.parametrize("premium,valid_price", PREMIUMS)
def test_200_source_price_matrix(tmp_path, source, premium, valid_price):
    out = tmp_path / "src" / "outputs"
    out.mkdir(parents=True)
    (out / "chain_NIFTY.json").write_text(json.dumps({
        "data_source": "dhan", "source_priority": "dhan_p0_live",
        "status": "MARKET_OPEN", "stale": False,
        "contracts": [{"source": source, "option_type": "CE",
                       "strike": 25000, "ltp": premium}],
    }))
    quote, reason = _load_chain_quote(tmp_path, "NIFTY", "CE", 25000)
    allowed = source.lower() == "dhan" and valid_price
    if allowed:
        assert reason == "OK" and quote is not None
    else:
        assert quote is None and reason == BLOCK_NO_LIVE_QUOTE

@pytest.mark.parametrize("source_fields", [
    {}, {"source": None}, {"source": ""}, {"data_source": "unknown"},
    {"quote_source": "manual"},
])
def test_missing_or_implicit_dhan_provenance_is_rejected(tmp_path, source_fields):
    out = tmp_path / "src" / "outputs"
    out.mkdir(parents=True)
    (out / "chain_NIFTY.json").write_text(json.dumps({
        "data_source": "dhan", "status": "MARKET_OPEN", "stale": False,
        "contracts": [{"option_type": "CE", "strike": 25000,
                       "ltp": 100, **source_fields}],
    }))
    quote, reason = _load_chain_quote(tmp_path, "NIFTY", "CE", 25000)
    assert quote is None and reason == BLOCK_NO_LIVE_QUOTE
