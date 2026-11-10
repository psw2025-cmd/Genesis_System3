"""In-Memory High-Performance Symbol Master Cache for Genesis_System3.

Replaces flat-file CSV lookups (api-scrip-master-detailed.csv) with an in-memory
indexed SQLite database. Provides sub-millisecond symbol resolution, option chain
matrix queries, and seamless BSE/NSE multi-exchange routing.
"""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Institutional lot sizes for major Indian indices and liquid underlyings
DEFAULT_LOT_SIZES: Dict[str, int] = {
    "NIFTY": 50,
    "BANKNIFTY": 15,
    "FINNIFTY": 25,
    "MIDCPNIFTY": 50,
    "SENSEX": 10,
    "BANKEX": 15,
    "RELIANCE": 250,
    "TCS": 175,
    "INFY": 400,
    "HDFCBANK": 550,
    "ICICIBANK": 700,
    "SBIN": 750,
    "TATAMOTORS": 575,
    "BHARTIARTL": 475,
    "ITC": 1600,
    "LT": 150,
}

# Dhan Under_Security_ID mappings for Option Chain API
DHAN_INDEX_SECURITY_IDS: Dict[str, int] = {
    "NIFTY": 13,
    "BANKNIFTY": 25,
    "FINNIFTY": 27,
    "MIDCPNIFTY": 442,
    "SENSEX": 51,
    "BANKEX": 12,
}

DHAN_INDEX_SEGMENTS: Dict[str, str] = {
    "NIFTY": "IDX_I",
    "BANKNIFTY": "IDX_I",
    "FINNIFTY": "IDX_I",
    "MIDCPNIFTY": "IDX_I",
    "SENSEX": "IDX_I",
    "BANKEX": "BSE_FNO",
}


class DhanMasterCache:
    """Singleton high-speed in-memory SQLite symbol master cache."""

    _instance: Optional["DhanMasterCache"] = None

    def __new__(cls) -> "DhanMasterCache":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_db()
        return cls._instance

    def _init_db(self) -> None:
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
        self._seed_default_universe()

    def _create_tables(self) -> None:
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS instruments (
                    security_id INTEGER PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    trading_symbol TEXT NOT NULL,
                    underlying TEXT NOT NULL,
                    exchange TEXT NOT NULL,
                    segment TEXT NOT NULL,
                    instrument_type TEXT NOT NULL,
                    strike_price REAL,
                    option_type TEXT,
                    expiry_date TEXT,
                    lot_size INTEGER DEFAULT 1,
                    tick_size REAL DEFAULT 0.05,
                    is_active INTEGER DEFAULT 1,
                    updated_at TEXT
                )
            """)
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_inst_sym ON instruments(symbol);")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_inst_tsym ON instruments(trading_symbol);")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_inst_underlying ON instruments(underlying, expiry_date);")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_inst_chain ON instruments(underlying, strike_price, option_type);")

    def _seed_default_universe(self) -> None:
        """Seed index underlyings and essential metadata into memory."""
        now = datetime.now(timezone.utc).isoformat()
        records = []
        for sym, sec_id in DHAN_INDEX_SECURITY_IDS.items():
            seg = DHAN_INDEX_SEGMENTS.get(sym, "IDX_I")
            exch = "BSE" if sym in ("SENSEX", "BANKEX") else "NSE"
            records.append((
                sec_id,
                sym,
                sym,
                sym,
                exch,
                seg,
                "INDEX",
                0.0,
                None,
                None,
                DEFAULT_LOT_SIZES.get(sym, 50),
                0.05,
                1,
                now,
            ))

        with self.conn:
            self.conn.executemany("""
                INSERT OR REPLACE INTO instruments (
                    security_id, symbol, trading_symbol, underlying, exchange, segment,
                    instrument_type, strike_price, option_type, expiry_date, lot_size,
                    tick_size, is_active, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, records)

    def upsert_instrument(self, item: Dict[str, Any]) -> None:
        """Insert or update an instrument record dynamically."""
        sec_id = int(item.get("security_id") or item.get("SEM_SMST_SECURITY_ID") or 0)
        if not sec_id:
            return
        sym = str(item.get("symbol") or item.get("SEM_CUSTOM_SYMBOL") or "").upper()
        tsym = str(item.get("trading_symbol") or item.get("SEM_TRADING_SYMBOL") or sym).upper()
        underlying = str(item.get("underlying") or sym).upper()
        exch = str(item.get("exchange") or item.get("SEM_EXM_EXCH_ID") or "NSE").upper()
        seg = str(item.get("segment") or item.get("SEM_SEGMENT") or "IDX_I")
        itype = str(item.get("instrument_type") or item.get("SEM_INSTRUMENT_NAME") or "OPTIDX")
        strike = float(item.get("strike_price") or item.get("SEM_STRIKE_PRICE") or 0.0)
        opttype = item.get("option_type") or item.get("SEM_OPTION_TYPE")
        opttype = str(opttype).upper() if opttype else None
        expiry = item.get("expiry_date") or item.get("SEM_EXPIRY_DATE")
        expiry = str(expiry) if expiry else None
        lot = int(item.get("lot_size") or item.get("SEM_LOT_UNITS") or DEFAULT_LOT_SIZES.get(underlying, 1))
        tick = float(item.get("tick_size") or item.get("SEM_TICK_SIZE") or 0.05)
        now = datetime.now(timezone.utc).isoformat()

        with self.conn:
            self.conn.execute("""
                INSERT OR REPLACE INTO instruments (
                    security_id, symbol, trading_symbol, underlying, exchange, segment,
                    instrument_type, strike_price, option_type, expiry_date, lot_size,
                    tick_size, is_active, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
            """, (sec_id, sym, tsym, underlying, exch, seg, itype, strike, opttype, expiry, lot, tick, now))

    def resolve_underlying_security(self, symbol: str) -> Tuple[Optional[int], str, str]:
        """Return (security_id, exchange_segment, exchange) for any index or stock."""
        sym = symbol.strip().upper()
        cur = self.conn.cursor()
        cur.execute("SELECT security_id, segment, exchange FROM instruments WHERE underlying = ? AND instrument_type = 'INDEX' LIMIT 1", (sym,))
        row = cur.fetchone()
        if row:
            return row["security_id"], row["segment"], row["exchange"]

        # Fallback dictionary check
        if sym in DHAN_INDEX_SECURITY_IDS:
            return DHAN_INDEX_SECURITY_IDS[sym], DHAN_INDEX_SEGMENTS.get(sym, "IDX_I"), "BSE" if sym in ("SENSEX", "BANKEX") else "NSE"

        return None, "NSE_FNO", "NSE"

    def get_option_chain_contracts(self, underlying: str, expiry: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve option chain contracts for an underlying with optional expiry filter."""
        sym = underlying.strip().upper()
        cur = self.conn.cursor()
        if expiry:
            cur.execute("""
                SELECT * FROM instruments
                WHERE underlying = ? AND expiry_date = ? AND option_type IN ('CE', 'PE')
                ORDER BY strike_price ASC, option_type DESC
            """, (sym, expiry))
        else:
            cur.execute("""
                SELECT * FROM instruments
                WHERE underlying = ? AND option_type IN ('CE', 'PE')
                ORDER BY strike_price ASC, option_type DESC
            """, (sym,))
        return [dict(r) for r in cur.fetchall()]

    def count_instruments(self) -> int:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) as total FROM instruments")
        row = cur.fetchone()
        return int(row["total"]) if row else 0


def get_master_cache() -> DhanMasterCache:
    """Convenience getter for singleton in-memory master cache."""
    return DhanMasterCache()
