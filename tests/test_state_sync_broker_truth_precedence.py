import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "dashboard" / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from state_sync_service import (
    _broker_update_from_probe,
    _health_broker_update_allowed,
    _normalize_qc_truth,
)


class BrokerTruthPrecedenceTests(unittest.TestCase):
    def test_firestore_never_accepts_legacy_health_broker_authority(self):
        with patch.dict(os.environ, {"SYSTEM3_STATE_BACKEND": "firestore"}, clear=False):
            self.assertFalse(_health_broker_update_allowed({}))
            self.assertFalse(
                _health_broker_update_allowed(
                    {"broker": {"connected": True, "truth_source": "dhan_readonly_probe"}}
                )
            )

    def test_local_health_fallback_allowed_when_no_direct_probe_exists(self):
        with patch.dict(os.environ, {"SYSTEM3_STATE_BACKEND": "file"}, clear=False):
            self.assertTrue(_health_broker_update_allowed({}))

    def test_direct_probe_wins_over_health_file_even_in_local_mode(self):
        with patch.dict(os.environ, {"SYSTEM3_STATE_BACKEND": "file"}, clear=False):
            updates = {
                "broker": {
                    "connected": True,
                    "truth_source": "dhan_readonly_probe",
                }
            }
            self.assertFalse(_health_broker_update_allowed(updates))

    def test_real_906_probe_is_persisted_as_disconnected_truth(self):
        update = _broker_update_from_probe(
            {
                "connected": False,
                "error": "DHAN_REQUEST_REJECTED_906",
                "latency_ms": 81,
                "upstream_code": 906,
                "upstream_classification": "DHAN_REQUEST_REJECTED_906",
            }
        )
        self.assertIsNotNone(update)
        self.assertFalse(update["connected"])
        self.assertEqual(update["status"], "disconnected")
        self.assertEqual(update["error"], "DHAN_REQUEST_REJECTED_906")
        self.assertEqual(update["upstream_code"], 906)
        self.assertEqual(update["truth_source"], "dhan_readonly_probe")

    def test_successful_probe_stays_connected(self):
        update = _broker_update_from_probe(
            {"connected": True, "error": None, "latency_ms": 41}
        )
        self.assertTrue(update["connected"])
        self.assertIsNone(update["error"])
        self.assertEqual(update["status"], "connected")


class QcFailClosedTruthTests(unittest.TestCase):
    def test_pass_with_zero_contracts_becomes_not_ready(self):
        qc = _normalize_qc_truth(
            {"status": "PASS", "contracts_total": 0, "underlyings": 0}
        )
        self.assertEqual(qc["status"], "NOT_READY")
        self.assertIn("NO_VERIFIED_CONTRACTS", qc["reasons"])

    def test_missing_contract_evidence_is_not_ready(self):
        qc = _normalize_qc_truth({"status": "PASS"})
        self.assertEqual(qc["status"], "NOT_READY")
        self.assertEqual(qc["contracts_total"], 0)

    def test_explicit_fail_is_not_downgraded(self):
        qc = _normalize_qc_truth(
            {"status": "FAIL", "contracts_total": 0, "failures": ["bad_chain"]}
        )
        self.assertEqual(qc["status"], "FAIL")
        self.assertIn("bad_chain", qc["failures"])
        self.assertIn("NO_VERIFIED_CONTRACTS", qc["reasons"])

    def test_positive_contracts_do_not_invent_pass(self):
        qc = _normalize_qc_truth({"contracts_total": 24, "underlyings": 4})
        self.assertEqual(qc["status"], "NOT_READY")
        self.assertIn("QC_STATUS_NOT_PROVEN", qc["reasons"])


if __name__ == "__main__":
    unittest.main()
