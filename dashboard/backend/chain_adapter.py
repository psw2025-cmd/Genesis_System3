"""Convert DataSourceManager chain output to normalized dashboard API contract format.

Complies with Master Option Symbol & Strike Schema (44 normalized fields).
"""

from __future__ import annotations

import math
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from core.brokers.dhan.nse_option_symbol import build_trading_symbol

# Default lot sizes for major Indian indices
LOT_SIZES = {
    "NIFTY": 50,
    "BANKNIFTY": 15,
    "FINNIFTY": 25,
    "MIDCPNIFTY": 50,
    "SENSEX": 10,
    "BANKEX": 15,
}


def normalize_index_chain_exchange(exchange: str, default: str = 'NSE') -> str:
    """Normalize index chain exchange string flags for the pipeline backend router."""
    if not exchange:
        return "NSE"
    return str(exchange).upper().strip()


def _configured_chain_limit() -> int:
    """Return explicit web contract limit; 0 means full broker chain."""
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


def _classify_buildup(change_price: float, change_oi: int) -> str:
    """Classify option open interest & price action buildup."""
    if change_price > 0 and change_oi > 0:
        return "Long Buildup"
    elif change_price < 0 and change_oi > 0:
        return "Short Buildup"
    elif change_price > 0 and change_oi < 0:
        return "Short Covering"
    elif change_price < 0 and change_oi < 0:
        return "Long Unwinding"
    return "Neutral"


def _calculate_max_pain(strikes: List[float], ce_oi_map: Dict[float, int], pe_oi_map: Dict[float, int]) -> float:
    """Compute option Max Pain strike where option writers lose the least payout."""
    if not strikes:
        return 0.0
    min_loss = float("inf")
    max_pain_strike = strikes[0]
    for expiry_price in strikes:
        total_loss = 0.0
        for strike, ce_oi in ce_oi_map.items():
            if expiry_price > strike:
                total_loss += (expiry_price - strike) * ce_oi
        for strike, pe_oi in pe_oi_map.items():
            if expiry_price < strike:
                total_loss += (strike - expiry_price) * pe_oi
        if total_loss < min_loss:
            min_loss = total_loss
            max_pain_strike = expiry_price
    return max_pain_strike


def _optional_float(value: Any) -> Optional[float]:
    """Preserve unavailable values as None while retaining genuine zero."""
    if value is None or value is pd.NA:
        return None
    try:
        if pd.isna(value):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _liquidity_bounce(df: pd.DataFrame) -> tuple[pd.DataFrame, Dict[str, int]]:
    """Reject dead option legs before UI limiting or feature consumption."""
    if df is None or df.empty:
        return df, {"filtered_total": 0, "zero_or_missing_oi": 0, "zero_or_missing_volume": 0}
    oi = pd.to_numeric(df.get("oi", pd.Series(index=df.index, dtype=float)), errors="coerce").fillna(0)
    volume = pd.to_numeric(df.get("volume", pd.Series(index=df.index, dtype=float)), errors="coerce").fillna(0)
    dead_oi = oi <= 0
    dead_volume = volume <= 0
    rejected = dead_oi | dead_volume
    return df.loc[~rejected].copy(), {
        "filtered_total": int(rejected.sum()),
        "zero_or_missing_oi": int(dead_oi.sum()),
        "zero_or_missing_volume": int(dead_volume.sum()),
    }


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

    spot_f = float(spot or 0)
    broker_rows_total = int(len(df))
    df, liquidity_counts = _liquidity_bounce(df)
    liquidity_eligible_rows_total = int(len(df))
    if df.empty:
        return None
    df = _limit_chain_df(df, spot)

    # Determine ATM strike
    unique_strikes = sorted(set(pd.to_numeric(df.get("strike", df.get("strike_price", [])), errors="coerce").dropna()))
    atm_strike = min(unique_strikes, key=lambda s: abs(s - spot_f)) if unique_strikes and spot_f > 0 else 0.0

    lot_size = LOT_SIZES.get(underlying.upper(), 50)
    ce_oi_map: Dict[float, int] = {}
    pe_oi_map: Dict[float, int] = {}

    contracts: List[Dict[str, Any]] = []
    chain_expiry = None

    for _, row in df.iterrows():
        opt = str(row.get("option_type", row.get("OptnTp", ""))).upper()
        if opt not in ("CE", "PE"):
            continue
        strike = float(row.get("strike", row.get("strike_price", 0)) or 0)
        oi = int(row.get("oi", 0) or 0)
        volume = int(row.get("volume", 0) or 0)
        previous_volume = int(row.get("previous_volume", 0) or 0)
        volume_change = volume - previous_volume if previous_volume > 0 else None
        volume_change_percent = (
            volume_change / previous_volume * 100.0
            if volume_change is not None
            else None
        )
        ltp_val = float(row.get("ltp", row.get("last_price", 0)) or 0)
        prev_close = float(row.get("previous_close_price", row.get("close", ltp_val)) or ltp_val)
        change_rs = ltp_val - prev_close
        change_pct = (change_rs / prev_close * 100.0) if prev_close > 0 else 0.0
        oi_change = int(row.get("oi_change", 0) or 0)
        oi_change_pct = float(row.get("oi_change_pct", 0) or 0)

        row_expiry = str(row.get("expiry", row.get("expiry_date", "")) or "")
        if row_expiry and not chain_expiry:
            chain_expiry = row_expiry

        # Track OI maps for max pain
        if opt == "CE":
            ce_oi_map[strike] = ce_oi_map.get(strike, 0) + oi
        else:
            pe_oi_map[strike] = pe_oi_map.get(strike, 0) + oi

        # Moneyness & Distance
        dist_abs = abs(strike - spot_f) if spot_f > 0 else 0.0
        dist_pct = (dist_abs / spot_f * 100.0) if spot_f > 0 else 0.0

        if dist_pct <= 0.5:
            moneyness = "ATM"
        elif (opt == "CE" and strike < spot_f) or (opt == "PE" and strike > spot_f):
            moneyness = "ITM"
        else:
            moneyness = "OTM"

        # Intrinsic & Time Value
        if opt == "CE":
            intrinsic = max(0.0, spot_f - strike) if spot_f > 0 else 0.0
        else:
            intrinsic = max(0.0, strike - spot_f) if spot_f > 0 else 0.0
        time_val = max(0.0, ltp_val - intrinsic)

        # Spreads & Liquidity
        bid = float(row.get("top_bid_price", row.get("bid", 0)) or 0)
        ask = float(row.get("top_ask_price", row.get("ask", 0)) or 0)
        spread = max(0.0, ask - bid) if (ask > 0 and bid > 0) else 0.0
        spread_pct = (spread / ltp_val * 100.0) if ltp_val > 0 else 0.0

        # Liquidity Score (0-100)
        liquidity_score = 100
        if spread_pct > 2.0:
            liquidity_score -= min(50, int(spread_pct * 10))
        if oi < 1000:
            liquidity_score -= 20
        if volume < 500:
            liquidity_score -= 20
        liquidity_score = max(0, min(100, liquidity_score))

        buildup = _classify_buildup(change_rs, oi_change)

        contracts.append({
            "strike_price": strike,
            "option_type": opt,
            "ltp": ltp_val,
            "net_change": change_rs,
            "net_change_percent": change_pct,
            "open_interest": oi,
            "oi_change": oi_change,
            "oi_change_percent": oi_change_pct,
            "volume": volume,
            "volume_change": volume_change,
            "volume_change_percent": volume_change_percent,
            "moneyness": moneyness,
            "intrinsic_value": intrinsic,
            "time_value": time_val,
            "bid_price": bid,
            "ask_price": ask,
            "bid_ask_spread": spread,
            "spread_percent": spread_pct,
            "liquidity_score": liquidity_score,
            "buildup_status": buildup,
            "lot_size": lot_size
        })

    max_pain = _calculate_max_pain(unique_strikes, ce_oi_map, pe_oi_map)

    return {
        "underlying": underlying.upper(),
        "spot_price": spot_f,
        "expiry_date": chain_expiry or expiry,
        "atm_strike": atm_strike,
        "max_pain_strike": max_pain,
        "contracts_count": len(contracts),
        "broker_rows_total": broker_rows_total,
        "liquidity_filtered_count": liquidity_counts["filtered_total"],
        "eligible_rows_count": liquidity_eligible_rows_total,
        "contracts": contracts,
        "last_updated_utc": datetime.now(timezone.utc).isoformat()
    }

