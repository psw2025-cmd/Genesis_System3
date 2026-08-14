from pathlib import Path

import pandas as pd

from dashboard.backend import chain_adapter
from dashboard.backend.routers import chain as chain_router


def test_underlyings_are_derived_from_broker_security_master(monkeypatch):
    monkeypatch.setattr(
        chain_router,
        "load_equity_fo_universe",
        lambda: {
            "underlyings": ["RELIANCE", "HDFCBANK", "ZZZTEST"],
            "contract_count": 4321,
            "source": "dhan_security_master",
        },
    )

    import asyncio

    payload = asyncio.run(chain_router.get_underlyings())
    assert "ZZZTEST" in payload["underlyings"]
    assert payload["counts"]["equity_options"] == 3
    assert payload["counts"]["option_contracts"] == 4321
    assert payload["source"] == "dhan_security_master"
    assert payload["broker"] == "DHAN"
    assert payload["read_only"] is True
    assert payload["live_trading_enabled"] is False


def test_chain_adapter_is_full_by_default_and_accepts_expiry(monkeypatch):
    monkeypatch.delenv("CHAIN_MAX_CONTRACTS", raising=False)
    rows = []
    for strike in range(1, 121):
        rows.append({"strike": strike, "option_type": "CE", "oi": 1, "ltp": 1, "expiry_date": "2026-08-27", "source": "dhan"})
        rows.append({"strike": strike, "option_type": "PE", "oi": 1, "ltp": 1, "expiry_date": "2026-08-27", "source": "dhan"})
    df = pd.DataFrame(rows)

    class DSM:
        def __init__(self):
            self.expiry = None

        def fetch_option_chain(self, underlying, expiry=""):
            self.expiry = expiry
            return df, 100.0

    dsm = DSM()
    result = chain_adapter.fetch_chain_for_api(dsm, "NIFTY", expiry="2026-08-27")
    assert dsm.expiry == "2026-08-27"
    assert result["total_contracts"] == 240
    assert result["broker_rows_total"] == 240
    assert result["complete_chain"] is True
    assert result["limited_for_web"] is False
    assert result["max_contracts"] == 0


def test_ui_has_dynamic_broker_discovery_and_full_strikes_default():
    text = Path("dashboard/frontend/src/components/OptionChain.tsx").read_text(encoding="utf-8")
    assert "/api/underlyings" in text
    assert "DHAN UNIVERSE" in text
    assert "EQ OPT" in text
    assert "DISCOVERY DEGRADED" in text
    assert "ALL STRIKES" in text
    assert "NO VERIFIED BROKER CHAIN ROWS" in text
    assert "const SYMBOLS =" not in text
    assert "range === 0 ? strikes" in text
