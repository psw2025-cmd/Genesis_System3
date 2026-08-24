"""Chain discovery and read-only expiry helpers for the production dashboard.

The large legacy app.py still owns /api/chain/{underlying}. This module supplies
broker-security-master discovery plus transitional startup wiring for dynamic
underlyings and explicit-expiry reads without creating any order authority.
"""
from __future__ import annotations

import asyncio
import csv
import sys
from functools import lru_cache
from typing import Any, Dict, List

from fastapi import APIRouter

from core.brokers.dhan.equity_fo_universe import (
    INDEX_FO_SYMBOLS,
    load_equity_fo_universe,
    load_equity_market_coverage,
    resolve_equity_security_master,
)

router = APIRouter(tags=["chain"])
_INDEX_PRIORITY = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX", "BANKEX"]
_MASTER_SYMBOL_ALIASES = {"BSXOPT": "SENSEX", "BKXOPT": "BANKEX"}


def underlying_from_master_row(row: Dict[str, Any]) -> str:
    """Resolve option underlying from a Dhan security-master row.

    BSE index options store SM_SYMBOL_NAME as BSXOPT/BKXOPT while the
    trading symbol is SENSEX-... / BANKEX-.... Prefer the trading prefix.
    """
    trading = str(row.get("SEM_TRADING_SYMBOL") or row.get("TRADING_SYMBOL") or "").strip().upper()
    custom = str(row.get("SEM_CUSTOM_SYMBOL") or row.get("DISPLAY_NAME") or "").strip().upper()
    explicit = str(row.get("UNDERLYING_SYMBOL") or "").strip().upper()
    sm = str(row.get("SM_SYMBOL_NAME") or row.get("SYMBOL_NAME") or "").strip().upper()
    if "-" in trading:
        prefix = trading.split("-", 1)[0].strip()
        if prefix and prefix not in {"CE", "PE", "FUT", "XX"}:
            return prefix
    if custom:
        first = custom.split()[0].strip()
        if first and first not in {"CE", "PE"}:
            return first
    if explicit:
        return explicit
    if sm in _MASTER_SYMBOL_ALIASES:
        return _MASTER_SYMBOL_ALIASES[sm]
    return sm


def build_underlyings_payload() -> Dict[str, Any]:
    universe = load_equity_fo_universe()
    coverage = load_equity_market_coverage()
    equity = [str(s).upper() for s in (universe.get("underlyings") or []) if s]
    index_set = {str(s).upper() for s in INDEX_FO_SYMBOLS if s}
    indices = [s for s in _INDEX_PRIORITY if s in index_set]
    indices.extend(sorted(index_set.difference(indices)))
    equity_unique = sorted(set(equity).difference(index_set))
    underlyings = indices + equity_unique
    cash = coverage.get("cash") or {}
    stock_options = coverage.get("stock_options") or {}
    return {
        "underlyings": underlyings,
        "indices": indices,
        "equity_options": equity_unique,
        "counts": {
            "total": len(underlyings),
            "indices": len(indices),
            "equity_options": len(equity_unique),
            "option_contracts": int(universe.get("contract_count") or 0),
            "nse_cash": int((cash.get("NSE") or {}).get("instrument_count") or 0),
            "bse_cash": int((cash.get("BSE") or {}).get("instrument_count") or 0),
            "nse_equity_option_underlyings": int((stock_options.get("NSE") or {}).get("underlying_count") or 0),
            "bse_equity_option_underlyings": int((stock_options.get("BSE") or {}).get("underlying_count") or 0),
            "nse_option_contracts": int((stock_options.get("NSE") or {}).get("contract_count") or 0),
            "bse_option_contracts": int((stock_options.get("BSE") or {}).get("contract_count") or 0),
        },
        "default": "NIFTY",
        "chain_endpoint": "/api/chain/{underlying}",
        "expiry_endpoint": "/api/expiries/{underlying}",
        "explicit_expiry_chain_endpoint": "/api/chain-expiry/{underlying}?expiry=YYYY-MM-DD",
        "source": universe.get("source") or "dhan_security_master",
        "source_mode": coverage.get("source_mode") or universe.get("source_mode"),
        "source_sha256": coverage.get("source_sha256"),
        "reliance_only": bool(coverage.get("reliance_only")),
        "scan_plan": coverage.get("scan_plan") or {},
        "prediction_horizons": coverage.get("prediction_horizons") or [],
        "learning_contract": coverage.get("learning_contract") or {},
        "instrument_type": "OPTIDX+OPTSTK",
        "broker": "DHAN",
        "read_only": True,
        "live_trading_enabled": False,
    }


@lru_cache(maxsize=1)
def _expiry_map() -> Dict[str, List[str]]:
    """Build all broker-master option expiries per underlying once per process."""
    result: Dict[str, set[str]] = {}
    master_path = resolve_equity_security_master()
    if not master_path.exists():
        return {}
    with master_path.open(encoding="utf-8", errors="replace") as handle:
        for row in csv.DictReader(handle):
            inst = str(row.get("SEM_INSTRUMENT_NAME") or row.get("INSTRUMENT") or "").strip().upper()
            if inst not in {"OPTIDX", "OPTSTK"}:
                continue
            name = underlying_from_master_row(row)
            expiry = str(
                row.get("SEM_EXPIRY_DATE")
                or row.get("SM_EXPIRY_DATE")
                or row.get("EXPIRY_DATE")
                or row.get("XpryDt")
                or ""
            ).strip()[:10]
            if name and expiry:
                result.setdefault(name, set()).add(expiry)
    return {name: sorted(values) for name, values in result.items()}


@router.get("/api/underlyings")
async def get_underlyings():
    return build_underlyings_payload()


def _expiries_from_live_chain(symbol: str) -> List[str]:
    """Harvest expiry dates from the last-good paced/on-demand chain cache."""
    found: set[str] = set()
    data = None
    try:
        parent = _legacy_app_module()
        cache = getattr(parent, "_PUSHED_CHAIN_CACHE", {}) if parent is not None else {}
        pushed = cache.get(symbol) if isinstance(cache, dict) else None
        if isinstance(pushed, dict):
            data = pushed.get("data") if isinstance(pushed.get("data"), dict) else pushed
        if data is None and parent is not None:
            getter = getattr(parent, "_cache_get", None)
            if callable(getter):
                hit = getter(f"chain_{symbol}", 300.0)
                if isinstance(hit, dict):
                    data = hit
    except Exception:
        data = None
    contracts = (data or {}).get("contracts") if isinstance(data, dict) else None
    if isinstance(contracts, list):
        for row in contracts:
            if not isinstance(row, dict):
                continue
            exp = str(row.get("expiry_date") or row.get("expiry") or "")[:10]
            if len(exp) == 10 and exp[4] == "-":
                found.add(exp)
    return sorted(found)


async def get_expiries(underlying: str):
    symbol = str(underlying or "").strip().upper()
    expiries = list(_expiry_map().get(symbol) or [])
    source = "dhan_security_master"
    if not expiries:
        live = _expiries_from_live_chain(symbol)
        if live:
            expiries = live
            source = "live_chain_cache"
    return {
        "underlying": symbol,
        "expiries": expiries,
        "count": len(expiries),
        "source": source,
        "broker": "DHAN",
        "read_only": True,
        "live_trading_enabled": False,
        "status": "OK" if expiries else "NO_EXPIRIES_IN_BROKER_MASTER",
    }


async def get_chain_expiry(underlying: str, expiry: str = ""):
    """Read one explicitly selected broker expiry with a bounded request."""
    symbol = str(underlying or "").strip().upper()
    requested = str(expiry or "").strip()
    allowed = list(_expiry_map().get(symbol) or [])
    if requested and requested not in allowed:
        live = _expiries_from_live_chain(symbol)
        allowed = sorted(set(allowed).union(live))
    if not requested or requested not in allowed:
        return {
            "underlying": symbol,
            "contracts": [],
            "total_contracts": 0,
            "status": "INVALID_OR_MISSING_EXPIRY",
            "message": "Select an expiry present in the Dhan security master",
            "available_expiries": allowed,
            "data_source": "dhan",
            "live_trading_enabled": False,
        }

    def _fetch():
        from core.data.datasource_manager import DataSourceManager
        from dashboard.backend.chain_adapter import fetch_chain_for_api

        return fetch_chain_for_api(DataSourceManager(), symbol, expiry=requested)

    try:
        payload = await asyncio.wait_for(asyncio.to_thread(_fetch), timeout=18.0)
    except asyncio.TimeoutError:
        payload = None
    except Exception as exc:
        return {
            "underlying": symbol,
            "contracts": [],
            "total_contracts": 0,
            "status": "CHAIN_EXPIRY_FETCH_ERROR",
            "message": type(exc).__name__,
            "requested_expiry": requested,
            "data_source": "dhan",
            "live_trading_enabled": False,
        }
    if not payload:
        return {
            "underlying": symbol,
            "contracts": [],
            "total_contracts": 0,
            "status": "NO_DHAN_DATA",
            "message": "No Dhan option-chain rows returned for selected expiry",
            "requested_expiry": requested,
            "data_source": "dhan",
            "live_trading_enabled": False,
        }
    payload["selected_expiry"] = requested
    payload["live_trading_enabled"] = False
    return payload


def _legacy_app_module():
    for name in ("dashboard.backend.app", "app"):
        mod = sys.modules.get(name)
        if mod is not None and getattr(mod, "app", None) is not None:
            return mod
    return None


def _install_legacy_bridge() -> None:
    """Upgrade discovery + register unique read-only expiry routes.

    Routes are registered immediately (not only on startup) so Cloud Run
    revisions never serve HTTP_404 for /api/expiries/{underlying}.
    """
    parent = _legacy_app_module()
    if parent is None or getattr(parent, "app", None) is None:
        return

    def _apply() -> None:
        try:
            payload = build_underlyings_payload()
            values: List[str] = list(payload.get("underlyings") or [])
            if values:
                parent.DEFAULT_UNDERLYINGS = values
                parent.SYSTEM3_UNDERLYINGS_METADATA = payload

            # app.py already owns /api/underlyings. Replace its callable truth
            # instead of registering a duplicate route.
            for route in parent.app.routes:
                if getattr(route, "path", None) == "/api/underlyings":
                    route.endpoint = get_underlyings
                    dependant = getattr(route, "dependant", None)
                    if dependant is not None:
                        dependant.call = get_underlyings
                    break

            paths = {getattr(route, "path", None) for route in parent.app.routes}
            if "/api/expiries/{underlying}" not in paths:
                parent.app.add_api_route(
                    "/api/expiries/{underlying}",
                    get_expiries,
                    methods=["GET"],
                    tags=["chain"],
                )
            if "/api/chain-expiry/{underlying}" not in paths:
                parent.app.add_api_route(
                    "/api/chain-expiry/{underlying}",
                    get_chain_expiry,
                    methods=["GET"],
                    tags=["chain"],
                )
        except Exception as exc:
            parent.SYSTEM3_UNDERLYINGS_METADATA = {
                "status": "DEGRADED",
                "error": type(exc).__name__,
                "source": "dhan_security_master",
                "live_trading_enabled": False,
            }

    _apply()

    @parent.app.on_event("startup")
    async def _refresh_supported_underlyings_from_dhan_master() -> None:
        _apply()


# Do NOT call at import time — app.py imports this module before
# ``app = FastAPI(...)`` exists, so the bridge would no-op and leave
# /api/expiries/{underlying} unregistered (UI shows EXPIRY DATA HTTP_404).
# app.py must call install_legacy_bridge() after the FastAPI app is created.


def install_legacy_bridge() -> None:
    """Public startup hook for app.py after FastAPI() construction."""
    _install_legacy_bridge()
