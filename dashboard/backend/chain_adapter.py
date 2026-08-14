"""Convert DataSourceManager chain output to dashboard API contract format."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import pandas as pd

from core.brokers.dhan.nse_option_symbol import build_trading_symbol


def _configured_chain_limit() -> int:
    """Return explicit web contract limit; 0 means full broker chain.

    GCP is the production authority. The previous implicit 160-contract cap was
    inherited from a legacy 512 MB Render constraint and silently prevented the
    UI from proving a complete broker chain. A limit is now opt-in only.
    """
    try:
        raw = int(os.environ.get("CHAIN_MAX_CONTRACTS", "0") or 0)
        return max(0, raw)
    except Exception:
        return 0


def _limit_chain_df(df: pd.DataFrame, spot: Any) -> pd.DataFrame:
    """Apply an explicit operator cap only; default is the complete chain."""
    max_contracts = _configured_chain_limit()
    if max_contracts <= 0 or df is None or df.empty or len(df) <= max_contracts:
        return df
    try:
        strike_col = "strike" if "strike" in df.columns else "strike_price" if "strike_price" in df.columns else None
        if not strike_col:
            return df.head(max_contracts)
        spot_f = float(spot or 0)
        if spot_f <= 0:
            return df.head(max_contracts)
        work = df.copy()
        work["_atm_distance"] = pd.to_numeric(work[strike_col], errors="coerce").sub(spot_f).abs()
        return work.sort_values("_atm_distance").head(max_contracts).drop(columns=["_atm_distance"], errors="ignore")
    except Exception:
        return df.head(max_contracts)


def _normalize_chain_source(source: Any) -> str:
    src = str(source or "").strip().lower()
    if src in ("", "datasource_manager", "real", "dhan_option_chain_live"):
        return "dhan"
    return src


def fetch_chain_for_api(dsm: Any, underlying: str, expiry: str = "") -> Optional[Dict[str, Any]]:
    """Fetch one requested expiry from Dhan and normalize for /api/chain."""
    if not hasattr(dsm, "fetch_option_chain"):
        return None
    result = dsm.fetch_option_chain(underlying.upper(), expiry=expiry)
    if not result or result[0] is None:
        return None
    df, spot = result
    if df is None or getattr(df, "empty", True):
        return None

    broker_rows_total = int(len(df))
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
            chain_expiry = row.get("expiry") or row.get("expiry_date") or expiry or None
        row_source = _normalize_chain_source(row.get("source", "dhan"))
        ltp_val = float(row.get("ltp", row.get("last_price", 0)) or 0)
        prev_close = float(row.get("previous_close_price", row.get("previous_close", 0)) or 0)
        if ltp_val > 0 and prev_close > 0:
            change_rs = ltp_val - prev_close
            change_pct = (ltp_val - prev_close) / prev_close * 100.0
        else:
            change_rs = 0.0
            change_pct = float(row.get("change_percent", row.get("pChange", 0)) or 0)
        base = {
            "underlying": underlying.upper(),
            "strike": strike,
            "option_type": opt,
            "oi": oi,
            "oi_change": int(row.get("change_in_oi", row.get("oi_change", oi - prev_oi)) or 0),
            "volume": int(row.get("volume", 0) or 0),
            "ltp": ltp_val,
            "iv": float(row.get("iv", 0) or 0),
            "delta": float(row.get("delta", 0) or 0),
            "gamma": float(row.get("gamma", 0) or 0),
            "theta": float(row.get("theta", 0) or 0),
            "vega": float(row.get("vega", 0) or 0),
            "top_bid_price": float(row.get("top_bid_price", 0) or 0),
            "top_ask_price": float(row.get("top_ask_price", 0) or 0),
            "previous_close_price": prev_close,
            "change": change_rs,
            "change_percent": change_pct,
            "security_id": row.get("security_id") or row.get("token"),
            "trading_symbol": row.get("trading_symbol") or row.get("tradingSymbol") or row.get("symbol"),
            "expiry_date": row.get("expiry") or row.get("expiry_date") or chain_expiry,
            "source": row_source,
            "data_source": row_source,
        }
        if not base.get("trading_symbol") and chain_expiry:
            try:
                built = build_trading_symbol(underlying.upper(), chain_expiry, strike, opt)
                if built:
                    base["trading_symbol"] = built
                    base["symbol"] = built
            except Exception:
                pass
        contracts.append(base)

    if not contracts:
        return None

    pe_oi = sum(c["oi"] for c in contracts if c["option_type"] == "PE")
    ce_oi = sum(c["oi"] for c in contracts if c["option_type"] == "CE")
    pcr = float(pe_oi / ce_oi) if ce_oi > 0 else 1.0
    source = _normalize_chain_source(contracts[0].get("source", "dhan"))
    configured_limit = _configured_chain_limit()

    return {
        "underlying": underlying.upper(),
        "spot": float(spot or 0),
        "pcr": pcr,
        "contracts": contracts,
        "total_contracts": len(contracts),
        "broker_rows_total": broker_rows_total,
        "data_source": source,
        "source_priority": "dhan_option_chain_live" if source == "dhan" else source,
        "status": "OK",
        "stale": False,
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
        "expiry_date": chain_expiry,
        "requested_expiry": expiry or None,
        "complete_chain": configured_limit <= 0 or len(contracts) >= broker_rows_total,
        "limited_for_web": configured_limit > 0 and len(contracts) < broker_rows_total,
        "max_contracts": configured_limit,
        "live_trading_enabled": False,
    }
