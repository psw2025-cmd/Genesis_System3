from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class LiveUiTruthRemediationContractTests(unittest.TestCase):
    def text(self, rel: str) -> str:
        return (ROOT / rel).read_text(encoding="utf-8", errors="replace")

    def test_truth_control_uses_shared_store_not_duplicate_http_probe_burst(self):
        text = self.text("dashboard/frontend/src/components/SystemTruthControl.tsx")
        self.assertIn("useStore", text)
        self.assertNotIn("axios", text)
        self.assertNotIn("Promise.all", text)
        self.assertNotIn("/api/health", text)
        self.assertIn("REQUIRED_CHAIN_SYMBOLS", text)
        for symbol in ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]:
            self.assertIn(symbol, text)
        self.assertIn("MARKET_CLOSED_DHAN_SNAPSHOT", text)
        self.assertIn("no duplicate broker/API probe burst", text)

    def test_e2e_proof_uses_shared_truth_and_accepts_verified_after_hours_dhan_snapshots(self):
        text = self.text("dashboard/frontend/src/components/EndToEndProof.tsx")
        self.assertIn("useStore", text)
        self.assertNotIn("axios", text)
        self.assertNotIn("fetch(", text)
        self.assertIn("REQUIRED_CHAIN_SYMBOLS", text)
        self.assertIn("MARKET_CLOSED_DHAN_SNAPSHOT", text)
        self.assertIn("VERIFIED_DHAN_SESSION_SNAPSHOT", text)
        self.assertIn("No duplicate 3.5-second probe storm", text)

    def test_genesis_never_replaces_workspace_with_blocking_loading_shell(self):
        text = self.text("dashboard/frontend/src/components/GenesisTab.tsx")
        self.assertIn("useStore", text)
        self.assertNotIn("if (data.loading) return", text)
        self.assertIn("BACKGROUND REFRESH", text)
        self.assertIn("Shared GCP/Dhan truth renders immediately", text)
        self.assertIn("loading: false", text)

    def test_positions_explicitly_separates_paper_and_dhan_ledgers(self):
        text = self.text("dashboard/frontend/src/components/Positions.tsx")
        self.assertIn("PAPER NET P&L", text)
        self.assertIn("DHAN LIVE POSITIONS", text)
        self.assertIn("PAPER positions ledger", text)
        self.assertIn("Open read-only Dhan broker truth", text)
        self.assertIn("setActiveTab('broker')", text)

    def test_decision_intel_does_not_claim_global_no_blockers_from_runtime_only(self):
        text = self.text("dashboard/frontend/src/components/workspaces/DecisionIntelligence.tsx")
        self.assertNotIn("✓ NO SYSTEM BLOCKERS", text)
        self.assertIn("NO RUNTIME CONNECTIVITY BLOCKERS", text)
        self.assertIn("model maturity, E2E evidence, human approval", text)

    def test_topbar_explains_missing_vix_without_fabricating_price(self):
        text = self.text("dashboard/frontend/src/components/TopBar.tsx")
        self.assertIn("vixMissingLabel", text)
        self.assertIn("Dhan no quote", text)
        self.assertIn("Dhan unavailable", text)
        self.assertIn("After-hours n/a", text)
        self.assertNotIn("INDIAVIX', spot:", text)

    def test_live_proof_uses_real_live_board_route_and_four_required_chain_subviews(self):
        text = self.text("scripts/gcp_live_ui_snapshot.py")
        self.assertIn('/api/market/live_board', text)
        self.assertNotIn('/api/market/live-board', text)
        self.assertIn('REQUIRED_CHAIN_SYMBOLS = ("NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY")', text)
        self.assertIn("_capture_required_chain_subviews", text)
        self.assertIn("all_required_chain_subviews_ready", text)
        self.assertIn("REQUIRED_CHAIN_SUBVIEW_SEMANTICS", text)
        self.assertIn("contracts_visible", text)
        self.assertIn("strikes_visible", text)
        self.assertIn("dhan_source_visible", text)
        self.assertIn("bad_source_visible", text)

    def test_live_proof_semantic_alerts_do_not_use_naive_error_substring_scan(self):
        text = self.text("scripts/gcp_live_ui_snapshot.py")
        self.assertIn("def _semantic_alerts", text)
        self.assertIn("status_start = re.match", text)
        self.assertNotIn('"ERROR",\n    "FAILED"', text)


if __name__ == "__main__":
    unittest.main()
