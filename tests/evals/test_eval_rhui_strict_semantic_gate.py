"""Regression contracts for strict RHUI semantic false-green prevention."""
from __future__ import annotations

import unittest
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.gcp_rhui_strict_semantic_gate import _api_failures, _text_failures


class RhuiStrictSemanticGateTests(unittest.TestCase):
    def _healthy_snapshot(self) -> dict:
        return {
            "deploy_sha": "abc1234",
            "revision": "genesis-system3-web-test",
            "broker_connected": True,
            "broker_error": None,
            "live_trading_enabled": False,
            "order_placement_allowed": False,
            "chains": {
                symbol: {
                    "contracts": 10,
                    "source_is_dhan": True,
                    "stale": False,
                    "spot": 100.0,
                }
                for symbol in ("NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY")
            },
        }

    def test_after_hours_broker_disconnected_is_still_failure(self) -> None:
        snapshot = self._healthy_snapshot()
        snapshot["broker_connected"] = False
        self.assertIn("broker_not_connected", _api_failures(snapshot))

    def test_after_hours_stale_chain_is_still_failure(self) -> None:
        snapshot = self._healthy_snapshot()
        snapshot["chains"]["NIFTY"]["stale"] = True
        self.assertIn("NIFTY_stale", _api_failures(snapshot))

    def test_connected_api_plus_dhan_waiting_ui_is_failure(self) -> None:
        failures = _text_failures(
            "overview",
            "Market closed\nDhan · Waiting\nSaturday snapshot",
            broker_connected=True,
        )
        self.assertTrue(any("DHAN · WAITING" in item for item in failures))

    def test_market_closed_alone_is_allowed_after_hours(self) -> None:
        failures = _text_failures(
            "overview",
            "Market closed\nDhan connected\nSnapshot ready",
            broker_connected=True,
        )
        self.assertEqual([], failures)

    def test_current_prediction_loading_marker_is_failure(self) -> None:
        failures = _text_failures(
            "prediction-audit",
            "LOADING VALIDATION\nWaiting for /api/accuracy_trend",
            broker_connected=True,
        )
        self.assertTrue(any("LOADING VALIDATION" in item for item in failures))
        self.assertTrue(any("/API/ACCURACY_TREND" in item for item in failures))

    def test_current_performance_loading_marker_is_failure(self) -> None:
        failures = _text_failures(
            "performance",
            "API status: /api/pnl loading · checked -- IST",
            broker_connected=True,
        )
        self.assertTrue(any("/API/PNL LOADING" in item for item in failures))


if __name__ == "__main__":
    unittest.main()
