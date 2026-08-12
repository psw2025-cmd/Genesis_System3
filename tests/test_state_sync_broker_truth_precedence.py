import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "dashboard" / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from state_sync_service import _health_broker_update_allowed


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


if __name__ == "__main__":
    unittest.main()
