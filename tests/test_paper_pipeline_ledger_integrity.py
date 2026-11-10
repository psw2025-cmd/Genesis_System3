"""Regression: real paper pipeline must never hide corrupted ledger or accept NaN quote."""
import json

import pytest

from dashboard.backend.paper_pipeline_v8 import (
    BLOCK_NO_LIVE_QUOTE,
    _append_jsonl_once,
    _load_chain_quote,
)


def test_paper_ledger_rejects_corruption_without_appending(tmp_path):
    ledger = tmp_path / "orders.jsonl"
    ledger.write_text('{"paper_order_id": "one"}\n{invalid-json}\n', encoding="utf-8")
    before = ledger.read_bytes()
    with pytest.raises(json.JSONDecodeError):
        _append_jsonl_once(ledger, {"paper_order_id": "two"}, "paper_order_id")
    assert ledger.read_bytes() == before


def test_paper_ledger_deduplicates_and_rejects_nonfinite_values(tmp_path):
    ledger = tmp_path / "orders.jsonl"
    assert _append_jsonl_once(ledger, {"paper_order_id": "one", "price": 100}, "paper_order_id")
    assert not _append_jsonl_once(ledger, {"paper_order_id": "one", "price": 200}, "paper_order_id")
    before = ledger.read_bytes()
    with pytest.raises(ValueError):
        _append_jsonl_once(ledger, {"paper_order_id": "two", "price": float("nan")}, "paper_order_id")
    assert ledger.read_bytes() == before


@pytest.mark.parametrize("bad_price", ["NaN", "Infinity", "-Infinity", "-1", "0"])
def test_dhan_chain_rejects_invalid_option_quote(tmp_path, bad_price):
    out = tmp_path / "src" / "outputs"
    out.mkdir(parents=True)
    (out / "chain_NIFTY.json").write_text(json.dumps({
        "data_source": "dhan", "source_priority": "dhan_p0_live",
        "status": "MARKET_OPEN", "stale": False,
        "contracts": [{"option_type": "CE", "strike": 25000,
                       "ltp": bad_price, "source": "dhan"}],
    }), encoding="utf-8")
    quote, status = _load_chain_quote(tmp_path, "NIFTY", "CE", 25000)
    assert quote is None
    assert status == BLOCK_NO_LIVE_QUOTE
