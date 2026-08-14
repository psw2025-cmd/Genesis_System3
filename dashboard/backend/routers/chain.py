"""
Chain discovery helpers for the production dashboard.

The large legacy app.py still owns /api/chain/{underlying} and currently owns
/api/underlyings.  This module supplies one broker-security-master discovery
contract and a startup bridge that replaces app.py's small DEFAULT_UNDERLYINGS
list without creating a duplicate live chain fetch path.  When app.py is finally
modularised, its endpoint should call build_underlyings_payload() directly.
"""
from __future__ import annotations

import sys
from typing import Any, Dict, List

from fastapi import APIRouter

from core.brokers.dhan.equity_fo_universe import INDEX_FO_SYMBOLS, load_equity_fo_universe

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
        "source": universe.get("source") or "dhan_security_master",
        "instrument_type": "OPTIDX+OPTSTK",
        "broker": "DHAN",
        "read_only": True,
        "live_trading_enabled": False,
    }


@router.get("/api/underlyings")
async def get_underlyings():
    """Modular endpoint used once app.py migrates to router ownership."""
    return build_underlyings_payload()


def _legacy_app_module():
    """Return the partially loaded dashboard app module when imported by it."""
    for name in ("dashboard.backend.app", "app"):
        mod = sys.modules.get(name)
        if mod is not None and getattr(mod, "app", None) is not None:
            return mod
    return None


def _install_legacy_underlying_bridge() -> None:
    """Keep the active app.py endpoint dynamic without registering duplicates.

    app.py imports this module before defining DEFAULT_UNDERLYINGS.  Startup runs
    only after app.py has finished loading, so mutating that global here changes
    the existing endpoint's request-time return value safely.
    """
    parent = _legacy_app_module()
    if parent is None:
        return

    @parent.app.on_event("startup")
    async def _refresh_supported_underlyings_from_dhan_master() -> None:
        try:
            payload = build_underlyings_payload()
            values: List[str] = list(payload.get("underlyings") or [])
            if values:
                parent.DEFAULT_UNDERLYINGS = values
                parent.SYSTEM3_UNDERLYINGS_METADATA = payload
        except Exception as exc:
            # Fail truthful: retain the app's conservative index set and expose
            # metadata for diagnostics rather than inventing a broader universe.
            parent.SYSTEM3_UNDERLYINGS_METADATA = {
                "status": "DEGRADED",
                "error": type(exc).__name__,
                "source": "dhan_security_master",
                "live_trading_enabled": False,
            }


_install_legacy_underlying_bridge()
