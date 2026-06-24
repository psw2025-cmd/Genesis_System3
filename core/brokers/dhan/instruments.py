import os
import sys
import json
import pandas as pd

# -------------------------------------------------------
# Path setup
# -------------------------------------------------------
# This file is in: core/brokers/dhan/instruments.py
# Project root is: C:/Genesis_System3
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from core.utils.logger import logger
from core.data.instruments_cache import get_instruments_df

# Local JSON copy of Dhan ScripMaster
# Expected location:
#   C:/Genesis_System3/storage/instruments/OpenAPIScripMaster.json
INSTRUMENT_JSON = os.path.join(ROOT_DIR, "storage", "instruments", "OpenAPIScripMaster.json")


def load_instruments() -> pd.DataFrame | None:
    """
    Load Dhan instruments master from cache (JSON or security_id_list.csv fallback).
    """
    df = get_instruments_df()
    if df is None or df.empty:
        return None
    return df


def find_by_tradingsymbol(exchange: str, tradingsymbol: str) -> dict | None:
    """
    Find a single row by exchange (exch_seg) + tradingsymbol (symbol).

    Example:
        exchange='NSE', tradingsymbol='SBIN-EQ'

    Returns:
        dict of row fields, or None if not found / error.
    """
    df = load_instruments()
    if df is None:
        return None

    cols = {c.lower(): c for c in df.columns}
    ex_col = cols.get("exch_seg")
    sym_col = cols.get("symbol")

    if not ex_col or not sym_col:
        logger.error("Instrument JSON missing exch_seg/symbol columns.")
        return None

    sub = df[(df[ex_col] == exchange) & (df[sym_col] == tradingsymbol)]
    if sub.empty:
        return None
    return sub.iloc[0].to_dict()


def find_options_for_underlying(underlying_name: str, exchange: str = "NFO") -> pd.DataFrame | None:
    """
    Return all option contracts for a given underlying (e.g. 'NIFTY', 'BANKNIFTY').

    For options we expect:
      exch_seg       = exchange (default 'NFO')
      name           = underlying_name (e.g. 'NIFTY', 'BANKNIFTY')
      instrumenttype contains 'OPT' (OPTIDX / OPTSTK)

    Returns:
        pandas.DataFrame of matching rows, or None on error / no matches.
    """
    df = load_instruments()
    if df is None:
        return None

    cols = {c.lower(): c for c in df.columns}
    ex_col = cols.get("exch_seg")
    name_col = cols.get("name")
    inst_col = cols.get("instrumenttype")

    if not ex_col or not name_col or not inst_col:
        logger.error("Instrument JSON missing exch_seg/name/instrumenttype columns.")
        return None

    sub = df[
        (df[ex_col] == exchange) & (df[name_col] == underlying_name) & (df[inst_col].str.contains("OPT", na=False))
    ]

    if sub.empty:
        logger.warning(f"No options found for {underlying_name} on {exchange}")
        return None

    return sub


def find_index_by_name(name: str, exchange: str) -> dict | None:
    """
    Find the index instrument row (used for spot LTP).

    For indices (NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY, SENSEX) Angel uses:
      exch_seg = 'NSE' or 'BSE'
      name     = e.g. 'NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY', 'SENSEX'
      instrumenttype often 'AMXIDX' (but we don't hard-require it).
    """
    df = load_instruments()
    if df is None:
        return None

    cols = {c.lower(): c for c in df.columns}
    ex_col = cols.get("exch_seg")
    name_col = cols.get("name")
    inst_col = cols.get("instrumenttype")

    if not ex_col or not name_col:
        logger.error("Instrument JSON missing exch_seg/name columns.")
        return None

    sub = df[(df[ex_col] == exchange) & (df[name_col] == name)]

    # Prefer rows that look like index types
    if inst_col and not sub.empty:
        idx_like = sub[sub[inst_col].str.contains("IDX", na=False)]
        if not idx_like.empty:
            sub = idx_like

    if sub.empty:
        logger.warning(f"No index row found for {name} on {exchange}")
        return None

    return sub.iloc[0].to_dict()
