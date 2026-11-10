"""Contracts for the canonical 22-tab production acceptance proof."""
from __future__ import annotations

import unittest

from scripts.gcp_full_dashboard_acceptance import (
    EXPECTED_TAB_IDS,
    REQUIRED_CHAINS,
    TAB_FORBIDDEN_ALWAYS,
    _parse_chain_visible,
)


class FullDashboardAcceptanceContractTests(unittest.TestCase):
    def test_exactly_22_current_canonical_tabs_are_covered(self) -> None:
        self.assertEqual(len(EXPECTED_TAB_IDS), 22)
        self.assertEqual(len(set(EXPECTED_TAB_IDS)), 22)
        self.assertEqual(set(TAB_FORBIDDEN_ALWAYS), set(EXPECTED_TAB_IDS))

    def test_required_chain_contract_is_exact(self) -> None:
        self.assertEqual(REQUIRED_CHAINS, ("NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"))

    def test_chain_parser_accepts_current_split_line_layout(self) -> None:
        text = """
        OPTION CHAIN
        SYMBOL NIFTY  SPOT 24750.15  CONTRACTS 488  STRIKES 244
        EXPIRIES 4
        source=dhan priority=dhan_worker_push status=READY fetched=2026-08-23T00:20:00Z
        """
        value = _parse_chain_visible(text, "NIFTY")
        self.assertTrue(value["symbol_visible"])
        self.assertTrue(value["source_is_dhan"])
        self.assertEqual(value["source"], "dhan")
        self.assertEqual(value["contracts"], 488)
        self.assertEqual(value["strikes"], 244)
        self.assertEqual(value["expiries"], 4)

    def test_chain_parser_does_not_accept_non_dhan_source(self) -> None:
        text = "SYMBOL NIFTY CONTRACTS 488 STRIKES 244\nsource=csv status=FALLBACK"
        value = _parse_chain_visible(text, "NIFTY")
        self.assertFalse(value["source_is_dhan"])


if __name__ == "__main__":
    unittest.main()
