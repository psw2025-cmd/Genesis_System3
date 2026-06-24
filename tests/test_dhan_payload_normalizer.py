"""Tests for Dhan payload normalizer."""

from core.brokers.dhan.dhan_payload_normalizer import (
    normalize_funds_payload,
    normalize_funds_row,
    normalize_holding_row,
    normalize_holdings_payload,
    normalize_position_row,
    normalize_positions_payload,
)


def test_normalize_holdings_list():
    raw = [{"tradingSymbol": "RELIANCE", "totalQty": 10, "avgCostPrice": 2500, "lastTradedPrice": 2600}]
    rows = normalize_holdings_payload(raw)
    assert len(rows) == 1
    norm = normalize_holding_row(rows[0])
    assert norm["symbol"] == "RELIANCE"
    assert norm["quantity"] == 10
    assert norm["pnl"] == 1000


def test_normalize_funds_dhan_typo_field():
    raw = {"availabelBalance": 50000, "utilizedAmount": 12000}
    norm = normalize_funds_row(normalize_funds_payload(raw))
    assert norm["available_balance"] == 50000
    assert norm["utilized_amount"] == 12000


def test_normalize_positions_fno_symbol():
    raw = {"data": [{"tradingSymbol": "NIFTY05FEB2623500CE", "netQty": 50, "unrealizedProfit": -200}]}
    rows = normalize_positions_payload(raw)
    assert len(rows) == 1
    norm = normalize_position_row(rows[0])
    assert norm["trading_symbol"] == "NIFTY05FEB2623500CE"
    assert norm["underlying"] == "NIFTY"
    assert norm["strike"] == 23500.0
    assert norm["option_type"] == "CE"
    assert norm["unrealized_pnl"] == -200
