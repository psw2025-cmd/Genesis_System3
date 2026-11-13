# Tests for Genesis System3 Columnar Storage, In-Memory DuckDB OLAP, and Truth Lineage Pipeline.
from __future__ import annotations
import os, sys
import unittest
import pandas as pd
from datetime import datetime, timezone

ROOT_DIR = r"C:\Genesis_System3_clean"
sys.path.insert(0, ROOT_DIR)

from core.data_lake.columnar_store import columnar_store, ColumnarStore
from core.engine.option_chain_pipeline import option_chain_pipeline

class TestColumnarTruthArchitecture(unittest.TestCase):
    def setUp(self):
        self.spot = 24650.0
        data = []
        for s in range(24400, 24900, 50):
            data.append({
                "strike": float(s),
                "option_type": "CE",
                "ltp": max(1.0, self.spot - s + 40),
                "oi": 12000 + (25000 - s) * 5,
                "volume": 20000,
                "iv": 14.8,
                "delta": 0.55
            })
            data.append({
                "strike": float(s),
                "option_type": "PE",
                "ltp": max(1.0, s - self.spot + 40),
                "oi": 14000 + (s - 24000) * 5,
                "volume": 22000,
                "iv": 15.1,
                "delta": -0.45
            })
        self.sample_df = pd.DataFrame(data)

    def test_01_columnar_store_ingestion(self):
        receipt = columnar_store.ingest_chain(
            symbol="NIFTY",
            df=self.sample_df,
            spot_price=self.spot,
            source="DhanHQ Live API",
            classification="REAL_VERIFIED"
        )
        self.assertEqual(receipt["status"], "INGESTED")
        self.assertEqual(receipt["symbol"], "NIFTY")
        self.assertEqual(receipt["rows"], len(self.sample_df))
        self.assertGreater(receipt["pcr"], 0.0)
        self.assertTrue(os.path.isfile(receipt["parquet_path"]))

    def test_02_duckdb_sub_millisecond_query(self):
        res = columnar_store.query_duckdb("SELECT symbol, pcr, max_pain, total_strikes FROM chain_catalog WHERE symbol = 'NIFTY'")
        self.assertEqual(len(res), 1)
        self.assertEqual(res["symbol"].iloc[0], "NIFTY")
        self.assertGreater(float(res["pcr"].iloc[0]), 0.5)

    def test_03_proximity_filtering(self):
        prox = columnar_store.get_option_chain("NIFTY", proximity_strikes=3)
        self.assertIsNotNone(prox)
        self.assertLessEqual(len(prox["strike"].unique()), 7)

    def test_04_csv_export_only_decoupling(self):
        export_file = columnar_store.export_to_csv("NIFTY")
        self.assertTrue(os.path.isfile(export_file))
        self.assertTrue("export" in export_file.lower())

    def test_05_option_chain_pipeline_6_stages(self):
        res = option_chain_pipeline.execute_pipeline(
            symbol="NIFTY",
            raw_payload={
                "symbol": "NIFTY",
                "spot": self.spot,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "strikes": [
                    {"strike": 24600, "ce": {"ltp": 85.0, "oi": 1000, "volume": 500}, "pe": {"ltp": 35.0, "oi": 800, "volume": 400}},
                    {"strike": 24650, "ce": {"ltp": 50.0, "oi": 1200, "volume": 600}, "pe": {"ltp": 50.0, "oi": 1100, "volume": 550}},
                    {"strike": 24700, "ce": {"ltp": 30.0, "oi": 1500, "volume": 700}, "pe": {"ltp": 80.0, "oi": 900, "volume": 450}}
                ]
            },
            source="DhanHQ Live API",
            classification="REAL_VERIFIED"
        )
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["symbol"], "NIFTY")
        self.assertIn("provenance", res)
        self.assertEqual(res["provenance"]["classification"], "REAL_VERIFIED")
        self.assertIn("stages_evidence", res)
        self.assertIn("stage1_raw", res["stages_evidence"])
        self.assertIn("stage2_parsed", res["stages_evidence"])
        self.assertIn("stage3_validation", res["stages_evidence"])
        self.assertIn("stage4_storage", res["stages_evidence"])
        self.assertIn("stage5_ml", res["stages_evidence"])

if __name__ == "__main__":
    unittest.main()
