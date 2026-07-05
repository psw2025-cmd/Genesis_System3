"""
NSE equity (stock) F&O universe — OPTSTK underlyings from Dhan security master.

NSE lists ~140 securities with stock options (OPTSTK) vs index options (OPTIDX).
References:
  - https://www.nseindia.com/products/content/derivatives/equities/contract_specifitns.htm
  - Dhan instrument master: SEM_INSTRUMENT_NAME = OPTSTK
"""

from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Set

ROOT = Path(__file__).resolve().parents[3]
SECURITY_MASTER = ROOT / "security_id_list.csv"

# Liquid F&O names used for live scanner priority (subset of full universe)
PRIORITY_EQUITY_FO = [
    "RELIANCE",
    "TCS",
    "HDFCBANK",
    "INFY",
    "ICICIBANK",
    "SBIN",
    "BHARTIARTL",
    "ITC",
    "KOTAKBANK",
    "LT",
    "AXISBANK",
    "MARUTI",
    "TATAMOTORS",
    "SUNPHARMA",
    "BAJFINANCE",
    "HINDUNILVR",
    "WIPRO",
    "ADANIENT",
    "TATASTEEL",
    "NTPC",
]


@lru_cache(maxsize=1)
def load_equity_fo_universe() -> Dict[str, Any]:
    """Load unique NSE stock underlyings with OPTSTK contracts from security master."""
    underlyings: Set[str] = set()
    contract_count = 0
    sample_contracts: List[Dict[str, Any]] = []

    if not SECURITY_MASTER.exists():
        return {
            "source": "missing_security_master",
            "underlying_count": 0,
            "contract_count": 0,
            "underlyings": [],
            "priority_underlyings": PRIORITY_EQUITY_FO,
            "implemented": False,
        }

    with SECURITY_MASTER.open(encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            exch = (row.get("SEM_EXM_EXCH_ID") or row.get("EXCH_ID") or "").strip().upper()
            inst = (row.get("SEM_INSTRUMENT_NAME") or row.get("INSTRUMENT") or "").strip().upper()
            seg = (row.get("SEM_SEGMENT") or row.get("SEGMENT") or "").strip().upper()
            if exch != "NSE" or inst != "OPTSTK":
                continue
            if seg and seg not in ("D", "DERIVATIVES"):
                continue
            name = (row.get("SM_SYMBOL_NAME") or row.get("SYMBOL_NAME") or "").strip().upper()
            if not name:
                sym = row.get("SEM_TRADING_SYMBOL") or row.get("SEM_CUSTOM_SYMBOL") or ""
                if "-" in sym:
                    name = sym.split("-")[0].upper()
            if not name:
                continue
            underlyings.add(name)
            contract_count += 1
            if len(sample_contracts) < 5:
                sample_contracts.append(
                    {
                        "underlying": name,
                        "trading_symbol": row.get("SEM_TRADING_SYMBOL") or row.get("SEM_CUSTOM_SYMBOL"),
                        "strike": row.get("SEM_STRIKE_PRICE"),
                        "option_type": row.get("SEM_OPTION_TYPE"),
                        "expiry_date": (row.get("SEM_EXPIRY_DATE") or "")[:10],
                        "lot_size": row.get("SEM_LOT_UNITS"),
                        "security_id": row.get("SEM_SMST_SECURITY_ID"),
                    }
                )

    sorted_names = sorted(underlyings)
    priority = [s for s in PRIORITY_EQUITY_FO if s in underlyings]
    return {
        "source": "security_id_list.csv",
        "underlying_count": len(sorted_names),
        "contract_count": contract_count,
        "underlyings": sorted_names,
        "priority_underlyings": priority,
        "sample_contracts": sample_contracts,
        "implemented": len(sorted_names) > 0,
        "instrument_type": "OPTSTK",
        "exchange": "NSE_FNO",
    }


def is_equity_fo_symbol(symbol: str) -> bool:
    sym = (symbol or "").strip().upper()
    if not sym:
        return False
    universe = load_equity_fo_universe()
    return sym in set(universe.get("underlyings") or [])


INDEX_FO_SYMBOLS = {"NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX", "BANKEX"}


def is_tradeable_fo_symbol(symbol: str) -> bool:
    """True for index F&O or NSE equity F&O underlyings; blocks cash-only movers."""
    sym = (symbol or "").strip().upper()
    if not sym:
        return False
    if sym in INDEX_FO_SYMBOLS:
        return True
    return is_equity_fo_symbol(sym)
