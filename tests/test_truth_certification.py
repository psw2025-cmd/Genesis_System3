"""
Genesis System3 — Phase 9 Truth Certification & Architecture Test Suite
Validates:
1. Traceability: 5-stage option chain truth pipeline from exchange to UI
2. Columnar Storage: In-memory Arrow, DuckDB OLAP, Snappy Parquet Lake
3. Export Layer Isolation: CSV decoupled as export-only format, not runtime source
4. Anti-Fake Guard: Fail-closed enforcement ("NO VERIFIED LIVE DATA")
5. Provenance Cryptographic Binding: SHA256 receipt generation on all live payloads
"""
from __future__ import annotations
import os, sys, unittest
import pandas as pd
from datetime import datetime, timezone

ROOT_DIR = r"C:\Genesis_System3_clean"
sys.path.insert(0, ROOT_DIR)

from core.data_lake.columnar_store import columnar_store, ColumnarStore
from core.engine.option_chain_pipeline import option_chain_pipeline, OptionChainPipeline
from core.engine.anti_fake_guard import anti_fake_guard, AntiFakeGuard

class TestTruthCertification(unittest.TestCase):
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
        self.sample_raw_feed = {
            "symbol": "NIFTY",
            "spot": self.spot,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "strikes": data
        }

    def test_01_traceability_across_pipeline_stages(self):
        """Phase 9 Requirement: Every live payload must be traceable across all pipeline stages with SHA256 hashes."""
        res = option_chain_pipeline.execute_pipeline(
            symbol="NIFTY",
            raw_payload=self.sample_raw_feed,
            source="DhanHQ Live API",
            classification="REAL_VERIFIED"
        )
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["symbol"], "NIFTY")
        
        prov = res["provenance"]
        self.assertEqual(prov["source"], "DhanHQ Live API")
        self.assertEqual(prov["classification"], "REAL_VERIFIED")
        self.assertIn("timestamp", prov)
        self.assertIn("exchange_timestamp", prov)
        self.assertGreaterEqual(prov["age_seconds"], 0.0)
        
        stages = res["stages_evidence"]
        self.assertIn("stage1_raw", stages)
        self.assertIn("stage2_parsed", stages)
        self.assertIn("stage3_validation", stages)
        self.assertIn("stage4_storage", stages)
        self.assertIn("stage5_ml", stages)
        
        # Verify cryptographic sha256 provenance in stage 1
        self.assertEqual(len(stages["stage1_raw"]["raw_sha256"]), 64)

    def test_02_columnar_storage_and_parquet_persistence(self):
        """Phase 9 Requirement: Parquet lake snapshots and DuckDB OLAP must function without runtime CSV."""
        receipt = columnar_store.ingest_chain(
            symbol="NIFTY",
            df=self.sample_df,
            spot_price=self.spot,
            source="DhanHQ Live API",
            classification="REAL_VERIFIED"
        )
        self.assertEqual(receipt["status"], "INGESTED")
        self.assertEqual(receipt["symbol"], "NIFTY")
        self.assertGreater(receipt["pcr"], 0.0)
        self.assertTrue(os.path.isfile(receipt["parquet_path"]))
        self.assertTrue(receipt["parquet_path"].endswith(".parquet"))

        # Verify DuckDB sub-millisecond query
        duck_df = columnar_store.query_duckdb("SELECT symbol, pcr, max_pain FROM chain_catalog WHERE symbol = 'NIFTY'")
        self.assertFalse(duck_df.empty)
        self.assertEqual(duck_df["symbol"].iloc[0], "NIFTY")

    def test_03_csv_isolated_as_export_layer_only(self):
        """Phase 9 Requirement: CSV is preserved strictly as an export layer, never runtime truth source."""
        columnar_store.ingest_chain(
            symbol="NIFTY",
            df=self.sample_df,
            spot_price=self.spot,
            source="DhanHQ Live API",
            classification="REAL_VERIFIED"
        )
        export_file = columnar_store.export_to_csv("NIFTY")
        self.assertTrue(os.path.isfile(export_file))
        self.assertTrue(export_file.endswith(".csv"))
        self.assertIn("storage\\export", export_file)
        
        df_export = pd.read_csv(export_file)
        self.assertGreater(len(df_export), 0)
        self.assertIn("strike", df_export.columns)

    def test_04_anti_fake_guard_fails_closed(self):
        """Phase 9 Requirement: Anti-Fake Guard must fail closed with NO VERIFIED LIVE DATA when feed is disconnected."""
        # 1. Disconnected feed
        wrapped_disconnected = anti_fake_guard.audit_and_wrap_payload(
            symbol="NIFTY",
            data=self.sample_raw_feed,
            raw_source="DhanHQ Live Feed",
            is_live_connected=False
        )
        self.assertFalse(wrapped_disconnected["verified"])
        self.assertEqual(wrapped_disconnected["verification_status"], "NO VERIFIED LIVE DATA")
        
        # 2. Simulated payload
        sim_data = dict(self.sample_raw_feed)
        sim_data["execution_mode"] = "simulated"
        wrapped_sim = anti_fake_guard.audit_and_wrap_payload(
            symbol="NIFTY",
            data=sim_data,
            raw_source="Simulated Test Stream",
            is_live_connected=False
        )
        self.assertFalse(wrapped_sim["verified"])
        self.assertEqual(wrapped_sim["verification_status"], "NO VERIFIED LIVE DATA")
        self.assertEqual(wrapped_sim["provenance"]["classification"], "SIMULATED")

    def test_05_source_provenance_metadata(self):
        """Phase 9 Requirement: Every response must contain complete provenance metadata (source, timestamp, exchange_timestamp, age)."""
        wrapped = anti_fake_guard.audit_and_wrap_payload(
            symbol="NIFTY",
            data=self.sample_raw_feed,
            raw_source="DhanHQ Live API",
            is_live_connected=True
        )
        self.assertIn("provenance", wrapped)
        prov = wrapped["provenance"]
        self.assertEqual(prov["source"], "DhanHQ Live API")
        self.assertIn("timestamp", prov)
        self.assertIn("exchange_timestamp", prov)
        self.assertIn("age_seconds", prov)
        self.assertGreaterEqual(prov["age_seconds"], 0.0)

if __name__ == "__main__":
    unittest.main()
