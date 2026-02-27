import os
import sys
import json
import pandas as pd

# -------------------------------------------------------
# Path setup
# -------------------------------------------------------
# This file is in: core/brokers/angel_one/instruments.py
# Project root is: C:/Genesis_System3
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from core.utils.logger import logger
from core.data.instruments_cache import get_instruments_df

# Local JSON copy of Angel One ScripMaster
# Expected location:
#   C:/Genesis_System3/storage/instruments/OpenAPIScripMaster.json
INSTRUMENT_JSON = os.path.join(ROOT_DIR, "storage", "instruments", "OpenAPIScripMaster.json")


def load_instruments() -> pd.DataFrame | None:
    """
    Load AngelOne instruments master from local JSON (OpenAPIScripMaster.json).
    NOW USES CACHE - loads once, returns cached DataFrame.

    JSON is a list of dicts with keys like:
      token, symbol, name, expiry, strike, lotsize, instrumenttype, exch_seg, tick_size

    Returns:
        pandas.DataFrame or None on error.
    """
    # Use cache instead of loading from disk every time
    return get_instruments_df()
    """
    Load AngelOne instruments master from local JSON (OpenAPIScripMaster.json).

    JSON is a list of dicts with keys like:
      token, symbol, name, expiry, strike, lotsize, instrumenttype, exch_seg, tick_size

    Returns:
        pandas.DataFrame or None on error.
    """
    if not os.path.exists(INSTRUMENT_JSON):
        logger.error(f"Instrument JSON not found: {INSTRUMENT_JSON}")
        return None

    try:
        with open(INSTRUMENT_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            logger.error("Instrument JSON is not a list.")
            return None

        df = pd.DataFrame(data)
        logger.info(f"Loaded instruments from JSON: {len(df)} rows")
        return df
    except Exception as e:
        logger.error(f"Failed to read instruments JSON: {e}")
        return None


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
