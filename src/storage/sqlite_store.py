"""
SQLite Storage for Option Chain Snapshots
"""
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime
import pytz
import time
from typing import Optional, List, Dict
import json
import sys

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.utils.logger import logger


class OptionChainStore:
    """
    SQLite storage for option chain snapshots.
    """
    
    def __init__(self, db_path: Optional[Path] = None, retention_days: int = 2):
        """
        Initialize storage.
        
        Args:
            db_path: Path to SQLite database (default: storage/live/option_chain.db)
            retention_days: Days of data to retain (default: 2)
        """
        if db_path is None:
            db_path = ROOT_DIR / "storage" / "live" / "option_chain.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.retention_days = retention_days
        
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Snapshots table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS snapshots (
                snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp_ist TEXT NOT NULL,
                timestamp_epoch REAL NOT NULL,
                underlying TEXT,
                exchange TEXT,
                total_options INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Contracts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contracts (
                contract_id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id INTEGER,
                timestamp_ist TEXT NOT NULL,
                timestamp_epoch REAL NOT NULL,
                underlying TEXT,
                exchange TEXT,
                token TEXT,
                symbol TEXT,
                strike REAL,
                option_type TEXT,
                expiry TEXT,
                ltp REAL,
                oi REAL,
                volume REAL,
                bid_price REAL,
                ask_price REAL,
                mid_price REAL,
                spread REAL,
                delta REAL,
                gamma REAL,
                theta REAL,
                vega REAL,
                iv REAL,
                intrinsic_value REAL,
                extrinsic_value REAL,
                dOI REAL,
                dVolume REAL,
                dMid REAL,
                oi_buildup TEXT,
                FOREIGN KEY (snapshot_id) REFERENCES snapshots(snapshot_id)
            )
        """)
        
        # Underlying summary table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS underlying_summary (
                summary_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp_ist TEXT NOT NULL,
                timestamp_epoch REAL NOT NULL,
                underlying TEXT,
                exchange TEXT,
                spot_price REAL,
                pcr REAL,
                pcr_delta_weighted REAL,
                total_oi REAL,
                total_volume REAL,
                liquidity_score REAL,
                signal_strength REAL,
                underlying_score REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Trade signals table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trade_signals (
                signal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp_ist TEXT NOT NULL,
                timestamp_epoch REAL NOT NULL,
                underlying TEXT,
                strategy TEXT,
                action TEXT,
                token TEXT,
                symbol TEXT,
                strike REAL,
                option_type TEXT,
                entry_mid REAL,
                stop_loss REAL,
                target REAL,
                qty_lots INTEGER,
                confidence REAL,
                reason TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_timestamp ON snapshots(timestamp_epoch)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_contracts_snapshot ON contracts(snapshot_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_contracts_token ON contracts(token)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_summary_underlying ON underlying_summary(underlying, timestamp_epoch)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_timestamp ON trade_signals(timestamp_epoch)")
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized: {self.db_path}")
    
    def save_snapshot(self, df: pd.DataFrame, underlying: str, exchange: str) -> int:
        """
        Save a snapshot to database.
        
        Args:
            df: DataFrame with option chain data
            underlying: Underlying name
            exchange: Exchange code
        
        Returns:
            snapshot_id
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        timestamp_ist = now.strftime('%Y-%m-%d %H:%M:%S IST')
        timestamp_epoch = now.timestamp()
        
        # Insert snapshot
        cursor.execute("""
            INSERT INTO snapshots (timestamp_ist, timestamp_epoch, underlying, exchange, total_options)
            VALUES (?, ?, ?, ?, ?)
        """, (timestamp_ist, timestamp_epoch, underlying, exchange, len(df)))
        
        snapshot_id = cursor.lastrowid
        
        # Insert contracts
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO contracts (
                    snapshot_id, timestamp_ist, timestamp_epoch, underlying, exchange,
                    token, symbol, strike, option_type, expiry,
                    ltp, oi, volume, bid_price, ask_price, mid_price, spread,
                    delta, gamma, theta, vega, iv,
                    intrinsic_value, extrinsic_value,
                    dOI, dVolume, dMid, oi_buildup
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                snapshot_id, timestamp_ist, timestamp_epoch,
                row.get('underlying'), row.get('exchange'),
                str(row.get('token', '')), str(row.get('symbol', '')),
                row.get('strike'), row.get('option_type'), str(row.get('expiry', '')),
                row.get('ltp'), row.get('oi'), row.get('volume'),
                row.get('bidPrice'), row.get('offerPrice'), row.get('mid_price'),
                row.get('bid_ask_spread'),
                row.get('delta'), row.get('gamma'), row.get('theta'), row.get('vega'), row.get('iv'),
                row.get('intrinsic_value'), row.get('extrinsic_value'),
                row.get('dOI'), row.get('dVolume'), row.get('dMid'),
                str(row.get('oi_buildup', ''))
            ))
        
        conn.commit()
        conn.close()
        
        logger.debug(f"Saved snapshot {snapshot_id} for {underlying}: {len(df)} contracts")
        return snapshot_id
    
    def get_latest_snapshot(self, underlying: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Get latest snapshot.
        
        Args:
            underlying: Optional underlying filter
        
        Returns:
            DataFrame or None
        """
        conn = sqlite3.connect(str(self.db_path))
        
        query = """
            SELECT c.* FROM contracts c
            JOIN snapshots s ON c.snapshot_id = s.snapshot_id
        """
        params = []
        
        if underlying:
            query += " WHERE c.underlying = ?"
            params.append(underlying)
        
        query += " ORDER BY c.timestamp_epoch DESC LIMIT 1000"
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        return df if not df.empty else None
    
    def cleanup_old_data(self):
        """Remove data older than retention_days."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cutoff_epoch = time.time() - (self.retention_days * 24 * 3600)
        
        # Delete old contracts
        cursor.execute("""
            DELETE FROM contracts
            WHERE timestamp_epoch < ?
        """, (cutoff_epoch,))
        
        # Delete old snapshots
        cursor.execute("""
            DELETE FROM snapshots
            WHERE timestamp_epoch < ?
        """, (cutoff_epoch,))
        
        # Delete old summaries
        cursor.execute("""
            DELETE FROM underlying_summary
            WHERE timestamp_epoch < ?
        """, (cutoff_epoch,))
        
        # Delete old signals
        cursor.execute("""
            DELETE FROM trade_signals
            WHERE timestamp_epoch < ?
        """, (cutoff_epoch,))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        if deleted > 0:
            logger.info(f"Cleaned up {deleted} old records")
