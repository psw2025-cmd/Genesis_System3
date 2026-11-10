"""Eval: fail-closed audit of Gmail/export signal-plan CSVs.

Never invent prices or approve LIVE/order actions from a spreadsheet.
"""

from __future__ import annotations

from pathlib import Path

from dashboard.backend.signal_plan_audit import (
    REQUIRED_TRADE_COLUMNS,
    audit_signal_plan_csv,
    audit_signal_plan_texts,
)

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"
TRADE_CSV = FIXTURE_DIR / "system3_signal_candidates_sample.csv"
REC_CSV = FIXTURE_DIR / "system3_plan_recommendations_sample.csv"
SCANNER_CSV = FIXTURE_DIR / "system3_scanner_gainers_sample.csv"


def test_required_trade_columns_match_gmail_preview():
    assert REQUIRED_TRADE_COLUMNS == {"symbol", "entry", "stoploss", "target"}


def test_audit_flags_invalid_geometry_and_zero_prices():
    report = audit_signal_plan_csv(TRADE_CSV)
    assert report["schema"] == "signal_plan_audit_v1"
    assert report["safety"]["live_trading_enabled"] is False
    assert report["safety"]["order_placement_allowed"] is False
    assert report["row_count"] == 5
    assert report["invented_prices"] is False
    ids = {f["code"] for f in report["findings"]}
    assert "INVALID_GEOMETRY" in ids
    assert "NON_POSITIVE_PRICE" in ids
    assert report["summary"]["valid_rows"] >= 1
    assert report["summary"]["invalid_rows"] >= 2


def test_audit_flags_live_enablement_language():
    report = audit_signal_plan_csv(REC_CSV)
    codes = {f["code"] for f in report["findings"]}
    assert "LIVE_OR_ORDER_LANGUAGE" in codes
    assert report["safety"]["live_trading_enabled"] is False


def test_audit_missing_file_fail_closed(tmp_path):
    report = audit_signal_plan_csv(tmp_path / "missing.csv")
    assert report["ok"] is False
    assert report["error"] == "FILE_NOT_FOUND"
    assert report["invented_prices"] is False


def test_scanner_csv_flags_tiny_premium_extreme_gain():
    report = audit_signal_plan_csv(SCANNER_CSV)
    assert report["ok"] is True
    assert report["invented_prices"] is False
    codes = {f["code"] for f in report["findings"]}
    assert "TINY_PREMIUM_EXTREME_GAIN" in codes
    assert "MISSING_COLUMNS" not in codes
    sensex_tiny = next(r for r in report["rows"] if r["symbol"] == "SENSEX" and r["ltp"] == 2.25)
    assert sensex_tiny["gain_pct"] == 4400.0


def test_plan_issue_schema_is_not_a_trade_sheet():
    report = audit_signal_plan_texts(
        [
            "issue_id,priority,observed_evidence,recommendation",
            "M032,P0,SENSEX 4400% on 2.25 LTP,Keep NO_TRADE until quality filters exist",
        ]
    )
    assert report["ok"] is True
    assert "MISSING_COLUMNS" not in {f["code"] for f in report["findings"]}


def test_audit_texts_do_not_synthesize_missing_pnl():
    report = audit_signal_plan_texts(
        [
            "symbol,entry,stoploss,target,pnl",
            "NIFTY25AUG25000CE,100,90,130,",
        ]
    )
    row = report["rows"][0]
    assert row["pnl"] is None
    assert "SYNTHETIC_PNL" not in {f["code"] for f in report["findings"]}
