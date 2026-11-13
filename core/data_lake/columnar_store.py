"""Genesis System3 ? Columnar Store & In-Memory Analytical Data Lake.
Replaces brittle runtime CSV file dependencies with high-performance In-Memory
PyArrow caching, DuckDB in-memory OLAP analytics, and Parquet snapshots.

Architectural Contract:
- Hot Layer: PyArrow RecordBatch / Table in RAM.
- Query Layer: Embedded DuckDB (:memory:) with sub-millisecond analytical SQL.
- Cold Lake: Snappy-compressed Parquet snapshots (storage/parquet/).
- CSV Adapter: EXPORT ONLY for human operator downloads; NEVER used as runtime truth.
"""
from __future__ import annotations

import os
import json
import time
import hashlib
from datetime import datetime, timezone
from typing import Any, Optional, Dict, List, Tuple
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import duckdb

ROOT_DIR = r"C:\Genesis_System3_clean"
PARQUET_DIR = os.path.join(ROOT_DIR, "storage", "parquet")
EXPORT_DIR = os.path.join(ROOT_DIR, "storage", "export")

os.makedirs(PARQUET_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)


class ColumnarStore:
    _instance: Optional[ColumnarStore] = None

    def __new__(cls) -> ColumnarStore:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_store()
        return cls._instance

    def _init_store(self) -> None:
        self.db = duckdb.connect(":memory:")
        self._arrow_cache: Dict[str, pa.Table] = {}
        self._df_cache: Dict[str, pd.DataFrame] = {}
        self._provenance_cache: Dict[str, Dict[str, Any]] = {}
        self._init_schemas()

    def _init_schemas(self) -> None:
        # Create global metadata catalog table in DuckDB
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS chain_catalog (
                symbol VARCHAR,
                spot_price DOUBLE,
                total_strikes INTEGER,
                pcr DOUBLE,
                max_pain DOUBLE,
                ingested_at TIMESTAMP,
                exchange_timestamp VARCHAR,
                provenance_hash VARCHAR,
                PRIMARY KEY (symbol)
            )
        """)

    def ingest_chain(
        self,
        symbol: str,
        df: pd.DataFrame,
        spot_price: float,
        exchange_timestamp: Optional[str] = None,
        source: str = "DhanHQ Live API",
        classification: str = "REAL_VERIFIED"
    ) -> Dict[str, Any]:
        """Ingest a normalized option chain DataFrame into hot memory, DuckDB, and Parquet."""
        if df is None or df.empty:
            return {"status": "skipped", "reason": "empty_dataframe"}

        sym = symbol.upper().strip()
        now_utc = datetime.now(timezone.utc)
        now_iso = now_utc.isoformat()
        exch_ts = exchange_timestamp or now_iso

        # Cleanse and ensure uniform schema
        clean_df = df.copy()
        clean_df["symbol"] = sym
        clean_df["spot_price"] = float(spot_price)
        clean_df["ingested_at"] = now_utc

        # Generate cryptographic content hash of payload
        payload_bytes = clean_df.to_json(orient="records").encode("utf-8")
        prov_hash = hashlib.sha256(payload_bytes).hexdigest()

        # 1. Hot Layer: Convert to PyArrow Table
        arrow_table = pa.Table.from_pandas(clean_df)
        self._arrow_cache[sym] = arrow_table
        self._df_cache[sym] = clean_df

        # 2. Query Layer: Register in DuckDB
        table_name = f"options_{sym.lower()}"
        self.db.register(f"view_{table_name}", clean_df)
        self.db.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM view_{table_name}")

        # Compute key analytical derivatives in DuckDB (< 1ms)
        metrics = self._compute_duckdb_metrics(table_name, sym, spot_price)

        # Update metadata catalog
        self.db.execute("""
            INSERT OR REPLACE INTO chain_catalog 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sym,
            spot_price,
            len(clean_df),
            metrics["pcr"],
            metrics["max_pain"],
            now_utc,
            exch_ts,
            prov_hash
        ))

        # 3. Cold Parquet Snapshot
        parquet_path = self._write_parquet(sym, arrow_table, now_utc)

        receipt = {
            "symbol": sym,
            "status": "INGESTED",
            "rows": len(clean_df),
            "spot_price": spot_price,
            "pcr": metrics["pcr"],
            "max_pain": metrics["max_pain"],
            "ingested_at": now_iso,
            "exchange_timestamp": exch_ts,
            "provenance_hash": prov_hash,
            "source": source,
            "classification": classification,
            "parquet_path": parquet_path,
            "engine": "DuckDB+PyArrow"
        }
        self._provenance_cache[sym] = receipt
        return receipt

    def _compute_duckdb_metrics(self, table_name: str, symbol: str, spot: float) -> Dict[str, float]:
        """Execute sub-millisecond DuckDB SQL for PCR and Max Pain."""
        try:
            # PCR = Total Put OI / Total Call OI
            res = self.db.execute(f"""
                SELECT 
                    COALESCE(SUM(CASE WHEN option_type = 'PE' THEN oi ELSE 0 END), 0) AS put_oi,
                    COALESCE(SUM(CASE WHEN option_type = 'CE' THEN oi ELSE 0 END), 0) AS call_oi
                FROM {table_name}
            """).fetchone()
            put_oi, call_oi = res if res else (0, 0)
            pcr = round(put_oi / call_oi, 4) if call_oi > 0 else 1.0

            # Max Pain approximation via strike OI loss minimization
            strikes = self.db.execute(f"""
                SELECT DISTINCT strike FROM {table_name} WHERE strike > 0 ORDER BY strike
            """).fetchall()
            max_pain = spot
            min_loss = float("inf")
            for (stk,) in strikes[:30]:
                loss = self.db.execute(f"""
                    SELECT SUM(
                        CASE 
                            WHEN option_type = 'CE' AND strike < {stk} THEN ({stk} - strike) * oi
                            WHEN option_type = 'PE' AND strike > {stk} THEN (strike - {stk}) * oi
                            ELSE 0 
                        END
                    ) FROM {table_name}
                """).fetchone()[0] or 0.0
                if loss < min_loss and loss > 0:
                    min_loss = loss
                    max_pain = float(stk)

            return {"pcr": pcr, "max_pain": max_pain}
        except Exception:
            return {"pcr": 1.0, "max_pain": spot}

    def _write_parquet(self, symbol: str, table: pa.Table, dt: datetime) -> str:
        """Persist columnar snapshot to Parquet lake with Snappy compression."""
        sym_dir = os.path.join(PARQUET_DIR, symbol.upper())
        os.makedirs(sym_dir, exist_ok=True)
        filename = f"{symbol.upper()}_{dt.strftime('%Y-%m-%d_%H%M%S')}.parquet"
        latest_file = f"{symbol.upper()}_latest.parquet"
        
        path_timed = os.path.join(sym_dir, filename)
        path_latest = os.path.join(sym_dir, latest_file)
        
        pq.write_table(table, path_timed, compression="snappy")
        pq.write_table(table, path_latest, compression="snappy")
        return path_latest

    def get_option_chain(
        self,
        symbol: str,
        proximity_strikes: int = 10
    ) -> Optional[pd.DataFrame]:
        """Retrieve option chain via hot cache or DuckDB with proximity filtering."""
        sym = symbol.upper().strip()
        table_name = f"options_{sym.lower()}"

        # 1. Hot Memory Check
        if sym in self._df_cache:
            df = self._df_cache[sym]
            if proximity_strikes > 0 and "strike" in df.columns and "spot_price" in df.columns:
                spot = df["spot_price"].iloc[0]
                strikes = sorted(df["strike"].unique())
                atm_idx = min(range(len(strikes)), key=lambda i: abs(strikes[i] - spot))
                start_i = max(0, atm_idx - proximity_strikes)
                end_i = min(len(strikes), atm_idx + proximity_strikes + 1)
                selected_strikes = set(strikes[start_i:end_i])
                return df[df["strike"].isin(selected_strikes)].copy()
            return df.copy()

        # 2. Cold Parquet Fallback
        latest_parquet = os.path.join(PARQUET_DIR, sym, f"{sym}_latest.parquet")
        if os.path.isfile(latest_parquet):
            table = pq.read_table(latest_parquet)
            df = table.to_pandas()
            self._arrow_cache[sym] = table
            self._df_cache[sym] = df
            self.db.register(f"view_{table_name}", df)
            self.db.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM view_{table_name}")
            return df

        return None

    def query_duckdb(self, query: str) -> pd.DataFrame:
        """Execute arbitrary analytical SQL on in-memory option chains."""
        return self.db.execute(query).df()

    def get_provenance(self, symbol: str) -> Dict[str, Any]:
        """Return cryptographically bound evidence receipt for symbol."""
        sym = symbol.upper().strip()
        return self._provenance_cache.get(sym, {
            "symbol": sym,
            "status": "NOT_LOADED",
            "source": "None",
            "classification": "UNKNOWN"
        })

    def export_to_csv(self, symbol: str) -> str:
        """EXPORT ONLY: Generate CSV for human operator download. Detached from runtime truth."""
        df = self.get_option_chain(symbol, proximity_strikes=0)
        if df is None or df.empty:
            raise ValueError(f"No option chain data available for {symbol} to export.")
        sym = symbol.upper().strip()
        export_path = os.path.join(EXPORT_DIR, f"{sym}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        df.to_csv(export_path, index=False)
        return export_path


columnar_store = ColumnarStore()
