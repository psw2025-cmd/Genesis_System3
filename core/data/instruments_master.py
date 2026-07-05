"""
Dhan instrument master — parse official CSV into normalized OpenAPI-style records.

Supports both column layouts:
  - Legacy bundled: security_id_list.csv (SEM_* columns)
  - Official CDN:   api-scrip-master-detailed.csv (EXCH_ID, SEGMENT, SECURITY_ID, ...)
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd

ROOT_DIR = Path(__file__).parent.parent.parent
INSTRUMENT_DIR = ROOT_DIR / "storage" / "instruments"
SYNCED_DETAILED = INSTRUMENT_DIR / "api-scrip-master-detailed.csv"
SYNCED_COMPACT = INSTRUMENT_DIR / "api-scrip-master.csv"
RUNTIME_JSON = INSTRUMENT_DIR / "OpenAPIScripMaster.json"
BUNDLED_CSV = ROOT_DIR / "security_id_list.csv"
META_JSON = INSTRUMENT_DIR / "master_meta.json"


def _map_exchange(exch: str, segment: str) -> str:
    if exch == "NSE" and segment == "D":
        return "NFO"
    if exch == "BSE" and segment == "D":
        return "BFO"
    return exch or "NSE"


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Unify legacy SEM_* and modern Dhan CDN column names."""
    cols = list(df.columns)
    upper = {c.upper(): c for c in cols}

    if "SEM_EXM_EXCH_ID" in upper or "SEM_SMST_SECURITY_ID" in upper:
        return df.rename(columns={upper.get(k, k): k for k in [
            "SEM_EXM_EXCH_ID", "SEM_SEGMENT", "SEM_SMST_SECURITY_ID",
            "SEM_INSTRUMENT_NAME", "SEM_TRADING_SYMBOL", "SEM_LOT_UNITS",
            "SM_SYMBOL_NAME", "SEM_EXPIRY_DATE", "SEM_STRIKE_PRICE", "SEM_TICK_SIZE",
        ] if k in upper})

    rename = {}
    if "EXCH_ID" in upper:
        field_map = [
            ("EXCH_ID", "SEM_EXM_EXCH_ID"),
            ("SEGMENT", "SEM_SEGMENT"),
            ("SECURITY_ID", "SEM_SMST_SECURITY_ID"),
            ("INSTRUMENT", "SEM_INSTRUMENT_NAME"),
            ("SYMBOL_NAME", "SEM_TRADING_SYMBOL"),
            ("DISPLAY_NAME", "SM_SYMBOL_NAME"),
            ("LOT_SIZE", "SEM_LOT_UNITS"),
            ("SM_EXPIRY_DATE", "SEM_EXPIRY_DATE"),
            ("STRIKE_PRICE", "SEM_STRIKE_PRICE"),
            ("TICK_SIZE", "SEM_TICK_SIZE"),
            ("UNDERLYING_SYMBOL", "UNDERLYING_SYMBOL"),
        ]
        for src, dst in field_map:
            if src in upper:
                rename[upper[src]] = dst
        if "SEM_INSTRUMENT_NAME" not in rename.values() and "INSTRUMENT_TYPE" in upper:
            rename[upper["INSTRUMENT_TYPE"]] = "SEM_INSTRUMENT_NAME"
    out = df.rename(columns=rename)
    if "UNDERLYING_SYMBOL" not in out.columns and "SEM_TRADING_SYMBOL" in out.columns:
        out["UNDERLYING_SYMBOL"] = out["SEM_TRADING_SYMBOL"].astype(str).str.split("-").str[0]
    return out


def dataframe_from_dhan_csv(df: pd.DataFrame, derivatives_only: bool = True) -> pd.DataFrame:
    work = _normalize_columns(df)
    required = [
        "SEM_EXM_EXCH_ID", "SEM_SEGMENT", "SEM_SMST_SECURITY_ID",
        "SEM_INSTRUMENT_NAME", "SEM_TRADING_SYMBOL", "SEM_LOT_UNITS",
        "SEM_EXPIRY_DATE", "SEM_STRIKE_PRICE", "SEM_TICK_SIZE",
    ]
    if any(c not in work.columns for c in required):
        return pd.DataFrame()

    if derivatives_only:
        work = work[work["SEM_SEGMENT"].astype(str).str.upper() == "D"]
    if work.empty:
        return pd.DataFrame()

    symbols = work["SEM_TRADING_SYMBOL"].astype(str)
    if "UNDERLYING_SYMBOL" in work.columns:
        underlying = work["UNDERLYING_SYMBOL"].astype(str).str.upper()
    else:
        underlying = symbols.str.split("-").str[0].str.upper()

    desc_col = "SM_SYMBOL_NAME" if "SM_SYMBOL_NAME" in work.columns else None
    description = work[desc_col].astype(str) if desc_col else symbols

    return pd.DataFrame(
        {
            "token": work["SEM_SMST_SECURITY_ID"].astype(str),
            "symbol": symbols,
            "name": underlying,
            "description": description,
            "expiry": work["SEM_EXPIRY_DATE"].astype(str).str[:10],
            "strike": pd.to_numeric(work["SEM_STRIKE_PRICE"], errors="coerce").fillna(0),
            "lotsize": pd.to_numeric(work["SEM_LOT_UNITS"], errors="coerce").fillna(1),
            "instrumenttype": work["SEM_INSTRUMENT_NAME"].astype(str),
            "exch_seg": [
                _map_exchange(str(e), str(s))
                for e, s in zip(work["SEM_EXM_EXCH_ID"], work["SEM_SEGMENT"])
            ],
            "tick_size": pd.to_numeric(work["SEM_TICK_SIZE"], errors="coerce").fillna(0.05),
        }
    )


def resolve_master_csv() -> Optional[Path]:
    for path in (SYNCED_DETAILED, SYNCED_COMPACT, BUNDLED_CSV):
        if path.exists() and path.stat().st_size > 1000:
            return path
    return None
