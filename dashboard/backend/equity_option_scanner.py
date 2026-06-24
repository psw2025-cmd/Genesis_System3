"""
Equity (stock) option scanner — highest momentum CE/PE from NSE bhavcopy OPTSTK rows.

Stock options use OPTSTK (NSE) vs OPTIDX for indices.
When prior close unavailable (EOD bhavcopy), ranks by OI buildup % and volume.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from core.brokers.dhan.equity_fo_universe import PRIORITY_EQUITY_FO, load_equity_fo_universe

ROOT = Path(__file__).resolve().parents[2]
BHAVCOPY_DIR = ROOT / "storage" / "bhavcopy"

INDEX_SEGMENTS = {"NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX", "BANKEX", "NIFTYNXT50"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _load_latest_bhavcopy_df() -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    if not BHAVCOPY_DIR.exists():
        return None, None
    files = sorted(BHAVCOPY_DIR.glob("*_fo_bhavcopy.csv"), reverse=True)
    if not files:
        return None, None
    path = files[0]
    try:
        return pd.read_csv(path, low_memory=False), path.stem.replace("_fo_bhavcopy", "")
    except Exception:
        return None, None


def _parse_equity_option_rows(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Extract NSE stock option rows from UDiFF or legacy bhavcopy."""
    cols = set(df.columns)
    if "TckrSymb" in cols:
        sym_col, opt_col = "TckrSymb", "OptnTp"
        strike_col = "StrkPric" if "StrkPric" in cols else "STRIKE_PR"
        oi_col = "OpnIntrst" if "OpnIntrst" in cols else "OPEN_INT"
        oi_chg_col = "ChngInOpnIntrst" if "ChngInOpnIntrst" in cols else "CHG_IN_OI"
        vol_col = "TtlTradgVol" if "TtlTradgVol" in cols else "CONTRACTS"
        ltp_col = "ClsPric" if "ClsPric" in cols else "CLOSE"
        exp_col = "XpryDt" if "XpryDt" in cols else "EXPIRY_DT"
        type_col = "FinInstrmTp" if "FinInstrmTp" in cols else None
    elif "SYMBOL" in cols:
        sym_col, opt_col = "SYMBOL", "OPTION_TYP"
        strike_col, oi_col = "STRIKE_PR", "OPEN_INT"
        oi_chg_col, vol_col, ltp_col, exp_col = "CHG_IN_OI", "CONTRACTS", "CLOSE", "EXPIRY_DT"
        type_col = "INSTRUMENT"
    else:
        return []

    sub = df[df[opt_col].astype(str).str.upper().isin(["CE", "PE"])].copy()
    if type_col and type_col in sub.columns:
        # Stock options: STO / OPTSTK; exclude index IDO / OPTIDX
        inst = sub[type_col].astype(str).str.upper()
        sub = sub[inst.isin(["STO", "OPTSTK", "STOCK OPTIONS"]) | (~inst.isin(["IDO", "OPTIDX", "INDEX OPTIONS"]))]
    # Exclude index underlyings
    sub = sub[~sub[sym_col].astype(str).str.upper().isin(INDEX_SEGMENTS)]

    rows: List[Dict[str, Any]] = []
    for _, r in sub.iterrows():
        underlying = str(r[sym_col]).strip().upper()
        opt = str(r[opt_col]).strip().upper()
        try:
            oi = float(r.get(oi_col) or 0)
            oi_chg = float(r.get(oi_chg_col) or 0)
            ltp = float(r.get(ltp_col) or 0)
            vol = float(r.get(vol_col) or 0)
            strike = float(r.get(strike_col) or 0)
        except (TypeError, ValueError):
            continue
        if ltp <= 0 or strike <= 0:
            continue
        prev_oi = max(oi - oi_chg, 1)
        oi_buildup_pct = (oi_chg / prev_oi) * 100.0
        rows.append(
            {
                "underlying": underlying,
                "option_type": opt,
                "strike": strike,
                "ltp": ltp,
                "oi": int(oi),
                "oi_change": int(oi_chg),
                "volume": int(vol),
                "gain_pct": round(oi_buildup_pct, 4),
                "gain_metric": "oi_buildup_pct",
                "expiry_date": str(r.get(exp_col) or "")[:10],
                "instrument_type": "OPTSTK",
            }
        )
    return rows


def _enrich_trading_symbol(row: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from core.brokers.dhan.nse_option_symbol import enrich_option_row

        return enrich_option_row({**row, "symbol_resolved_from": "equity_scanner"})
    except Exception:
        return row


def scan_equity_top_gainers(
    rows: List[Dict[str, Any]],
    priority_only: bool = False,
    top_n: int = 10,
) -> Dict[str, Any]:
    if priority_only:
        allowed = set(PRIORITY_EQUITY_FO)
        rows = [r for r in rows if r["underlying"] in allowed]

    ce = sorted([r for r in rows if r["option_type"] == "CE"], key=lambda x: x["gain_pct"], reverse=True)
    pe = sorted([r for r in rows if r["option_type"] == "PE"], key=lambda x: x["gain_pct"], reverse=True)

    by_stock: Dict[str, Dict[str, Any]] = {}
    for r in rows:
        u = r["underlying"]
        if u not in by_stock:
            by_stock[u] = {"underlying": u, "top_ce": None, "top_pe": None}
        slot = "top_ce" if r["option_type"] == "CE" else "top_pe"
        cur = by_stock[u][slot]
        if cur is None or r["gain_pct"] > cur["gain_pct"]:
            by_stock[u][slot] = _enrich_trading_symbol(r)

    return {
        "market_top_ce": _enrich_trading_symbol(ce[0]) if ce else None,
        "market_top_pe": _enrich_trading_symbol(pe[0]) if pe else None,
        "top_ce_list": [_enrich_trading_symbol(r) for r in ce[:top_n]],
        "top_pe_list": [_enrich_trading_symbol(r) for r in pe[:top_n]],
        "stocks_scanned": len(by_stock),
        "by_stock_sample": list(by_stock.values())[:top_n],
    }


def build_equity_options_report(top_n: int = 10, priority_only: bool = False) -> Dict[str, Any]:
    universe = load_equity_fo_universe()
    df, bhav_date = _load_latest_bhavcopy_df()
    rows = _parse_equity_option_rows(df) if df is not None else []
    scan = scan_equity_top_gainers(rows, priority_only=priority_only, top_n=top_n) if rows else {}

    segments = {
        "index_options": {
            "implemented": True,
            "segments": ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"],
            "instrument_type": "OPTIDX",
            "api": "/api/scanner/top_contract_gainers",
        },
        "equity_options": {
            "implemented": bool(universe.get("implemented")),
            "underlying_count": universe.get("underlying_count", 0),
            "contract_count": universe.get("contract_count", 0),
            "instrument_type": "OPTSTK",
            "exchange": "NSE_FNO",
            "api": "/api/scanner/equity_options",
            "bhavcopy_date": bhav_date,
            "contracts_parsed": len(rows),
            "live_chain_per_stock": False,
            "note": "Full per-stock Dhan chain scan deferred — uses bhavcopy OPTSTK + security master",
        },
        "cash_equity": {
            "implemented": True,
            "scope": "FORECAST_ONLY_CASH_EQUITY",
            "broker_api": "/api/broker/holdings",
            "note": "Holdings read-only; not ranked for option paper trade",
        },
    }

    return {
        "generated_utc": _utc_now(),
        "status": "ok" if universe.get("implemented") else "partial",
        "segments": segments,
        "universe": universe,
        "scanner": {
            **scan,
            "gain_metric": "oi_buildup_pct",
            "gain_metric_note": "Bhavcopy EOD — OI buildup % used when intraday LTP change unavailable",
            "bhavcopy_date": bhav_date,
            "data_available": bool(rows),
        },
        "implementation_gaps": [
            g for g in [
                "LIVE_PER_STOCK_DHAN_CHAIN" if not segments["equity_options"].get("live_chain_per_stock") else None,
                "BHAVCOPY_LOCAL" if not bhav_date else None,
                "INTRADAY_PRICE_GAIN" if rows and rows[0].get("gain_metric") == "oi_buildup_pct" else None,
            ] if g
        ],
    }
