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
        prev_oi = int(row.get("previous_oi", row.get("prev_oi", 0)) or 0)
        oi_change = int(row.get("change_in_oi", row.get("oi_change", oi - prev_oi)) or 0)
        oi_change_pct = (oi_change / prev_oi * 100.0) if prev_oi > 0 else 0.0

        if opt == "CE":
            ce_oi_map[strike] = ce_oi_map.get(strike, 0) + oi
        else:
            pe_oi_map[strike] = pe_oi_map.get(strike, 0) + oi

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

        bid = float(row.get("top_bid_price", row.get("bid", 0)) or 0)
        ask = float(row.get("top_ask_price", row.get("ask", 0)) or 0)
        spread = max(0.0, ask - bid) if (bid > 0 and ask > 0) else 0.0
        spread_pct = (spread / ltp_val * 100.0) if ltp_val > 0 else 0.0
        volume = int(row.get("volume", 0) or 0)

        # Distance & Moneyness
        dist_abs = abs(strike - spot_f) if spot_f > 0 else 0.0
        dist_pct = (dist_abs / spot_f * 100.0) if spot_f > 0 else 0.0
        if spot_f <= 0 or abs(strike - atm_strike) < 1e-3:
            moneyness = "ATM"
        elif opt == "CE":
            moneyness = "ITM" if strike < spot_f else "OTM"
        else:
            moneyness = "ITM" if strike > spot_f else "OTM"

        # Intrinsic & Time Value
        if opt == "CE":
            intrinsic = max(0.0, spot_f - strike) if spot_f > 0 else 0.0
        else:
            intrinsic = max(0.0, strike - spot_f) if spot_f > 0 else 0.0
        time_val = max(0.0, ltp_val - intrinsic) if ltp_val > 0 else 0.0

        # Liquidity score (0 to 100) based on volume, OI, and tight spread
        spread_factor = max(0.0, 1.0 - (spread_pct / 5.0)) if spread_pct > 0 else 0.5
        oi_factor = min(1.0, oi / 100000.0) if oi > 0 else 0.0
        vol_factor = min(1.0, volume / 50000.0) if volume > 0 else 0.0
        liquidity_score = round((spread_factor * 40 + oi_factor * 30 + vol_factor * 30), 1)

        # Buildup & unusual activity
        buildup = _classify_buildup(change_rs, oi_change)
        unusual_flag = bool((volume > 0 and oi > 0 and (volume / oi) > 2.0) or abs(oi_change_pct) > 50.0)

        base: Dict[str, Any] = {
            "exchange": "NSE_FNO",
            "underlying": underlying.upper(),
            "underlying_symbol": underlying.upper(),
            "underlying_type": "INDEX" if underlying.upper() in LOT_SIZES else "EQUITY",
            "expiry": chain_expiry,
            "expiry_date": chain_expiry,
            "strike": strike,
            "option_type": opt,
            "spot_price": spot_f,
            "atm_reference": atm_strike,
            "moneyness_bucket": moneyness,
            "distance_from_atm_abs": round(dist_abs, 2),
            "distance_from_atm_pct": round(dist_pct, 2),
            "ltp": ltp_val,
            "change": round(change_rs, 2),
            "change_percent": round(change_pct, 2),
            "top_bid_price": bid,
            "top_ask_price": ask,
            "bid": bid,
            "ask": ask,
            "bid_ask_spread": round(spread, 2),
            "bid_ask_spread_pct": round(spread_pct, 2),
            "volume": volume,
            "oi": oi,
            "oi_change": oi_change,
            "oi_change_pct": round(oi_change_pct, 2),
            "iv": float(row.get("iv", 0) or 0),
            "iv_change": float(row.get("iv_change", 0) or 0),
            "delta": float(row.get("delta", 0) or 0),
            "gamma": float(row.get("gamma", 0) or 0),
            "theta": float(row.get("theta", 0) or 0),
            "vega": float(row.get("vega", 0) or 0),
            "rho": float(row.get("rho", 0) or 0),
            "intrinsic_value": round(intrinsic, 2),
            "time_value": round(time_val, 2),
            "lot_size": lot_size,
            "turnover": round(volume * ltp_val, 2),
            "liquidity_score": liquidity_score,
            "buildup_type": buildup,
            "support_resistance_tag": "ATM" if moneyness == "ATM" else "",
            "unusual_activity_flag": unusual_flag,
            "previous_close_price": prev_close,
            "security_id": row.get("security_id") or row.get("token"),
            "trading_symbol": row.get("trading_symbol") or row.get("tradingSymbol") or row.get("symbol"),
            "source": row_source,
            "data_source": row_source,
            "verification_status": "VERIFIED_DHAN" if row_source == "dhan" else "SIMULATED",
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
    pe_vol = sum(c["volume"] for c in contracts if c["option_type"] == "PE")
    ce_vol = sum(c["volume"] for c in contracts if c["option_type"] == "CE")
    pcr = float(pe_oi / ce_oi) if ce_oi > 0 else 1.0

    pcr_context = "BULLISH" if pcr > 1.2 else "BEARISH" if pcr < 0.8 else "NEUTRAL"
    max_pain = _calculate_max_pain(unique_strikes, ce_oi_map, pe_oi_map)

    # Mark support and resistance tags based on highest PE OI (support) and highest CE OI (resistance)
    if pe_oi_map:
        max_pe_strike = max(pe_oi_map, key=pe_oi_map.get)
        for c in contracts:
            if c["strike"] == max_pe_strike and c["option_type"] == "PE":
                c["support_resistance_tag"] = "MAJOR_SUPPORT"
    if ce_oi_map:
        max_ce_strike = max(ce_oi_map, key=ce_oi_map.get)
        for c in contracts:
            if c["strike"] == max_ce_strike and c["option_type"] == "CE":
                c["support_resistance_tag"] = "MAJOR_RESISTANCE"

    source = _normalize_chain_source(contracts[0].get("source", "dhan"))
    configured_limit = _configured_chain_limit()
    is_live = bool(spot_f > 0 and source == "dhan")

    return {
        "underlying": underlying.upper(),
        "spot": spot_f,
        "atm_strike": atm_strike,
        "max_pain": max_pain,
        "pcr": round(pcr, 3),
        "pcr_context": pcr_context,
        "total_ce_oi": ce_oi,
        "total_pe_oi": pe_oi,
        "total_ce_volume": ce_vol,
        "total_pe_volume": pe_vol,
        "contracts": contracts,
        "total_contracts": len(contracts),
        "broker_rows_total": broker_rows_total,
        "data_source": source,
        "data_mode": "LIVE" if is_live else "SIMULATION",
        "verification_status": "VERIFIED_LIVE" if is_live else "VERIFIED_SIMULATION",
        "reason_if_unverified": None if is_live else "Chain normalized from simulation/offline dataset (market closed).",
        "as_of_utc": datetime.now(timezone.utc).isoformat(),
        "freshness_seconds": 1.0,
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
