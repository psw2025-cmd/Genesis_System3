from datetime import date
from pathlib import Path

import pandas as pd

from scripts.options_bigdata_download import (
    Manifest,
    RollingRequest,
    Underlying,
    build_plan,
    flatten_rolling_response,
    load_universe,
    relative_strikes,
    verify_data,
    write_frame,
)


def test_relative_strikes_index_and_stock():
    assert len(relative_strikes("OPTIDX", 0)) == 21
    assert len(relative_strikes("OPTIDX", 1)) == 7
    assert len(relative_strikes("OPTSTK", 0)) == 7
    assert set(relative_strikes("OPTSTK", 0)) == {"ATM", "ATM+1", "ATM-1", "ATM+2", "ATM-2", "ATM+3", "ATM-3"}


def test_plan_exact_request_count():
    universe = [Underlying("NIFTY", "13", "OPTIDX"), Underlying("RELIANCE", "2885", "OPTSTK")]
    plan = build_plan(universe, date(2026, 1, 1), date(2026, 1, 31), interval="5")
    assert len(plan) == 182
    assert len({req.key for req in plan}) == 182


def test_load_detailed_security_master_deduplicates_nse_and_bse(tmp_path: Path):
    csv_path = tmp_path / "master.csv"
    csv_path.write_text(
        "EXCH_ID,SEGMENT,INSTRUMENT,UNDERLYING_SYMBOL,UNDERLYING_SECURITY_ID,SYMBOL_NAME\n"
        "NSE,D,OPTSTK,RELIANCE,2885,RELIANCE\n"
        "NSE,D,OPTSTK,RELIANCE,2885,RELIANCE\n"
        "NSE,D,OPTIDX,NIFTY,13,NIFTY\n"
        "BSE,D,OPTIDX,SENSEX,51,SENSEX\n"
        "NSE,E,EQUITY,RELIANCE,2885,RELIANCE\n",
        encoding="utf-8",
    )
    values = load_universe(csv_path)
    assert [(v.exchange_segment, v.symbol, v.instrument) for v in values] == [
        ("BSE_FNO", "SENSEX", "OPTIDX"),
        ("NSE_FNO", "NIFTY", "OPTIDX"),
        ("NSE_FNO", "RELIANCE", "OPTSTK"),
    ]


def test_flatten_rolling_response():
    req = RollingRequest(Underlying("NIFTY", "13", "OPTIDX"), date(2026, 1, 1), date(2026, 1, 2), "WEEK", 0, "ATM", "CALL", "1")
    payload = {"data": {"ce": {"timestamp": [1, 2], "open": [10, 11], "high": [12, 13], "low": [9, 10], "close": [11, 12], "iv": [0.2, 0.21], "volume": [100, 110], "strike": [24000, 24000], "oi": [1000, 1100], "spot": [24010, 24020]}}}
    frame = flatten_rolling_response(req, payload)
    assert len(frame) == 2
    assert frame.loc[0, "exchange_segment"] == "NSE_FNO"
    assert frame.loc[0, "option_type"] == "CALL"
    assert frame.loc[1, "oi"] == 1100


def register(manifest: Manifest, output: Path, source: str, rows: int):
    from scripts.options_bigdata_download import sha256_file
    manifest.upsert(
        object_key=source, source=source, symbol="NIFTY", start_date="2026-01-01", end_date="2026-01-02",
        status="DOWNLOADED", rows=rows, bytes=output.stat().st_size, sha256=sha256_file(output), path=str(output),
        http_status=200, error="", updated_utc="2026-01-02T00:00:00Z",
    )


def test_verify_data_detects_clean_partition(tmp_path: Path):
    data_root = tmp_path / "data"
    frame = pd.DataFrame({
        "timestamp": [1, 2], "underlying": ["NIFTY", "NIFTY"], "option_type": ["CALL", "CALL"],
        "open": [10, 11], "high": [12, 13], "low": [9, 10], "close": [11, 12],
        "iv": [0.2, 0.21], "volume": [100, 110], "strike": [24000, 24000],
        "oi": [1000, 1100], "spot": [24010, 24020],
    })
    output = write_frame(frame, data_root / "dhan_rolling" / "clean.parquet")
    manifest = Manifest(data_root / "manifest.sqlite3")
    register(manifest, output, "DHAN_ROLLING", 2)
    result = verify_data(data_root, manifest)
    assert result["status"] == "PASS"
    assert result["files_checked"] == 1
    assert result["rows_checked"] == 2
    assert result["traded_rows_checked"] == 2
    assert result["no_trade_rows"] == 0


def test_verify_udiff_schema_quarantines_bad_traded_future_high(tmp_path: Path):
    data_root = tmp_path / "data"
    frame = pd.DataFrame({
        "FinInstrmTp": ["STF", "STF"],
        "OpnPric": [10, 11], "HghPric": [12, 10], "LwPric": [9, 9], "ClsPric": [11, 12],
        "TtlTradgVol": [100, 110], "OpnIntrst": [1000, 1100],
    })
    output = write_frame(frame, data_root / "nse_fo_eod" / "bad.parquet")
    manifest = Manifest(data_root / "manifest.sqlite3")
    register(manifest, output, "NSE_FO_EOD", 2)
    result = verify_data(data_root, manifest)
    assert result["status"] == "PASS_WITH_QUARANTINE"
    assert result["quarantined_invalid_market_rows"] == 1
    assert result["invalid_traded_futures_ohlc_rows"] == 1
    assert result["invalid_traded_option_ohlc_rows"] == 0
    assert result["partial_traded_ohlc_rows"] == 0
    assert result["structural_failure_count"] == 0
    assert result["missing_ohlc_schema_files"] == 0
    assert result["missing_volume_oi_schema_files"] == 0


def test_verify_allows_zero_ohlc_for_no_trade_contract(tmp_path: Path):
    data_root = tmp_path / "data"
    frame = pd.DataFrame({
        "OpnPric": [0], "HghPric": [0], "LwPric": [0], "ClsPric": [25.5],
        "TtlTradgVol": [0], "OpnIntrst": [450],
    })
    output = write_frame(frame, data_root / "nse_fo_eod" / "no_trade.parquet")
    manifest = Manifest(data_root / "manifest.sqlite3")
    register(manifest, output, "NSE_FO_EOD", 1)
    result = verify_data(data_root, manifest)
    assert result["status"] == "PASS"
    assert result["traded_rows_checked"] == 0
    assert result["no_trade_rows"] == 1
    assert result["quarantined_invalid_market_rows"] == 0
    assert result["partial_traded_ohlc_rows"] == 0


def test_manifest_preserves_completed_status_for_resume(tmp_path: Path):
    manifest = Manifest(tmp_path / "manifest.sqlite3")
    manifest.upsert(
        object_key="done", source="DHAN_ROLLING", symbol="NIFTY", start_date="2026-01-01", end_date="2026-01-02",
        status="NO_DATA", rows=0, bytes=0, sha256="", path="", http_status=200,
        error="EMPTY_SERIES", updated_utc="2026-01-02T00:00:00Z",
    )
    assert manifest.status("done") == "NO_DATA"
