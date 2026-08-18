"""BR-2 MICRO2: runtime QC must observe push/TTL snapshots, never live Dhan OC."""

from __future__ import annotations

import asyncio
import importlib.util
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict

import pytest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "dashboard" / "backend" / "app.py"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

FORBIDDEN = "NETWORK_CHAIN_CALL_FORBIDDEN_BR2_MICRO2"
UNDERLYINGS = ("NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY")


def _runtime_qc_block() -> str:
    text = APP.read_text(encoding="utf-8")
    start = text.index('@app.get("/api/qc/runtime")')
    end = text.index('@app.get("/api/underlyings")', start)
    return text[start:end]


def test_runtime_qc_must_not_create_an_independent_live_dhan_chain_path():
    """BR-2: QC is an observer; it must never multiply live Dhan chain demand."""
    block = _runtime_qc_block()

    forbidden = (
        "DataSourceManager",
        "fetch_chain_for_api",
        "_run_blocking",
    )
    for token in forbidden:
        assert token not in block, (
            f"/api/qc/runtime contains direct live-chain token {token!r}; "
            "runtime QC must observe canonical push/TTL snapshots only"
        )


def test_runtime_qc_must_reuse_canonical_chain_snapshot_and_ttl_cache():
    """The QC path must consume the same last-good authority as UI chain reads."""
    block = _runtime_qc_block()

    assert (
        "_chain_from_push_cache" in block
    ), "/api/qc/runtime must consult the canonical pushed/micro-loop chain snapshot"
    assert "_cache_get" in block and "chain_" in block, (
        "/api/qc/runtime must fall back to the canonical local chain TTL cache, " "not a new broker fetch"
    )
    assert block.index("_chain_from_push_cache") < block.index(
        "_cache_get"
    ), "/api/qc/runtime must consult the pushed snapshot before the TTL cache"


def test_runtime_qc_missing_cache_remains_fail_closed_not_trade_ready():
    """No cached rows must remain explicit NO_DATA/WARMING, never fabricated PASS."""
    block = _runtime_qc_block()

    assert '"contracts": []' in block
    assert '"total_contracts": 0' in block
    assert "overall_passed" in block
    assert '"live_trading_enabled": False' in block
    assert '"order_placement_allowed": False' in block
    assert "str(exc)" not in block
    assert "runtime QC import failed" in block


def _raise_forbidden(*_args, **_kwargs):
    raise RuntimeError(FORBIDDEN)


def _snapshot(source: str, underlying: str) -> Dict[str, Any]:
    return {
        "underlying": underlying,
        "contracts": [
            {
                "strike": 25000,
                "option_type": "CE",
                "ltp": 12.5,
                "bidPrice": 12.0,
                "askPrice": 13.0,
            }
        ],
        "total_contracts": 1,
        "status": "MARKET_OPEN",
        "data_source": source,
        "stale": source.startswith("ttl"),
        "live": source.startswith("push"),
    }


@pytest.fixture(scope="module")
def runtime_qc_app_mod():
    old_val = os.environ.get("REQUIRE_API_KEY")
    os.environ["REQUIRE_API_KEY"] = "false"
    try:
        spec = importlib.util.spec_from_file_location(
            "dashboard_backend_app_br2_micro2_runtime_qc",
            ROOT / "dashboard" / "backend" / "app.py",
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
def isolated_runtime_qc(runtime_qc_app_mod, monkeypatch):
    mod = runtime_qc_app_mod
    mod._PUSHED_CHAIN_CACHE.clear()
    mod._API_CACHE.clear()
    monkeypatch.setattr(mod, "MARKET_DETECTION_AVAILABLE", True)
    monkeypatch.setattr(mod, "is_market_open", lambda: (True, "br2-micro2-unit"))
    monkeypatch.setattr(mod, "_run_blocking", _raise_forbidden)
    monkeypatch.setattr(mod, "_run_dhan_oc", _raise_forbidden)

    import core.data.datasource_manager as dsm
    import dashboard.backend.chain_adapter as chain_adapter

    monkeypatch.setattr(chain_adapter, "fetch_chain_for_api", _raise_forbidden)

    class _ForbiddenDataSourceManager:
        def __init__(self, *_args, **_kwargs):
            raise RuntimeError(FORBIDDEN)

    monkeypatch.setattr(dsm, "DataSourceManager", _ForbiddenDataSourceManager)
    yield mod
    mod._PUSHED_CHAIN_CACHE.clear()
    mod._API_CACHE.clear()


def _seed_push(mod, source: str = "push_marker_BR2") -> None:
    now = time.time()
    for sym in UNDERLYINGS:
        payload = _snapshot(source, sym)
        mod._PUSHED_CHAIN_CACHE[sym] = {
            "data": payload,
            "received_at": now,
            "market_open": True,
        }


def _seed_ttl(mod, source: str = "ttl_marker_BR2") -> None:
    for sym in UNDERLYINGS:
        mod._cache_set(f"chain_{sym}", _snapshot(source, sym))


def test_runtime_qc_observes_push_cache_without_network(isolated_runtime_qc):
    mod = isolated_runtime_qc
    _seed_push(mod)

    result = asyncio.run(mod.get_qc_runtime())

    assert FORBIDDEN not in str(result)
    assert result["live_trading_enabled"] is False
    assert result["order_placement_allowed"] is False
    assert result["total_contracts"] == 4
    nifty = result["underlying_results"]["NIFTY"]
    assert nifty["snapshot_source"] == "push"
    assert nifty["data_source"] == "push_marker_BR2"
    assert nifty["total_contracts"] == 1
    assert nifty["fetch_error"] is None


def test_runtime_qc_observes_ttl_cache_without_network(isolated_runtime_qc):
    mod = isolated_runtime_qc
    _seed_ttl(mod)

    result = asyncio.run(mod.get_qc_runtime())

    assert FORBIDDEN not in str(result)
    assert result["live_trading_enabled"] is False
    assert result["order_placement_allowed"] is False
    assert result["total_contracts"] == 4
    nifty = result["underlying_results"]["NIFTY"]
    assert nifty["snapshot_source"] == "ttl"
    assert nifty["data_source"] == "ttl_marker_BR2"
    assert nifty["total_contracts"] == 1


def test_runtime_qc_push_wins_over_ttl_without_network(isolated_runtime_qc):
    mod = isolated_runtime_qc
    _seed_ttl(mod, "ttl_marker_BR2")
    _seed_push(mod, "push_marker_BR2")

    result = asyncio.run(mod.get_qc_runtime())

    assert FORBIDDEN not in str(result)
    for sym in UNDERLYINGS:
        row = result["underlying_results"][sym]
        assert row["snapshot_source"] == "push"
        assert row["data_source"] == "push_marker_BR2"
        assert row["data_source"] != "ttl_marker_BR2"


def test_runtime_qc_empty_caches_fail_closed_without_network(isolated_runtime_qc):
    mod = isolated_runtime_qc

    result = asyncio.run(mod.get_qc_runtime())

    assert FORBIDDEN not in str(result)
    assert result["overall_passed"] is False
    assert result["total_contracts"] == 0
    assert result["live_trading_enabled"] is False
    assert result["order_placement_allowed"] is False
    assert result["status"] == "FAIL"
    for sym in UNDERLYINGS:
        row = result["underlying_results"][sym]
        assert row["snapshot_source"] == "none"
        assert row["total_contracts"] == 0
        assert row["status"] == "NO_DATA"
        assert row["data_source"] == "no_snapshot"
        assert row["fetch_error"] is None
    assert any("no pushed or TTL chain snapshot" in item for item in result["critical_failures"])
