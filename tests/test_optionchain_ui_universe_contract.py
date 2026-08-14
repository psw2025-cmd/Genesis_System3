from pathlib import Path

import asyncio
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
    payload = asyncio.run(chain_router.get_underlyings())
    assert "ZZZTEST" in payload["underlyings"]
    assert payload["counts"]["equity_options"] == 3
    assert payload["counts"]["option_contracts"] == 4321
    assert payload["source"] == "dhan_security_master"
    assert payload["broker"] == "DHAN"
    assert payload["read_only"] is True
    assert payload["live_trading_enabled"] is False
    assert payload["expiry_endpoint"] == "/api/expiries/{underlying}"


def test_expiry_discovery_returns_all_broker_master_expiries(monkeypatch):
    monkeypatch.setattr(
        chain_router,
        "_expiry_map",
        lambda: {"RELIANCE": ["2026-08-27", "2026-09-24", "2026-10-29"]},
    )
    payload = asyncio.run(chain_router.get_expiries("reliance"))
    assert payload["underlying"] == "RELIANCE"
    assert payload["expiries"] == ["2026-08-27", "2026-09-24", "2026-10-29"]
    assert payload["count"] == 3
    assert payload["source"] == "dhan_security_master"
    assert payload["broker"] == "DHAN"
    assert payload["read_only"] is True
    assert payload["live_trading_enabled"] is False


def test_sensex_expiries_resolve_from_trading_symbol_not_bsxopt():
    chain_router._expiry_map.cache_clear()
    row = {
        "SEM_TRADING_SYMBOL": "SENSEX-Aug2026-78000-CE",
        "SEM_CUSTOM_SYMBOL": "SENSEX 14 AUG 78000 CALL",
        "SM_SYMBOL_NAME": "BSXOPT",
    }
    assert chain_router.underlying_from_master_row(row) == "SENSEX"
    payload = asyncio.run(chain_router.get_expiries("SENSEX"))
    assert payload["underlying"] == "SENSEX"
    assert payload["count"] >= 1
    assert payload["status"] == "OK"
    assert any(str(x).startswith("2026-") for x in payload["expiries"])


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
    assert result["requested_expiry"] == "2026-08-27"
    assert result["live_trading_enabled"] is False


def test_install_legacy_bridge_registers_expiry_routes_after_app_exists():
    from fastapi import FastAPI

    class Parent:
        app = FastAPI()
        DEFAULT_UNDERLYINGS = ["NIFTY"]
        SYSTEM3_UNDERLYINGS_METADATA = {}

    parent = Parent()

    def _fake_legacy():
        return parent

    old = chain_router._legacy_app_module
    chain_router._legacy_app_module = _fake_legacy  # type: ignore[assignment]
    try:
        chain_router.install_legacy_bridge()
        paths = {getattr(r, "path", None) for r in parent.app.routes}
        monkey_paths = sorted(p for p in paths if p)
    finally:
        chain_router._legacy_app_module = old  # type: ignore[assignment]
    assert "/api/expiries/{underlying}" in monkey_paths
    assert "/api/chain-expiry/{underlying}" in monkey_paths


def test_ui_has_dynamic_broker_discovery_expiries_and_full_strikes_default():
    text = Path("dashboard/frontend/src/components/OptionChain.tsx").read_text(encoding="utf-8")
    assert "/api/underlyings" in text
    assert "/api/expiries/" in text
    assert "/api/chain-expiry/" in text
    assert "Option expiry" in text
    assert "EXPIRIES" in text
    assert "selected_expiry=" in text
    assert "DHAN UNIVERSE" in text
    assert "EQ OPT" in text
    assert "DISCOVERY DEGRADED" in text
    assert "ALL STRIKES" in text
    assert "NO VERIFIED BROKER CHAIN ROWS" in text
    assert "const SYMBOLS =" not in text
    assert "range === 0 ? strikes" in text
