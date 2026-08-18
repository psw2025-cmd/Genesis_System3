import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "dashboard" / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from routers import broker


class FakeStateStore:
    def __init__(self):
        self.updates = []

    def update_state(self, updates):
        self.updates.append(updates)


class BrokerRouterStateTruthTests(unittest.TestCase):
    def tearDown(self):
        broker._state_store = None

    def test_906_is_allow_listed_as_disconnected_state(self):
        truth = broker._state_broker_truth(
            {
                "connected": False,
                "error": "DHAN_REQUEST_REJECTED_906",
                "upstream_classification": "DHAN_REQUEST_REJECTED_906",
                "upstream_code": 906,
                "latency_ms": 57,
                "token": "must-not-copy",
            }
        )
        self.assertFalse(truth["connected"])
        self.assertEqual(truth["status"], "disconnected")
        self.assertEqual(truth["error"], "DHAN_REQUEST_REJECTED_906")
        self.assertEqual(truth["upstream_code"], 906)
        self.assertNotIn("token", truth)

    def test_negative_status_is_persisted_not_ignored(self):
        store = FakeStateStore()
        broker._state_store = store
        broker._persist_broker_truth(
            {"connected": False, "error": "DHAN_REQUEST_REJECTED_906", "upstream_code": 906}
        )
        self.assertEqual(len(store.updates), 1)
        saved = store.updates[0]["broker"]
        self.assertFalse(saved["connected"])
        self.assertEqual(saved["error"], "DHAN_REQUEST_REJECTED_906")

    def test_connected_status_clears_error(self):
        truth = broker._state_broker_truth(
            {"connected": True, "error": "stale-error", "latency_ms": 20}
        )
        self.assertTrue(truth["connected"])
        self.assertIsNone(truth["error"])
        self.assertEqual(truth["status"], "connected")


if __name__ == "__main__":
    unittest.main()
