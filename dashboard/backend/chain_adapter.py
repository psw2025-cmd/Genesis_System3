"""Convert DataSourceManager chain output to dashboard API contract format."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import pandas as pd


def fetch_chain_for_api(dsm: Any, underlying: str) -> Optional[Dict[str, Any]]:
    """Fetch option chain via DataSourceManager and normalize for /api/chain."""
    if not hasattr(dsm, "fetch_option_chain"):
        return None
    result = dsm.fetch_option_chain(underlying.upper())
    if not result:
        return None
    df, spot = result
    if df is None or df.empty:
        return None

    contracts: List[Dict[str, Any]] = []
    for _, row in df.iterrows():
        opt = str(row.get("option_type", row.get("OptnTp", ""))).upper()
        if opt not in ("CE", "PE"):
            continue
        strike = float(row.get("strike", row.get("strike_price", 0)) or 0)
        oi = int(row.get("oi", 0) or 0)
        prev_oi = int(row.get("previous_oi", row.get("prev_oi", 0)) or 0)
        contracts.append(
            {
                "strike": strike,
                "option_type": opt,
                "oi": oi,
                "oi_change": int(row.get("change_in_oi", row.get("oi_change", oi - prev_oi)) or 0),
                "volume": int(row.get("volume", 0) or 0),
                "ltp": float(row.get("ltp", row.get("last_price", 0)) or 0),
                "iv": float(row.get("iv", 0) or 0),
                "delta": float(row.get("delta", 0) or 0),
                "gamma": float(row.get("gamma", 0) or 0),
                "theta": float(row.get("theta", 0) or 0),
                "vega": float(row.get("vega", 0) or 0),
                "top_bid_price": float(row.get("top_bid_price", 0) or 0),
                "top_ask_price": float(row.get("top_ask_price", 0) or 0),
                "source": str(row.get("source", "datasource_manager")),
            }
        )

    if not contracts:
        return None

    pe_oi = sum(c["oi"] for c in contracts if c["option_type"] == "PE")
    ce_oi = sum(c["oi"] for c in contracts if c["option_type"] == "CE")
    pcr = float(pe_oi / ce_oi) if ce_oi > 0 else 1.0
    source = contracts[0].get("source", "real")

    return {
        "underlying": underlying.upper(),
        "spot": float(spot or 0),
        "pcr": pcr,
        "contracts": contracts[:1000],
        "total_contracts": len(contracts),
        "data_source": source,
        "status": "OK",
    }
