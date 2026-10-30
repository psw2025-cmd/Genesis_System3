"""Contract: after-hours MARKET CLOSED must not false-fail live UI semantic proof."""
from __future__ import annotations

import unittest

from scripts.gcp_live_ui_semantic_proof import (
    KEY_TAB_FORBIDDEN,
    SESSION_OPEN_ONLY_FORBIDDEN,
    _effective_forbidden,
    _expected_market_open,
)


class LiveUiSemanticAfterHoursContractTests(unittest.TestCase):
    def test_session_only_markers_are_gated(self) -> None:
        forbidden = KEY_TAB_FORBIDDEN["decision-intel"]
        when_open = _effective_forbidden(forbidden, expect_open=True)
        when_closed = _effective_forbidden(forbidden, expect_open=False)
        self.assertIn("MARKET CLOSED", when_open)
        self.assertIn("AFTER HOURS", when_open)
        self.assertNotIn("MARKET CLOSED", when_closed)
        self.assertNotIn("AFTER HOURS", when_closed)
        self.assertIn("DISCONNECTED / NO AUTH", when_closed)

    def test_session_only_set_matches_known_false_positive_markers(self) -> None:
        self.assertEqual(SESSION_OPEN_ONLY_FORBIDDEN, frozenset({"MARKET CLOSED", "AFTER HOURS"}))

    def test_expected_market_open_helper_exists(self) -> None:
        # Smoke: callable and returns bool for "now".
        self.assertIsInstance(_expected_market_open(), bool)


if __name__ == "__main__":
    unittest.main()
