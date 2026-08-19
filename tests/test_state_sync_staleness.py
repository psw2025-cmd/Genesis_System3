import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "dashboard" / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from runtime_state_store import RuntimeStateStore
from state_sync_service import StateSyncService


STALE_RISK = {
    "var95": 999.0,
    "es95": 888.0,
    "exposure": 777.0,
    "concentration": 0.9,
    "greeks": {"delta": 6.0, "gamma": 5.0, "theta": 4.0, "vega": 3.0},
    "limits": {"status": "FAIL", "breaches": ["STALE_BREACH"]},
}


class StateSyncStalenessTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.outputs = Path(self.tmp.name)
        self.store = RuntimeStateStore(self.outputs)
        # Keep this unit test fully offline: a connected broker snapshot prevents
        # StateSyncService's bootstrap read-only Dhan probe from being invoked.
        self.store.update_state(
            {
                "broker": {
                    "connected": True,
                    "name": "dhan",
                    "status": "connected",
                    "error": None,
                }
            }
        )

    def tearDown(self):
        self.tmp.cleanup()

    def _seed_stale_runtime_state(self):
        self.store.update_state(
            {
                "positions": [{"symbol": "STALE", "quantity": 10}],
                "pnl": {
                    "unrealized": 101.0,
                    "realized": 202.0,
                    "total": 303.0,
                    "day_total": 404.0,
                },
                "risk": STALE_RISK,
            }
        )

    async def test_missing_runtime_files_clear_stale_positions_pnl_and_risk(self):
        self._seed_stale_runtime_state()

        await StateSyncService(self.store, self.outputs).sync_state()
        state = self.store.get_state()

        self.assertEqual(state["positions"], [])
        self.assertEqual(
            state["pnl"],
            {"unrealized": 0.0, "realized": 0.0, "total": 0.0, "day_total": 0.0},
        )
        self.assertEqual(state["risk"]["var95"], 0.0)
        self.assertEqual(state["risk"]["es95"], 0.0)
        self.assertEqual(state["risk"]["exposure"], 0.0)
        self.assertEqual(state["risk"]["concentration"], 0.0)
        self.assertEqual(
            state["risk"]["greeks"],
            {"delta": 0.0, "gamma": 0.0, "theta": 0.0, "vega": 0.0},
        )
        self.assertEqual(state["risk"]["limits"], {"status": "PASS", "breaches": []})

    async def test_malformed_runtime_files_fail_closed_instead_of_preserving_history(self):
        self._seed_stale_runtime_state()
        (self.outputs / "positions_live.json").write_text("{not-json")
        (self.outputs / "paper_pnl_summary.json").write_text("{not-json")

        await StateSyncService(self.store, self.outputs).sync_state()
        state = self.store.get_state()

        self.assertEqual(state["positions"], [])
        self.assertEqual(state["pnl"]["total"], 0.0)
        self.assertEqual(state["risk"]["exposure"], 0.0)
        self.assertEqual(state["risk"]["limits"]["breaches"], [])

    async def test_fresh_position_and_pnl_files_still_populate_runtime_state(self):
        positions = [
            {
                "symbol": "NIFTY",
                "quantity": 2,
                "delta": 0.5,
                "gamma": 0.1,
                "theta": -0.2,
                "vega": 0.3,
            }
        ]
        (self.outputs / "positions_live.json").write_text(json.dumps({"positions": positions}))
        (self.outputs / "paper_pnl_summary.json").write_text(
            json.dumps(
                {
                    "total_unrealized_pnl": 12.5,
                    "total_realized_pnl": 7.5,
                    "total_pnl": 20.0,
                    "daily_pnl": 20.0,
                }
            )
        )

        await StateSyncService(self.store, self.outputs).sync_state()
        state = self.store.get_state()

        self.assertEqual(state["positions"], positions)
        self.assertEqual(
            state["pnl"],
            {"unrealized": 12.5, "realized": 7.5, "total": 20.0, "day_total": 20.0},
        )


if __name__ == "__main__":
    unittest.main()
