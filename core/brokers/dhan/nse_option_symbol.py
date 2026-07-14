"""
NSE / Dhan F&O option contract symbol resolver.

Conventions (NSE index options, Dhan SEM_TRADING_SYMBOL):
  Monthly / weekly (Dhan compact):  {UNDERLYING}{DDMMMYY}{STRIKE}{CE|PE}
  Example: NIFTY05FEB2623500CE  →  NIFTY, 05-Feb-2026, strike 23500, Call

References:
  - NSE contract specs: https://www.nseindia.com/products/content/derivatives/equities/contract_specifitns.htm
  - Dhan instrument master: https://dhanhq.co/docs/v2/instruments/
  - OpenAlgo symbol format: https://docs.openalgo.in/symbol-format
"""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Union

try:
    from core.data.instruments_cache import get_instruments_df
except ImportError:
    get_instruments_df = None

# NSE index F&O defaults (lot size used when instrument master unavailable)
INDEX_FO_DEFAULTS: Dict[str, Dict[str, Any]] = {
    "NIFTY": {"lot_size": 50, "strike_step": 50, "exchange_segment": "NSE_FNO"},
    "BANKNIFTY": {"lot_size": 15, "strike_step": 100, "exchange_segment": "NSE_FNO"},
    "FINNIFTY": {"lot_size": 40, "strike_step": 50, "exchange_segment": "NSE_FNO"},
    "MIDCPNIFTY": {"lot_size": 75, "strike_step": 25, "exchange_segment": "NSE_FNO"},
    "SENSEX": {"lot_size": 10, "strike_step": 100, "exchange_segment": "BSE_FNO"},
    "BANKEX": {"lot_size": 15, "strike_step": 100, "exchange_segment": "BSE_FNO"},
}

_MONTHS = "JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC"
_UNDERLYINGS = "|".join(sorted(INDEX_FO_DEFAULTS.keys(), key=len, reverse=True))

# Dhan/NSE compact: NIFTY05FEB2623500CE
_TRADING_SYMBOL_RE = re.compile(
    rf"^(?P<underlying>{_UNDERLYINGS})"
    rf"(?P<expiry>\d{{2}}(?:{_MONTHS})\d{{2}})"
    rf"(?P<strike>\d+(?:\.\d+)?)"
    rf"(?P<option_type>CE|PE)$",
    re.IGNORECASE,
)


def _parse_stock_trading_symbol(sym: str) -> Optional[Dict[str, Any]]:
    """Parse stock OPTSTK symbol — supports YYMMM and DDMMMYY (OpenAlgo/NSE)."""
    m = re.match(
        rf"^(?P<underlying>[A-Z][A-Z0-9&]+?)"
        rf"(?P<yy>\d{{2}})(?P<mon>{_MONTHS})"
        rf"(?P<strike>\d+(?:\.\d+)?)"
        rf"(?P<option_type>CE|PE)$",
        sym,
        re.IGNORECASE,
    )
    if not m:
        return None
    g = m.groupdict()
    yy = int(g["yy"])
    mon = g["mon"].upper()
    strike = float(g["strike"])
    # Disambiguate DDMMMYY (VEDL25APR24292.5CE) vs YYMMM (RELIANCE25JUN2500CE)
    underlying = g["underlying"].upper()
    if len(mon) == 3 and strike > 10000 and yy <= 31:
        # Likely DDMMMYY merged: 25APR24 + 292.5 misparsed as yy=25 mon=APR strike=24292.5
        dm = re.match(
            rf"^(?P<u>[A-Z][A-Z0-9&]+)(?P<dd>\d{{2}})(?P<mon>{_MONTHS})(?P<yy>\d{{2}})(?P<strike>\d+(?:\.\d+)?)(?P<opt>CE|PE)$",
            sym,
            re.I,
        )
        if dm:
            dg = dm.groupdict()
            return {
                "underlying": dg["u"].upper(),
                "expiry_date": date(int(dg["yy"]) + 2000, _MONTH_MAP[dg["mon"].upper()], int(dg["dd"])).isoformat(),
                "strike": float(dg["strike"]),
                "option_type": dg["opt"].upper(),
                "trading_symbol": sym,
                "symbol_format": "DDMMMYY",
                "instrument_type": "OPTSTK",
            }
    return {
        "underlying": underlying,
        "expiry_date": date(2000 + yy, _MONTH_MAP[mon], 1).isoformat(),
        "strike": strike,
        "option_type": g["option_type"].upper(),
        "trading_symbol": sym,
        "symbol_format": "YYMMM",
        "instrument_type": "OPTSTK",
    }


_WEEKLY_SYMBOL_RE = re.compile(
    rf"^(?P<underlying>{_UNDERLYINGS})"
    rf"(?P<yy>\d{{2}})(?P<m>\d)(?P<dd>\d{{2}})"
    rf"(?P<strike>\d+(?:\.\d+)?)"
    rf"(?P<option_type>CE|PE)$",
    re.IGNORECASE,
)

_MONTH_MAP = {
    "JAN": 1,
    "FEB": 2,
    "MAR": 3,
    "APR": 4,
    "MAY": 5,
    "JUN": 6,
    "JUL": 7,
    "AUG": 8,
    "SEP": 9,
    "OCT": 10,
    "NOV": 11,
    "DEC": 12,
}


def _parse_expiry_input(expiry: Union[str, date, datetime, None]) -> Optional[date]:
    if expiry is None:
        return None
    if isinstance(expiry, datetime):
        return expiry.date()
    if isinstance(expiry, date):
        return expiry
    text = str(expiry).strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d%b%Y", "%d-%b-%Y"):
        try:
            return datetime.strptime(text[:10] if fmt == "%Y-%m-%d" else text, fmt).date()
        except ValueError:
            continue
    # DDMMMYYYY e.g. 30DEC2024 (synthetic chain generator)
    m = re.match(rf"^(\d{{2}})({_MONTHS})(\d{{4}})$", text.upper())
    if m:
        dd, mon, yyyy = m.groups()
        return date(int(yyyy), _MONTH_MAP[mon], int(dd))
    # DDMMMYY e.g. 05FEB26
    m = re.match(rf"^(\d{{2}})({_MONTHS})(\d{{2}})$", text.upper())
    if m:
        dd, mon, yy = m.groups()
        return date(2000 + int(yy), _MONTH_MAP[mon], int(dd))
    return None


def _format_strike(strike: float) -> str:
    if float(strike) == int(strike):
        return str(int(strike))
    return str(strike)


def build_trading_symbol(
    underlying: str,
    expiry: Union[str, date, datetime],
    strike: float,
    option_type: str,
) -> str:
    """Build Dhan/NSE compact trading symbol: NIFTY05FEB2623500CE."""
    exp = _parse_expiry_input(expiry)
    if exp is None:
        raise ValueError(f"Invalid expiry: {expiry!r}")
    dd = exp.strftime("%d")
    mmm = exp.strftime("%b").upper()
    yy = exp.strftime("%y")
    opt = option_type.upper().strip()
    if opt not in ("CE", "PE"):
        raise ValueError(f"option_type must be CE or PE, got {option_type!r}")
    return f"{underlying.upper()}{dd}{mmm}{yy}{_format_strike(strike)}{opt}"


def parse_trading_symbol(trading_symbol: str) -> Optional[Dict[str, Any]]:
    """Parse NSE/Dhan option trading symbol into components."""
    sym = (trading_symbol or "").strip().upper()
    if not sym:
        return None

    m = _TRADING_SYMBOL_RE.match(sym)
    if m:
        g = m.groupdict()
        exp_txt = g["expiry"]
        dd = int(exp_txt[:2])
        mon = exp_txt[2:5]
        yy = int(exp_txt[5:7])
        return {
            "underlying": g["underlying"].upper(),
            "expiry_date": date(2000 + yy, _MONTH_MAP[mon], dd).isoformat(),
            "strike": float(g["strike"]),
            "option_type": g["option_type"].upper(),
            "trading_symbol": sym,
            "symbol_format": "DDMMMYY",
            "instrument_type": "OPTIDX",
        }

    stock = _parse_stock_trading_symbol(sym)
    if stock:
        return stock

    m = _WEEKLY_SYMBOL_RE.match(sym)
    if m:
        g = m.groupdict()
        yy = int(g["yy"])
        month = int(g["m"])
        dd = int(g["dd"])
        return {
            "underlying": g["underlying"].upper(),
            "expiry_date": date(2000 + yy, month, dd).isoformat(),
            "strike": float(g["strike"]),
            "option_type": g["option_type"].upper(),
            "trading_symbol": sym,
            "symbol_format": "YYMDD",
        }
    return None


_INSTRUMENTS_BY_SYMBOL = None
_INSTRUMENTS_BY_KEY = None
_LAST_DF_ID = None


def _lookup_instrument_master(
    underlying: str,
    strike: float,
    option_type: str,
    expiry_date: Optional[date] = None,
    trading_symbol: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    global _INSTRUMENTS_BY_SYMBOL, _INSTRUMENTS_BY_KEY, _LAST_DF_ID
    if get_instruments_df is None:
        return None

    df = get_instruments_df()
    if df is None or df.empty:
        return None

    if _LAST_DF_ID != id(df) or _INSTRUMENTS_BY_SYMBOL is None:
        cols = {c.lower(): c for c in df.columns}
        ex_col = cols.get("exch_seg")
        name_col = cols.get("name")
        sym_col = cols.get("symbol")
        strike_col = cols.get("strike")
        expiry_col = cols.get("expiry")
        token_col = cols.get("token")
        lot_col = cols.get("lotsize") or cols.get("lot_size")
        inst_col = cols.get("instrumenttype")

        sub = df.copy()
        if ex_col:
            sub = sub[sub[ex_col].astype(str).str.upper().isin(["NFO", "BFO"])]
        if inst_col:
            sub = sub[sub[inst_col].astype(str).str.contains("OPT", na=False)]

        by_sym = {}
        by_key = {}
        if not sub.empty:
            records = sub.to_dict("records")
            for r in records:
                sym_val = str(r.get(sym_col) or "").strip().upper()
                if sym_val:
                    by_sym[sym_val] = r
                underlying_val = str(r.get(name_col) or "").strip().upper()
                try:
                    strike_val = float(r.get(strike_col) or 0.0)
                except (ValueError, TypeError):
                    strike_val = 0.0
                opt_val = "CE" if sym_val.endswith("CE") else ("PE" if sym_val.endswith("PE") else "")
                expiry_val = str(r.get(expiry_col) or "")[:10]
                if underlying_val and strike_val > 0 and opt_val and expiry_val:
                    key = (underlying_val, strike_val, opt_val, expiry_val)
                    by_key[key] = r

        _INSTRUMENTS_BY_SYMBOL = by_sym
        _INSTRUMENTS_BY_KEY = by_key
        _LAST_DF_ID = id(df)

    cols = {c.lower(): c for c in df.columns}
    name_col = cols.get("name")
    sym_col = cols.get("symbol")
    strike_col = cols.get("strike")
    expiry_col = cols.get("expiry")
    token_col = cols.get("token")
    lot_col = cols.get("lotsize") or cols.get("lot_size")

    row = None
    if trading_symbol:
        row = _INSTRUMENTS_BY_SYMBOL.get(trading_symbol.upper())
    else:
        exp_str = expiry_date.strftime("%Y-%m-%d") if expiry_date else ""
        if exp_str:
            row = _INSTRUMENTS_BY_KEY.get((underlying.upper(), float(strike), option_type.upper(), exp_str))

    if row is None:
        return None

    sym_val = str(row[sym_col]) if sym_col and row.get(sym_col) is not None else None
    exp_val = (
        str(row[expiry_col])[:10]
        if expiry_col and row.get(expiry_col) is not None
        else (expiry_date.isoformat() if expiry_date else None)
    )
    return {
        "trading_symbol": sym_val,
        "security_id": str(row[token_col]) if token_col else None,
        "underlying": underlying.upper(),
        "strike": float(row[strike_col]) if strike_col else float(strike),
        "option_type": option_type.upper(),
        "expiry_date": exp_val,
        "lot_size": int(row[lot_col]) if lot_col and row.get(lot_col) is not None else None,
        "exchange_segment": "NSE_FNO",
        "resolved_from": "instrument_master",
    }


def resolve_option_contract(
    underlying: str,
    strike: float,
    option_type: str,
    expiry_date: Union[str, date, datetime, None] = None,
    trading_symbol: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Resolve full contract identity: prefer instrument master, else build symbol.
    """
    underlying_u = underlying.upper()
    opt = option_type.upper().strip()
    exp = _parse_expiry_input(expiry_date)

    if trading_symbol:
        parsed = parse_trading_symbol(trading_symbol)
        if parsed:
            underlying_u = parsed["underlying"]
            strike = parsed["strike"]
            opt = parsed["option_type"]
            exp = _parse_expiry_input(parsed["expiry_date"])

    master = _lookup_instrument_master(underlying_u, strike, opt, exp, trading_symbol)
    if master:
        defaults = INDEX_FO_DEFAULTS.get(underlying_u, {})
        master.setdefault("lot_size", defaults.get("lot_size"))
        master.setdefault("exchange_segment", defaults.get("exchange_segment", "NSE_FNO"))
        return master

    if exp is None:
        defaults = INDEX_FO_DEFAULTS.get(underlying_u, {})
        return {
            "underlying": underlying_u,
            "strike": float(strike),
            "option_type": opt,
            "trading_symbol": trading_symbol,
            "expiry_date": None,
            "security_id": None,
            "lot_size": defaults.get("lot_size"),
            "exchange_segment": defaults.get("exchange_segment", "NSE_FNO"),
            "resolved_from": "partial",
        }

    built = build_trading_symbol(underlying_u, exp, strike, opt)
    defaults = INDEX_FO_DEFAULTS.get(underlying_u, {})
    return {
        "underlying": underlying_u,
        "strike": float(strike),
        "option_type": opt,
        "trading_symbol": built,
        "expiry_date": exp.isoformat(),
        "security_id": None,
        "lot_size": defaults.get("lot_size"),
        "exchange_segment": defaults.get("exchange_segment", "NSE_FNO"),
        "resolved_from": "built_symbol",
    }


def enrich_option_row(row: Dict[str, Any], default_expiry: Union[str, date, None] = None) -> Dict[str, Any]:
    """Add trading_symbol, expiry_date, security_id, lot_size to a trade/position/chain row."""
    if not isinstance(row, dict):
        return row
    out = dict(row)

    trading_symbol = out.get("trading_symbol") or out.get("tradingSymbol") or out.get("symbol")
    # If symbol is only underlying (NIFTY), do not treat as trading symbol
    if trading_symbol and str(trading_symbol).upper() in INDEX_FO_DEFAULTS:
        trading_symbol = None

    underlying = out.get("underlying") or out.get("name") or ""
    strike = out.get("strike") or out.get("strike_price") or out.get("strikePrice")
    option_type = out.get("option_type") or out.get("optionType") or out.get("drvOptionType")
    expiry = out.get("expiry_date") or out.get("expiry") or out.get("drvExpiryDate") or default_expiry

    if strike is None or not option_type:
        if trading_symbol:
            parsed = parse_trading_symbol(trading_symbol)
            if parsed:
                out.update({k: v for k, v in parsed.items() if k != "symbol_format"})
        return out

    resolved = resolve_option_contract(
        underlying=str(underlying),
        strike=float(strike),
        option_type=str(option_type),
        expiry_date=expiry,
        trading_symbol=str(trading_symbol) if trading_symbol else None,
    )

    out["underlying"] = resolved.get("underlying") or underlying
    out["trading_symbol"] = resolved.get("trading_symbol")
    out["symbol"] = out["trading_symbol"]  # canonical tradable symbol for APIs
    if resolved.get("expiry_date"):
        out["expiry_date"] = resolved["expiry_date"]
    if resolved.get("security_id"):
        out["security_id"] = resolved["security_id"]
    if resolved.get("lot_size") and not out.get("lot_size"):
        out["lot_size"] = resolved["lot_size"]
    out["exchange_segment"] = resolved.get("exchange_segment", "NSE_FNO")
    out["symbol_resolved_from"] = resolved.get("resolved_from")
    return out


def enrich_option_rows(
    rows: List[Dict[str, Any]],
    default_expiry: Union[str, date, None] = None,
) -> List[Dict[str, Any]]:
    return [enrich_option_row(r, default_expiry=default_expiry) for r in rows]
