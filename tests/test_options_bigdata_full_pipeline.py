import os

import pytest

from scripts.options_bigdata_full_pipeline import ensure_analyzer_only


def test_full_pipeline_blocks_live_flags(monkeypatch):
    monkeypatch.setenv("LIVE_TRADING_ENABLED", "1")
    with pytest.raises(RuntimeError):
        ensure_analyzer_only()
    monkeypatch.setenv("LIVE_TRADING_ENABLED", "0")
    monkeypatch.setenv("SYSTEM3_LIVE_TRADING_ALLOWED", "true")
    with pytest.raises(RuntimeError):
        ensure_analyzer_only()
