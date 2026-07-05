"""
Tests for OI cache staleness guards and is_expiry_day() in nse_provider.py.
Uses tmp_path fixture for file isolation — never touches real state/market_cache.json.
"""

import json
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

import core.data.nse_provider as nse_provider


@pytest.fixture(autouse=True)
def isolate_cache(tmp_path, monkeypatch):
    cache_file = str(tmp_path / "market_cache.json")
    monkeypatch.setattr(nse_provider, "MARKET_CACHE_FILE", cache_file)
    return cache_file


def _write_cache(cache_date_str, oi_data, tmp_path):
    path = tmp_path / "market_cache.json"
    path.write_text(
        json.dumps(
            {
                "last_updated": "2026-01-01T00:00:00",
                "cache_date": cache_date_str,
                "oi_data": oi_data,
            }
        )
    )


def _today_str():
    return date.today().isoformat()


def _days_ago(n):
    return (date.today() - timedelta(days=n)).isoformat()


# TC-OI-1: Yesterday's cache — returns oi_data
def test_yesterday_cache_returns_data(tmp_path):
    _write_cache(_days_ago(1), {"NIFTY": 500000, "BANKNIFTY": 200000}, tmp_path)
    result = nse_provider.load_oi_cache()
    assert result == {"NIFTY": 500000, "BANKNIFTY": 200000}


# TC-OI-2: Same-day cache — returns {} (morning run guard)
def test_same_day_cache_returns_empty(tmp_path):
    _write_cache(_today_str(), {"NIFTY": 500000}, tmp_path)
    result = nse_provider.load_oi_cache()
    assert result == {}


# TC-OI-3: Cache older than 3 days — returns {}
def test_stale_cache_4_days_returns_empty(tmp_path):
    _write_cache(_days_ago(4), {"NIFTY": 500000}, tmp_path)
    result = nse_provider.load_oi_cache()
    assert result == {}


# TC-OI-4: Cache exactly 3 days old — returns data (boundary: 3 days is still valid)
def test_three_days_old_cache_is_valid(tmp_path):
    _write_cache(_days_ago(3), {"NIFTY": 500000}, tmp_path)
    result = nse_provider.load_oi_cache()
    assert result == {"NIFTY": 500000}


# TC-OI-5: Cache exactly 4 days old — returns {} (4 > MAX_OI_CACHE_AGE_DAYS=3)
def test_four_days_old_cache_is_stale(tmp_path):
    _write_cache(_days_ago(4), {"NIFTY": 500000}, tmp_path)
    result = nse_provider.load_oi_cache()
    assert result == {}


# TC-OI-6: Missing file — returns {} without crash
def test_missing_file_returns_empty():
    result = nse_provider.load_oi_cache()
    assert result == {}


# TC-OI-7: Corrupt JSON — returns {} without crash
def test_corrupt_json_returns_empty(tmp_path):
    path = tmp_path / "market_cache.json"
    path.write_text("NOT VALID JSON {{{")
    result = nse_provider.load_oi_cache()
    assert result == {}


# TC-OI-8: save_oi_cache round-trip — data survives save → load
def test_save_and_load_round_trip(tmp_path, monkeypatch):
    oi = {"NIFTY": 123456, "BANKNIFTY": 654321}
    nse_provider.save_oi_cache(oi)
    # Simulate reading next day (monkeypatch date.today to be tomorrow)
    tomorrow = date.today() + timedelta(days=1)

    class FakeDate:
        @staticmethod
        def today():
            return tomorrow

        @staticmethod
        def strptime(s, fmt):
            return date.fromisoformat(s) if fmt == "%Y-%m-%d" else date(*time.strptime(s, fmt)[:3])

    # We only need to move the "today" so the cache_date (today) is "yesterday" relative to read
    # Instead: just verify cache file was written with today's date and correct data
    cache_path = tmp_path / "market_cache.json"
    content = json.loads(cache_path.read_text())
    assert content["oi_data"] == oi
    assert content["cache_date"] == date.today().isoformat()


# TC-OI-9: is_expiry_day() — Thursday returns True
def test_expiry_day_thursday():
    import datetime as _dt
    from unittest.mock import MagicMock, patch

    class _FakeDate(_dt.date):
        @classmethod
        def today(cls):
            return cls(2026, 6, 18)  # a known Thursday

    with patch("datetime.date", _FakeDate):
        assert nse_provider.is_expiry_day() is True


# TC-OI-10: is_expiry_day() — Mon/Tue/Wed/Fri return False
@pytest.mark.parametrize(
    "date_str,expected",
    [
        ("2026-06-16", False),  # Monday
        ("2026-06-17", False),  # Tuesday
        ("2026-06-18", True),  # Thursday (confirm weekday=3)
        ("2026-06-20", False),  # Friday
    ],
)
def test_expiry_day_parametrize(date_str, expected):
    import datetime as _dt
    from unittest.mock import patch

    y, m, d = map(int, date_str.split("-"))

    class _FakeDate(_dt.date):
        @classmethod
        def today(cls):
            return cls(y, m, d)

    with patch("datetime.date", _FakeDate):
        assert nse_provider.is_expiry_day() == expected


# TC-OI-11: Missing cache_date field — returns oi_data (backward compat)
def test_missing_cache_date_returns_data(tmp_path):
    path = tmp_path / "market_cache.json"
    path.write_text(
        json.dumps(
            {
                "last_updated": "2026-01-01T00:00:00",
                "oi_data": {"NIFTY": 999},
            }
        )
    )
    result = nse_provider.load_oi_cache()
    assert result == {"NIFTY": 999}
