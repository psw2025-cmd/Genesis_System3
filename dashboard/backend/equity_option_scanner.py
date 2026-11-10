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

    if sub.empty:
        return []

    # Vectorized numeric conversions
    sub[strike_col] = pd.to_numeric(sub[strike_col], errors="coerce").fillna(0.0)
    sub[ltp_col] = pd.to_numeric(sub[ltp_col], errors="coerce").fillna(0.0)
    sub[oi_col] = pd.to_numeric(sub[oi_col], errors="coerce").fillna(0.0)
    sub[oi_chg_col] = pd.to_numeric(sub[oi_chg_col], errors="coerce").fillna(0.0)
    sub[vol_col] = pd.to_numeric(sub[vol_col], errors="coerce").fillna(0.0)

    # Filter invalid prices/strikes
    sub = sub[(sub[ltp_col] > 0) & (sub[strike_col] > 0)]
    if sub.empty:
        return []

    prev_oi = (sub[oi_col] - sub[oi_chg_col]).clip(lower=1.0)
    sub["gain_pct"] = (sub[oi_chg_col] / prev_oi * 100.0).round(4)

    # Create final structured DataFrame
    res_df = pd.DataFrame(
        {
            "underlying": sub[sym_col].astype(str).str.strip().str.upper(),
            "option_type": sub[opt_col].astype(str).str.strip().str.upper(),
            "strike": sub[strike_col],
            "ltp": sub[ltp_col],
            "oi": sub[oi_col].astype(int),
            "oi_change": sub[oi_chg_col].astype(int),
            "volume": sub[vol_col].astype(int),
            "gain_pct": sub["gain_pct"],
            "gain_metric": "oi_buildup_pct",
            "expiry_date": sub[exp_col].astype(str).str.slice(0, 10) if exp_col in sub.columns else "",
            "instrument_type": "OPTSTK",
        }
    )

    return res_df.to_dict("records")


def _enrich_trading_symbol(row: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from core.brokers.dhan.nse_option_symbol import enrich_option_row

        return enrich_option_row({**row, "symbol_resolved_from": "equity_scanner"})
    except Exception:
        return row


def _rows_from_chain_payload(sym: str, chain: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for c in chain.get("contracts") or []:
        if not isinstance(c, dict):
            continue
        opt = str(c.get("option_type") or "").upper()
        if opt not in {"CE", "PE"}:
            continue
        try:
            ltp = float(c.get("ltp") or 0)
            strike = float(c.get("strike") or 0)
        except (TypeError, ValueError):
            continue
        if ltp <= 0 or strike <= 0:
            continue
        oi_chg = int(c.get("oi_change") or c.get("dOI") or 0)
        out.append(
            {
                "underlying": str(sym).upper(),
                "option_type": opt,
                "strike": strike,
                "ltp": ltp,
                "oi": int(c.get("oi") or 0),
                "oi_change": oi_chg,
                "volume": int(c.get("volume") or 0),
                "gain_pct": float(oi_chg),
                "gain_metric": "live_oi_change",
                "expiry_date": str(c.get("expiry_date") or chain.get("expiry_date") or "")[:10],
                "instrument_type": "OPTSTK",
            }
        )
    return out


def _equity_rows_from_app_chain_cache() -> Tuple[List[Dict[str, Any]], Dict[str, Any], int]:
    rows: List[Dict[str, Any]] = []
    live_chains: Dict[str, Any] = {}
    live_ok = 0
    symbols = list(dict.fromkeys([*PRIORITY_EQUITY_FO, "POWERGRID"]))
    app_mod = None
    try:
        from dashboard.backend import app as app_mod  # type: ignore
    except Exception:
        app_mod = None
    for sym in symbols[:12]:
        chain = None
        if app_mod is not None:
            getter = getattr(app_mod, "_chain_from_push_cache", None)
            if callable(getter):
                try:
                    chain = getter(sym)
                except Exception:
                    chain = None
            if chain is None:
                cache_get = getattr(app_mod, "_cache_get", None)
                if callable(cache_get):
                    try:
                        hit = cache_get(f"chain_{sym}", 400.0)
                        if isinstance(hit, dict):
                            chain = hit
                    except Exception:
                        chain = None
        if not isinstance(chain, dict):
            snap = ROOT / "state" / "chain_cache" / f"{sym}.json"
            if snap.exists():
                try:
                    import json

                    loaded = json.loads(snap.read_text(encoding="utf-8"))
                    chain = loaded.get("data") if isinstance(loaded, dict) and "data" in loaded else loaded
                except Exception:
                    chain = None
        if not isinstance(chain, dict) or not (chain.get("contracts") or []):
            continue
        parsed = _rows_from_chain_payload(sym, chain)
        if not parsed:
            continue
        live_ok += 1
        live_chains[sym] = {
            "underlying": sym,
            "spot": chain.get("spot"),
            "total_contracts": chain.get("total_contracts") or len(chain.get("contracts") or []),
            "pcr": chain.get("pcr"),
            "expiry_date": chain.get("expiry_date"),
            "status": chain.get("status"),
            "data_source": chain.get("data_source"),
            "sample_contracts": (chain.get("contracts") or [])[:6],
        }
        rows.extend(parsed)
    return rows, live_chains, live_ok


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
            by_stock[u][slot] = r

    by_stock_sample = []
    for stock_info in list(by_stock.values())[:top_n]:
        sample = {
            "underlying": stock_info["underlying"],
            "top_ce": _enrich_trading_symbol(stock_info["top_ce"]) if stock_info["top_ce"] else None,
            "top_pe": _enrich_trading_symbol(stock_info["top_pe"]) if stock_info["top_pe"] else None,
        }
        by_stock_sample.append(sample)

    return {
        "market_top_ce": _enrich_trading_symbol(ce[0]) if ce else None,
        "market_top_pe": _enrich_trading_symbol(pe[0]) if pe else None,
        "top_ce_list": [_enrich_trading_symbol(r) for r in ce[:top_n]],
        "top_pe_list": [_enrich_trading_symbol(r) for r in pe[:top_n]],
        "stocks_scanned": len(by_stock),
        "by_stock_sample": by_stock_sample,
    }


def build_equity_options_report(top_n: int = 10, priority_only: bool = False) -> Dict[str, Any]:
    universe = load_equity_fo_universe()
    df, bhav_date = _load_latest_bhavcopy_df()
    rows = _parse_equity_option_rows(df) if df is not None else []
    live_chains: Dict[str, Any] = {}
    live_chain_ok = 0

    # When bhavcopy is absent, reuse last-good Dhan equity chains already in
    # the dashboard cache. Extra OC fetches here starve the paced index stream.
    if not rows:
        cached_rows, cached_chains, cached_ok = _equity_rows_from_app_chain_cache()
        rows.extend(cached_rows)
        live_chains.update(cached_chains)
        live_chain_ok += cached_ok

    scan = scan_equity_top_gainers(rows, priority_only=priority_only, top_n=top_n) if rows else {}

    segments = {
        "index_options": {
            "implemented": True,
            "segments": ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"],
            "instrument_type": "OPTIDX",
            "api": "/api/scanner/top_contract_gainers",
        },
        "equity_options": {
            "implemented": bool(universe.get("implemented")) or live_chain_ok > 0,
            "underlying_count": universe.get("underlying_count", 0),
            "contract_count": universe.get("contract_count", 0),
            "instrument_type": "OPTSTK",
            "exchange": "NSE_FNO",
            "api": "/api/scanner/equity_options",
            "bhavcopy_date": bhav_date,
            "contracts_parsed": len(rows),
            "live_chain_per_stock": live_chain_ok > 0,
            "live_chains_ok": live_chain_ok,
            "note": (
                "Live Dhan equity option chains from last-good cache"
                if live_chain_ok > 0
                else "Waiting for a Dhan equity option-chain snapshot (load RELIANCE/HDFCBANK on Trade tab, or last-good cache)"
            ),
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
        "status": "ok" if (universe.get("implemented") or live_chain_ok > 0) else "partial",
        "segments": segments,
        "universe": universe,
        "live_chains": live_chains,
        "scanner": {
            **scan,
            "gain_metric": "oi_buildup_pct" if bhav_date else ("live_oi_change" if rows else "unavailable"),
            "gain_metric_note": (
                "Bhavcopy EOD — OI buildup % used when intraday LTP change unavailable"
                if bhav_date
                else "Live Dhan option-chain OI change used because local bhavcopy is absent"
            ),
            "bhavcopy_date": bhav_date,
            "data_available": bool(rows),
        },
        "implementation_gaps": [
            g
            for g in [
                "LIVE_PER_STOCK_DHAN_CHAIN" if not segments["equity_options"].get("live_chain_per_stock") else None,
                "BHAVCOPY_LOCAL" if not bhav_date else None,
                "INTRADAY_PRICE_GAIN" if rows and rows[0].get("gain_metric") == "oi_buildup_pct" else None,
            ]
            if g
        ],
    }
