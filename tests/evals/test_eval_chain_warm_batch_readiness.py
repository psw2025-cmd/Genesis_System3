"""Eval: cold-start 4-symbol chain warm must not depend on serial 20s timing."""

from __future__ import annotations

import asyncio
import importlib.util
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict

import pytest

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "dashboard" / "backend" / "app.py"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

REQUIRED = ("NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY")


def _src() -> str:
    return APP.read_text(encoding="utf-8")


def test_required_chain_symbols_are_explicit_and_exclude_sensex_from_smoke_gate():
    src = _src()
    assert '_REQUIRED_CHAIN_SYMBOLS = ("NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY")' in src
    assert "_CHAIN_COLD_START_GAP_S" in src
    assert "await _warm_required_index_chains_cold_start()" in src
    assert "required_symbols_ready" in src


def test_batch_chains_does_not_cache_warming_placeholders():
    src = _src()
    batch = src.split("async def batch_chains():", 1)[1].split("async def get_chain(", 1)[0]
    assert "if not ready:" in batch
    assert "return payload" in batch
    assert batch.index("if not ready:") < batch.rindex("_cache_set")


def test_missing_expiry_fail_closed_contract_intact():
    chain_src = (ROOT / "dashboard" / "backend" / "routers" / "chain.py").read_text(
        encoding="utf-8"
    )
    assert "INVALID_OR_MISSING_EXPIRY" in chain_src
    expiry_fn = chain_src.split("async def get_chain_expiry", 1)[1].split("def _legacy_app_module", 1)[0]
    assert "if not requested or requested not in allowed:" in expiry_fn
    assert '"contracts": []' in expiry_fn
    assert '"total_contracts": 0' in expiry_fn


def _snapshot(sym: str, *, status: str = "MARKET_CLOSED_DHAN_SNAPSHOT", contracts: int = 2) -> Dict[str, Any]:
    rows = [
        {
            "underlying": sym,
            "strike": 24000.0 + i,
            "option_type": "CE" if i % 2 == 0 else "PE",
            "oi": 0,
            "ltp": 0.0,
            "source": "dhan",
        }
        for i in range(contracts)
    ]
    return {
        "underlying": sym,
        "contracts": rows,
        "spot": 24078.3,
        "pcr": 0.7,
        "total_contracts": contracts,
        "data_source": "dhan",
        "status": status,
        "live": False,
        "snapshot": True,
        "stale": False,
    }


@pytest.fixture(scope="module")
def chain_warm_app_mod():
    old_val = os.environ.get("REQUIRE_API_KEY")
    os.environ["REQUIRE_API_KEY"] = "false"
    try:
        spec = importlib.util.spec_from_file_location(
            "dashboard_backend_app_chain_warm_eval",
            APP,
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        if old_val is not None:
            os.environ["REQUIRE_API_KEY"] = old_val
        else:
            os.environ.pop("REQUIRE_API_KEY", None)


@pytest.fixture
def isolated_chain_warm(chain_warm_app_mod):
    mod = chain_warm_app_mod
    mod._PUSHED_CHAIN_CACHE.clear()
    mod._API_CACHE.clear()
    yield mod
    mod._PUSHED_CHAIN_CACHE.clear()
    mod._API_CACHE.clear()


def _seed_push(mod, symbols=REQUIRED, **kwargs) -> None:
    now = time.time()
    for sym in symbols:
        mod._PUSHED_CHAIN_CACHE[sym] = {
            "data": _snapshot(sym, **kwargs),
            "received_at": now,
            "market_open": False,
        }


def test_empty_cache_is_warming_not_valid(isolated_chain_warm):
    mod = isolated_chain_warm
    payload = asyncio.run(mod.batch_chains())
    assert payload["required_symbols_ready"] is False
    assert payload["cache_hit"] is False
    for sym in REQUIRED:
        entry = payload["chains"][sym]
        assert entry["status"] == "CHAIN_CACHE_WARMING"
        assert entry["contracts"] == []
        assert entry["total_contracts"] == 0
        assert mod._usable_chain_snapshot(entry) is False
    assert "batch_chains_v1" not in mod._API_CACHE


def test_partial_warm_is_not_cached_as_valid(isolated_chain_warm):
    mod = isolated_chain_warm
    _seed_push(mod, symbols=("NIFTY", "BANKNIFTY"))
    payload = asyncio.run(mod.batch_chains())
    assert payload["required_symbols_ready"] is False
    assert payload["chains"]["NIFTY"]["total_contracts"] == 2
    assert payload["chains"]["FINNIFTY"]["status"] == "CHAIN_CACHE_WARMING"
    assert payload["chains"]["MIDCPNIFTY"]["status"] == "CHAIN_CACHE_WARMING"
    assert "batch_chains_v1" not in mod._API_CACHE


def test_cold_start_four_symbol_batch_readiness(isolated_chain_warm, monkeypatch):
    mod = isolated_chain_warm

    async def _fake_uncached(sym, closed_timeout_s=None):
        return _snapshot(str(sym).upper())

    async def _no_sleep(_seconds):
        return None

    monkeypatch.setattr(mod, "_get_chain_uncached", _fake_uncached)
    monkeypatch.setattr(mod, "_market_open_from_state", lambda: False)
    monkeypatch.setattr(mod.asyncio, "sleep", _no_sleep)

    warmed = asyncio.run(mod._warm_required_index_chains_cold_start())
    assert set(warmed) == set(REQUIRED)

    payload = asyncio.run(mod.batch_chains())
    assert payload["required_symbols_ready"] is True
    for sym in REQUIRED:
        entry = payload["chains"][sym]
        assert entry["status"] == "MARKET_CLOSED_DHAN_SNAPSHOT"
        assert len(entry["contracts"]) == 2
        assert entry["spot"] > 0
        assert mod._usable_chain_snapshot(entry) is True
    assert "batch_chains_v1" in mod._API_CACHE


def test_market_closed_snapshot_path(isolated_chain_warm):
    mod = isolated_chain_warm
    _seed_push(mod, status="MARKET_CLOSED_DHAN_SNAPSHOT")
    payload = asyncio.run(mod.batch_chains())
    assert payload["required_symbols_ready"] is True
    for sym in REQUIRED:
        assert payload["chains"][sym]["status"] == "MARKET_CLOSED_DHAN_SNAPSHOT"
        assert payload["chains"][sym]["snapshot"] is True
        assert payload["chains"][sym]["live"] is False


def test_empty_ok_payload_is_not_treated_as_valid(isolated_chain_warm):
    mod = isolated_chain_warm
    fake = {
        "underlying": "NIFTY",
        "contracts": [],
        "spot": 24078.3,
        "pcr": 1.0,
        "total_contracts": 0,
        "data_source": "dhan",
        "status": "OK",
    }
    assert mod._usable_chain_snapshot(fake) is False
    mod._PUSHED_CHAIN_CACHE["NIFTY"] = {
        "data": fake,
        "received_at": time.time(),
        "market_open": False,
    }
    entry = mod._resolve_batch_chain_entry("NIFTY")
    assert entry["status"] == "CHAIN_CACHE_WARMING"
    assert entry["contracts"] == []


def test_stale_empty_cache_stays_fail_closed(isolated_chain_warm):
    mod = isolated_chain_warm
    mod._cache_set(
        "chain_NIFTY",
        {
            "underlying": "NIFTY",
            "contracts": [],
            "spot": 0,
            "total_contracts": 0,
            "status": "OK",
            "data_source": "dhan",
        },
    )
    payload = asyncio.run(mod.batch_chains())
    assert payload["chains"]["NIFTY"]["status"] == "CHAIN_CACHE_WARMING"
    assert payload["required_symbols_ready"] is False


def test_missing_expiry_endpoint_fail_closed():
    from dashboard.backend.routers.chain import get_chain_expiry

    result = asyncio.run(get_chain_expiry("NIFTY", expiry=""))
    assert result["status"] == "INVALID_OR_MISSING_EXPIRY"
    assert result["total_contracts"] == 0
    assert result["contracts"] == []


def test_smoke_required_symbols_match_batch_gate():
    snap = (ROOT / "scripts" / "gcp_live_ui_snapshot.py").read_text(encoding="utf-8")
    assert 'REQUIRED_CHAIN_SYMBOLS = ("NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY")' in snap
