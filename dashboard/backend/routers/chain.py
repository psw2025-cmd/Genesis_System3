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
    SECURITY_MASTER,
    load_equity_fo_universe,
)

router = APIRouter(tags=["chain"])
_INDEX_PRIORITY = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX", "BANKEX"]


def build_underlyings_payload() -> Dict[str, Any]:
    universe = load_equity_fo_universe()
    equity = [str(s).upper() for s in (universe.get("underlyings") or []) if s]
    index_set = {str(s).upper() for s in INDEX_FO_SYMBOLS if s}
    indices = [s for s in _INDEX_PRIORITY if s in index_set]
    indices.extend(sorted(index_set.difference(indices)))
    equity_unique = sorted(set(equity).difference(index_set))
    underlyings = indices + equity_unique
    return {
        "underlyings": underlyings,
        "indices": indices,
        "equity_options": equity_unique,
        "counts": {
            "total": len(underlyings),
            "indices": len(indices),
            "equity_options": len(equity_unique),
            "option_contracts": int(universe.get("contract_count") or 0),
        },
        "default": "NIFTY",
        "chain_endpoint": "/api/chain/{underlying}",
        "expiry_endpoint": "/api/expiries/{underlying}",
        "explicit_expiry_chain_endpoint": "/api/chain-expiry/{underlying}?expiry=YYYY-MM-DD",
        "source": universe.get("source") or "dhan_security_master",
        "instrument_type": "OPTIDX+OPTSTK",
        "broker": "DHAN",
        "read_only": True,
        "live_trading_enabled": False,
    }


@lru_cache(maxsize=1)
def _expiry_map() -> Dict[str, List[str]]:
    """Build all broker-master option expiries per underlying once per process."""
    result: Dict[str, set[str]] = {}
    if not SECURITY_MASTER.exists():
        return {}
    with SECURITY_MASTER.open(encoding="utf-8", errors="replace") as handle:
        for row in csv.DictReader(handle):
            inst = str(row.get("SEM_INSTRUMENT_NAME") or row.get("INSTRUMENT") or "").strip().upper()
            if inst not in {"OPTIDX", "OPTSTK"}:
                continue
            name = str(row.get("SM_SYMBOL_NAME") or row.get("SYMBOL_NAME") or "").strip().upper()
            if not name:
                custom = str(row.get("SEM_TRADING_SYMBOL") or row.get("SEM_CUSTOM_SYMBOL") or "").strip().upper()
                name = custom.split("-")[0] if "-" in custom else ""
            expiry = str(row.get("SEM_EXPIRY_DATE") or row.get("EXPIRY_DATE") or row.get("XpryDt") or "").strip()[:10]
            if name and expiry:
                result.setdefault(name, set()).add(expiry)
    return {name: sorted(values) for name, values in result.items()}


@router.get("/api/underlyings")
async def get_underlyings():
    return build_underlyings_payload()


async def get_expiries(underlying: str):
    symbol = str(underlying or "").strip().upper()
    expiries = list(_expiry_map().get(symbol) or [])
    return {
        "underlying": symbol,
        "expiries": expiries,
        "count": len(expiries),
        "source": "dhan_security_master",
        "broker": "DHAN",
        "read_only": True,
        "live_trading_enabled": False,
        "status": "OK" if expiries else "NO_EXPIRIES_IN_BROKER_MASTER",
    }


async def get_chain_expiry(underlying: str, expiry: str = ""):
    """Read one explicitly selected broker expiry with a bounded request."""
    symbol = str(underlying or "").strip().upper()
    requested = str(expiry or "").strip()
    allowed = _expiry_map().get(symbol) or []
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
