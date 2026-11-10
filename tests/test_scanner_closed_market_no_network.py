import os
import unittest
from unittest.mock import patch

from dashboard.backend import contract_gain_scanner as scanner


class ClosedMarketScannerContractTests(unittest.TestCase):
    def test_cloud_closed_market_returns_without_chain_fetch(self):
        with patch.object(scanner, "_cloud_market_closed", return_value=True), patch.object(
            scanner, "fetch_chains_for_market", side_effect=AssertionError("network fetch must not run")
        ):
            result = scanner.build_top_contract_gainers_report(
                top_n=5,
                market_top_n=25,
                include_equity=True,
            )

        self.assertEqual(result["status"], "market_closed")
        self.assertFalse(result["market_open"])
        self.assertEqual(result["ranking_mode"], "closed_market_no_network")
        self.assertEqual(result["chains_fetched"], [])
        self.assertEqual(result["segments"], scanner.INDEX_SEGMENTS)
        self.assertEqual(result["segments_implemented"], 0)
        self.assertFalse(result["live_trading_enabled"])

    def test_local_or_open_path_preserves_normal_fetch_behavior(self):
        fake_chains = {
            "NIFTY": {
                "contracts": [
                    {
                        "option_type": "CE",
                        "strike": 25000,
                        "ltp": 110.0,
                        "previous_close": 100.0,
                    }
                ]
            }
        }
        with patch.object(scanner, "_cloud_market_closed", return_value=False), patch.object(
            scanner, "fetch_chains_for_market", return_value=fake_chains
        ) as fetch:
            result = scanner.build_top_contract_gainers_report(
                top_n=5,
                market_top_n=25,
                include_equity=False,
            )

        fetch.assert_called_once()
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["contracts_scored_total"], 1)
        self.assertEqual(result["market_top_table"][0]["gain_pct"], 10.0)

    def test_cloud_detection_fails_open_to_existing_scanner_when_detector_errors(self):
        with patch.dict(os.environ, {"K_SERVICE": "genesis-system3-web"}, clear=False), patch(
            "utils.market_hours.is_market_open", side_effect=RuntimeError("detector unavailable")
        ):
            self.assertFalse(scanner._cloud_market_closed())


if __name__ == "__main__":
    unittest.main()
