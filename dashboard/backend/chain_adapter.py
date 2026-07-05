"""Convert DataSourceManager chain output to dashboard API contract format."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import pandas as pd

from core.brokers.dhan.nse_option_symbol import enrich_option_row


def _int_env(name: str, default: int) -> int:
    try:
        return max(10, int(os.environ.get(name, str(default)) or default))
    except Exception:
        return default


def _limit_chain_df(df: pd.DataFrame, spot: Any) -> pd.DataFrame:
    """Reduce option chain size before JSON conversion/caching.

    Render Starter has 512MB RAM. Returning/caching full option-chain frames can
    push the web service near OOM. Keep contracts around ATM plus enough liquid
    rows for dashboard/scanner use. Worker can still compute fuller datasets.
    """
    max_contracts = _int_env("CHAIN_MAX_CONTRACTS", 160)
    try:
        if df is None or df.empty or len(df) <= max_contracts:
            return df
        strike_col = "strike" if "strike" in df.columns else "strike_price" if "strike_price" in df.columns else None
        if not strike_col:
            return df.head(max_contracts)
        spot_f = float(spot or 0)
        if spot_f <= 0:
            return df.head(max_contracts)
        work = df.copy()
        work["_atm_distance"] = pd.to_numeric(work[strike_col], errors="coerce").sub(spot_f).abs()
        work = work.sort_values("_atm_distance").head(max_contracts).drop(columns=["_atm_distance"], errors="ignore")
        return work
    except Exception:
        return df.head(max_contracts)


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

    df = _limit_chain_df(df, spot)

    contracts: List[Dict[str, Any]] = []
    chain_expiry = None
    for _, row in df.iterrows():
        opt = str(row.get("option_type", row.get("OptnTp", ""))).upper()
        if opt not in ("CE", "PE"):
            continue
        strike = float(row.get("strike", row.get("strike_price", 0)) or 0)
        oi = int(row.get("oi", 0) or 0)
        prev_oi = int(row.get("previous_oi", row.get("prev_oi", 0)) or 0)
        if chain_expiry is None:
            chain_expiry = row.get("expiry") or row.get("expiry_date")
        base = {
            "underlying": underlying.upper(),
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
            "previous_close_price": float(row.get("previous_close_price", 0) or 0),
            "change_percent": float(row.get("change_percent", row.get("pChange", 0)) or 0),
            "security_id": row.get("security_id") or row.get("token"),
            "trading_symbol": row.get("trading_symbol") or row.get("tradingSymbol") or row.get("symbol"),
            "expiry_date": row.get("expiry") or row.get("expiry_date"),
            "source": str(row.get("source", "datasource_manager")),
        }
        contracts.append(enrich_option_row(base, default_expiry=chain_expiry))

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
        "contracts": contracts,
        "total_contracts": len(contracts),
        "data_source": source,
        "status": "OK",
        "expiry_date": chain_expiry,
        "limited_for_web": True,
        "max_contracts": _int_env("CHAIN_MAX_CONTRACTS", 160),
    }
