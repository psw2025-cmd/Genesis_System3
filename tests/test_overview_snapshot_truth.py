from pathlib import Path


OVERVIEW = Path("dashboard/frontend/src/components/Overview.tsx")


def _source() -> str:
    return OVERVIEW.read_text(encoding="utf-8")


def test_overview_does_not_claim_all_market_data_is_waiting_when_spot_exists():
    source = _source()
    assert "c == null ? 'Waiting for market data'" not in source
    assert "Spot snapshot available · change unavailable" in source


def test_overview_does_not_hardcode_no_timeseries_failure_marker():
    source = _source()
    assert "NO TIME-SERIES DATA · SNAPSHOT ONLY" not in source


def test_overview_explicitly_separates_snapshot_from_intraday_history():
    source = _source()
    assert "CURRENT SNAPSHOT AVAILABLE · INTRADAY HISTORY NOT WIRED" in source
    assert "SNAPSHOT UNAVAILABLE · INTRADAY HISTORY NOT WIRED" in source


def test_overview_remains_fail_closed_when_snapshot_is_absent():
    source = _source()
    assert "Market snapshot unavailable" in source
    assert "value={p > 0 ? fmt(p, 2) : '--'}" in source
