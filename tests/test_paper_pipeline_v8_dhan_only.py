import json

from dashboard.backend.paper_pipeline_v8 import BLOCK_NO_LIVE_QUOTE, _load_chain_quote


def _write_chain(tmp_path, underlying, payload):
    out = tmp_path / "src" / "outputs"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"chain_{underlying}.json").write_text(json.dumps(payload), encoding="utf-8")


def test_paper_quote_accepts_dhan_only(tmp_path):
    _write_chain(
        tmp_path,
        "NIFTY",
        {
            "underlying": "NIFTY",
            "spot": 25000,
            "data_source": "dhan",
            "source_priority": "dhan_p0_live",
            "status": "MARKET_OPEN",
            "stale": False,
            "contracts": [
                {"option_type": "CE", "strike": 25000, "ltp": 101.5, "source": "dhan"},
            ],
        },
    )

    quote, status = _load_chain_quote(tmp_path, "NIFTY", "CE", 25000)

    assert status == "OK"
    assert quote is not None
    assert quote["ltp"] == 101.5
    assert quote["chain_data_source"] == "dhan"


def test_paper_quote_blocks_csv_fallback_even_with_ltp(tmp_path):
    _write_chain(
        tmp_path,
        "BANKNIFTY",
        {
            "underlying": "BANKNIFTY",
            "spot": 58417,
            "data_source": "csv_fallback",
            "source_priority": "csv_fallback_after_live_fetch_failed",
            "status": "STALE_CSV_FALLBACK",
            "stale": True,
            "contracts": [
                {"option_type": "CE", "strike": 58400, "ltp": 100.0, "source": "csv"},
            ],
        },
    )

    quote, status = _load_chain_quote(tmp_path, "BANKNIFTY", "CE", 58417)

    assert quote is None
    assert status == BLOCK_NO_LIVE_QUOTE


def test_paper_quote_blocks_synthetic_even_if_not_stale(tmp_path):
    _write_chain(
        tmp_path,
        "FINNIFTY",
        {
            "underlying": "FINNIFTY",
            "spot": 24000,
            "data_source": "synthetic",
            "source_priority": "synthetic",
            "status": "MARKET_OPEN",
            "stale": False,
            "contracts": [
                {"option_type": "PE", "strike": 24000, "ltp": 88.0, "source": "synthetic"},
            ],
        },
    )

    quote, status = _load_chain_quote(tmp_path, "FINNIFTY", "PE", 24000)

    assert quote is None
    assert status == BLOCK_NO_LIVE_QUOTE
