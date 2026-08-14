"""
Chain router — lightweight discovery endpoints only.

Important:
- The authoritative /api/chain/{underlying} endpoint lives in dashboard.backend.app.
- This router only exposes the broker/security-master discovery contract used by
  the production UI. It must not create a second option-chain fetch path.
- Underlying coverage comes from the Dhan security master, not a hard-coded UI list.
"""
from __future__ import annotations

from fastapi import APIRouter

from core.brokers.dhan.equity_fo_universe import INDEX_FO_SYMBOLS, load_equity_fo_universe

router = APIRouter(tags=["chain"])

# Stable operator order for index underlyings. Any newly supported index from the
# broker contract is appended deterministically after this list.
_INDEX_PRIORITY = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX", "BANKEX"]


@router.get("/api/underlyings")
async def get_underlyings():
    """Return the complete option-underlying discovery contract for the UI.

    Equity option underlyings are derived from Dhan's current security master
    (OPTSTK). Index symbols come from the broker-supported index contract. The UI
    can therefore search/select the full supported universe without embedding a
    small symbol list in frontend source.
    """
    universe = load_equity_fo_universe()
    equity = [str(s).upper() for s in (universe.get("underlyings") or []) if s]

    index_set = {str(s).upper() for s in INDEX_FO_SYMBOLS if s}
    indices = [s for s in _INDEX_PRIORITY if s in index_set]
    indices.extend(sorted(index_set.difference(indices)))

    underlyings = indices + [s for s in sorted(set(equity)) if s not in index_set]
    return {
        "underlyings": underlyings,
        "indices": indices,
        "equity_options": sorted(set(equity)),
        "counts": {
            "total": len(underlyings),
            "indices": len(indices),
            "equity_options": len(set(equity)),
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
