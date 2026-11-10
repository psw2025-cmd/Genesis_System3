"""Regression contract: the API's actionable CE/PE gainer filter must be importable.

No network, broker access, cloud mutations or order calls are performed.
"""
from datetime import datetime, timedelta, timezone

from dashboard.backend.contract_gain_scanner import is_actionable_gainer_row


def _row(**overrides):
    today = datetime.now(timezone(timedelta(hours=5, minutes=30))).date()
    row = {
        "symbol": "NIFTY",
        "trading_symbol": "NIFTY-CE",
        "option_type": "CE",
        "expiry_date": (today + timedelta(days=7)).isoformat(),
        "ltp": 11.5,
        "gain_pct": 42.0,
    }
    row.update(overrides)
    return row


def test_accepts_valid_ce_and_pe():
    assert is_actionable_gainer_row(_row())
    assert is_actionable_gainer_row(_row(option_type="PE"))


def test_rejects_expired_and_missing_expiry():
    today = datetime.now(timezone(timedelta(hours=5, minutes=30))).date()
    assert not is_actionable_gainer_row(_row(expiry_date=(today - timedelta(days=1)).isoformat()))
    assert not is_actionable_gainer_row(_row(expiry_date=None))
    assert not is_actionable_gainer_row(_row(expiry_date="not-a-date"))


def test_rejects_invalid_or_illiquid_unpriced_rows():
    assert not is_actionable_gainer_row(None)
    assert not is_actionable_gainer_row(_row(option_type="FUT"))
    assert not is_actionable_gainer_row(_row(trading_symbol=None, symbol=None))
    assert not is_actionable_gainer_row(_row(ltp=0.01))
    assert not is_actionable_gainer_row(_row(ltp=None))
    assert not is_actionable_gainer_row(_row(ltp=float("nan")))
    assert not is_actionable_gainer_row(_row(ltp=float("inf")))


def test_does_not_mutate_input():
    row = _row()
    before = dict(row)
    assert is_actionable_gainer_row(row)
    assert row == before
