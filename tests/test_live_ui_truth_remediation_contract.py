from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from scripts.gcp_live_ui_snapshot import _chain_metadata_line, _chain_source_value, _is_bad_chain_source  # noqa: E402


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
        self.assertIn("Shared local/Dhan truth renders immediately", text)
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

    def test_topbar_never_infers_broker_connected_from_unrelated_api_success(self):
        text = self.text("dashboard/frontend/src/components/TopBar.tsx")
        self.assertNotIn("apiResponded && !hasError", text)
        self.assertIn("brokerIsConnected(health, brokerConnected, brokerStatus)", text)
        self.assertIn("isNonAuthBrokerRejection", text)
        self.assertIn("Request rejected", text)
        self.assertIn("Session OK", text)

    def test_w1_connected_true_is_not_broker_reliability_pass(self):
        health = self.text("dashboard/frontend/src/lib/healthTruth.ts")
        self.assertIn("export function brokerReliabilityPass", health)
        self.assertIn("isNonAuthBrokerRejection", health)
        panel = self.text("dashboard/frontend/src/components/SystemProgressPanel.tsx")
        self.assertIn("Broker market-data reliability", panel)
        self.assertIn("connected=true must not imply", panel)
        broker = self.text("dashboard/frontend/src/components/BrokerPanel.tsx")
        self.assertIn("SESSION CONNECTED - RELIABILITY NOT PROVEN", broker)
        self.assertIn("DO NOT ROTATE TOKEN FOR 906", broker)

    def test_w4_live_gate_alert_leak_is_classified_out_of_active_stream(self):
        helper = self.text("dashboard/frontend/src/lib/alertTruth.ts")
        self.assertIn("export function isLiveReadinessInfo", helper)
        self.assertIn("OPS_LIVE_GATE", helper)
        tab = self.text("dashboard/frontend/src/components/AlertsTab.tsx")
        self.assertIn("splitAlertStream", tab)
        app = self.text("dashboard/backend/app.py")
        self.assertIn('"type": alert_type', app)
        self.assertNotIn("owner must set live_trading_approved=true in kill_switch.json", app)

    def test_frontend_market_hours_is_explicitly_timezone_safe(self):
        text = self.text("dashboard/frontend/src/utils/marketHours.ts")
        self.assertIn("Asia/Kolkata", text)
        self.assertIn("Intl.DateTimeFormat", text)
        self.assertIn("timeZone: IST_ZONE", text)
        self.assertIn("isMarketOpen(now: Date = new Date())", text)
        self.assertNotIn("getTimezoneOffset", text)

    def test_partial_health_cannot_clobber_market_open_to_false(self):
        text = self.text("dashboard/frontend/src/store.ts")
        self.assertIn("marketOpen: isMarketOpen()", text)
        self.assertIn("marketOpenFromHealth", text)
        self.assertIn("return previous", text)
        self.assertNotIn("Boolean(health?.market?.is_open ?? health?.market_status === 'open')", text)

    def test_post_deploy_semantic_proof_is_not_route_only(self):
        text = self.text("scripts/gcp_live_ui_semantic_proof.py")
        for symbol in ("NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"):
            self.assertIn(symbol, text)
        for marker in (
            "MARKET CLOSED",
            "AFTER HOURS",
            "WAITING · BROKER",
            "WAITING · 4 CHAINS",
            "WAITING FOR MARKET DATA",
            "NO CONTRACTS RETURNED BY BACKEND",
            "LOADING SIGNALS",
            "LOADING MARKET TOP",
            "TOKEN_EXPIRED_OR_INVALID",
        ):
            self.assertIn(marker, text)
        self.assertIn("/api/deploy/info", text)
        self.assertIn("/api/broker/status", text)
        self.assertIn("live-ui/semantic-proof", text)
        self.assertIn("order_placement_allowed", text)
        self.assertIn("live_trading_enabled", text)
        self.assertIn("SESSION_OPEN_ONLY_FORBIDDEN", text)
        self.assertIn("_effective_forbidden", text)

    def test_post_deploy_semantic_workflow_targets_exact_deployed_sha_read_only(self):
        text = self.text(".github/workflows/gcp-live-ui-semantic-proof.yml")
        self.assertIn('workflows: ["Cloud Run Auto Deploy"]', text)
        self.assertIn("github.event.workflow_run.head_sha", text)
        self.assertIn("Checkout exact deployed SHA", text)
        self.assertIn("persist-credentials: false", text)
        self.assertIn("contents: read", text)
        self.assertIn("statuses: write", text)
        self.assertNotIn("id-token: write", text)
        self.assertNotIn("gcloud ", text)
        self.assertIn("python scripts/gcp_live_ui_semantic_proof.py", text)

    def test_local_browser_smoke_has_bounded_chrome_cold_start_budget(self):
        text = self.text("scripts/frontend_local_runtime_smoke.py")
        self.assertIn('timeout=60', text)
        self.assertIn('outer 180s attempt budget', text)

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
        self.assertIn("source_value", text)

    def test_chain_source_parser_ignores_universe_csv_when_explicit_source_is_dhan(self):
        sample = (
            "status=market_closed_dhan_snapshot · symbol NIFTY · source_priority=dhan_live>worker_push "
            "· source=dhan · universe=security_id_list.csv · contracts=462 · strikes=231"
        )
        self.assertEqual(_chain_source_value(sample, "NIFTY"), "dhan")
        self.assertFalse(_is_bad_chain_source(_chain_source_value(sample, "NIFTY")))
        self.assertIn("universe=security_id_list.csv", _chain_metadata_line(sample, "NIFTY"))

    def test_chain_source_parser_accepts_current_two_line_production_layout(self):
        sample = "\n".join(
            [
                "SYMBOL NIFTY",
                "CONTRACTS 488",
                "STRIKES 244",
                "source=dhan priority=dhan_last_verified_snapshot status=MARKET_CLOSED_DHAN_SNAPSHOT",
                "SYMBOL BANKNIFTY",
                "source=csv status=stale",
            ]
        )
        self.assertEqual(_chain_source_value(sample, "NIFTY"), "dhan")
        self.assertIn("source=dhan", _chain_metadata_line(sample, "NIFTY"))
        self.assertEqual(_chain_source_value(sample, "BANKNIFTY"), "csv")

    def test_chain_source_parser_accepts_provenance_after_full_header_controls(self):
        sample = "\n".join(
            [
                "SYMBOL NIFTY",
                "SPOT 24,077.50",
                "PCR 1.02",
                "CONTRACTS 159",
                "STRIKES 105",
                "VISIBLE",
                "ALL STRIKES (105)",
                "+/-5 ATM",
                "+/-10 ATM",
                "+/-20 ATM",
                "+/-40 ATM",
                "2026-09-01",
                "2026-09-08",
                "2026-09-15",
                "symbol NIFTY · source=dhan_p0_live · status=MARKET_OPEN · complete_chain=true",
                "CE OI CE LTP STRIKE PE LTP PE OI",
            ]
        )
        self.assertEqual(_chain_source_value(sample, "NIFTY"), "dhan_p0_live")
        self.assertIn("complete_chain=true", _chain_metadata_line(sample, "NIFTY"))

    def test_chain_source_parser_rejects_explicit_non_dhan_sources(self):
        for source in ["csv", "synthetic", "yahoo", "mock", "fake"]:
            sample = f"status=ok · symbol NIFTY · source={source} · contracts=100 · strikes=50"
            value = _chain_source_value(sample, "NIFTY")
            self.assertEqual(value, source)
            self.assertTrue(_is_bad_chain_source(value))

    def test_live_proof_semantic_alerts_do_not_use_naive_error_substring_scan(self):
        text = self.text("scripts/gcp_live_ui_snapshot.py")
        self.assertIn("def _semantic_alerts", text)
        self.assertIn("status_start = re.match", text)
        self.assertNotIn('"ERROR",\n    "FAILED"', text)


if __name__ == "__main__":
    unittest.main()
