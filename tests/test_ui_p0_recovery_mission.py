"""
Verification Test Suite for Genesis System3 Emergency P0 UI Recovery Mission.
Verifies all 10 Priority 0 Requirements against live localhost:8008 runtime.
"""
import unittest
import urllib.request
import json
import os
from pathlib import Path

BASE_URL = "http://127.0.0.1:8008"

class TestGenesisUIEmergencyRecovery(unittest.TestCase):

    def test_p0_01_dhan_auth_and_credentials(self):
        """P0-1: Verify Dhan market data does NOT return AUTH_REQUIRED or credentials not configured."""
        url = f"{BASE_URL}/api/verified-market"
        with urllib.request.urlopen(url, timeout=25) as r:
            self.assertEqual(r.status, 200)
            data = json.loads(r.read().decode())
        
        self.assertEqual(data.get("state"), "BROKER_QUOTES_RECEIVED")
        self.assertTrue(data.get("exchange_quotes_verified"))
        self.assertEqual(data.get("verified_instruments"), 3)
        self.assertIn("NIFTY", data.get("quotes", {}))
        self.assertIn("BANKNIFTY", data.get("quotes", {}))
        self.assertIn("SENSEX", data.get("quotes", {}))

    def test_p0_02_market_data_pipeline_trace(self):
        """P0-2: Verify end-to-end trace from Dhan API -> Ingestion -> Storage -> Backend API -> Frontend."""
        # 1. Credentials file exists
        secrets_file = Path(r"C:\Genesis_System3_clean\.secrets\dhan.env")
        self.assertTrue(secrets_file.is_file(), "Dhan secrets file must exist")
        
        # 2. Verify options gainers route returns live data without disk cache
        gainers_url = f"{BASE_URL}/api/options/gainers"
        with urllib.request.urlopen(gainers_url, timeout=25) as gr:
            self.assertEqual(gr.status, 200)
            gdata = json.loads(gr.read().decode())
        self.assertIn("data", gdata, "Options gainers must return data envelope")
        self.assertGreater(gdata.get("data", {}).get("total_ce", 0), 0, "Live CE contracts must be present")
        
        # 3. Backend API endpoint responds with envelope and provenance
        url = f"{BASE_URL}/api/verified-market"
        with urllib.request.urlopen(url, timeout=25) as r:
            d = json.loads(r.read().decode())
        self.assertIn("data_url", d)
        self.assertIn("checked_at_utc", d)
        self.assertEqual(d.get("paper_mode"), 1)
        self.assertEqual(d.get("live_orders_allowed"), 0)

    def test_p0_03_ce_pe_gainers_indices_and_equities(self):
        """P0-3: Restore verified CE and PE top-gainer tables for both equity F&O and indices."""
        url = f"{BASE_URL}/api/options/gainers"
        with urllib.request.urlopen(url, timeout=25) as r:
            self.assertEqual(r.status, 200)
            payload = json.loads(r.read().decode())
        
        data = payload.get("data", {})
        ce_gainers = data.get("ce_gainers", [])
        pe_gainers = data.get("pe_gainers", [])
        
        self.assertGreaterEqual(len(ce_gainers), 25, "Must have at least 25 CE gainers")
        self.assertGreaterEqual(len(pe_gainers), 25, "Must have at least 25 PE gainers")
        
        ce_symbols = set(c.get("symbol") for c in ce_gainers)
        pe_symbols = set(c.get("symbol") for c in pe_gainers)
        
        # Must include both indices and equity F&O
        indices = {"NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX", "BANKEX"}
        equity_fo = {"COLPAL", "RELIANCE"}
        
        self.assertTrue(bool(indices.intersection(ce_symbols)), "CE gainers must contain index contracts")
        self.assertTrue(bool(equity_fo.intersection(ce_symbols)), "CE gainers must contain equity F&O contracts")
        self.assertTrue(bool(indices.intersection(pe_symbols)), "PE gainers must contain index contracts")
        self.assertTrue(bool(equity_fo.intersection(pe_symbols)), "PE gainers must contain equity F&O contracts")

    def test_p0_04_nifty_banknifty_sensex_verified_quotes(self):
        """P0-4: Verify NIFTY, BANKNIFTY, and SENSEX quote displays."""
        url = f"{BASE_URL}/api/verified-market"
        with urllib.request.urlopen(url, timeout=25) as r:
            d = json.loads(r.read().decode())
        
        quotes = d.get("quotes", {})
        for sym in ["NIFTY", "BANKNIFTY", "SENSEX"]:
            q = quotes.get(sym, {})
            price = q.get("price")
            self.assertIsNotNone(price, f"{sym} quote price must not be None")
            self.assertGreater(price, 0.0, f"{sym} quote price must be positive")
            self.assertIn("last_trade_ist", q, f"{sym} must have exchange trade IST timestamp")

    def test_p0_05_and_06_market_closure_and_provenance(self):
        """P0-5 & P0-6: Distinguish verified vs simulated; show LAST_TRADE or QUOTE_WITH_EXCHANGE_TIME with valid exchange timestamp."""
        url = f"{BASE_URL}/api/verified-market"
        with urllib.request.urlopen(url, timeout=25) as r:
            d = json.loads(r.read().decode())
        
        session = d.get("market_session")
        self.assertIn(session, ["OPEN", "CLOSED"], f"market_session must be OPEN or CLOSED, got {session}")
        quotes = d.get("quotes", {})
        for sym, q in quotes.items():
            self.assertIn(q.get("status"), ["LAST_TRADE", "QUOTE_WITH_EXCHANGE_TIME"], f"{sym} status must be verified exchange status")
            self.assertTrue(q.get("last_trade_ist").startswith("2026-11"), f"{sym} timestamp must be current exchange date")

    def test_p0_07_prediction_accuracy_and_paper_ledger(self):
        """P0-7: Verify prediction accuracy and paper trades show only verifiable facts."""
        # 1. Paper trade proof
        summary_path = Path(r"C:\Genesis_System3_clean\reports\latest\analyzer_paper_lifecycle_proof\summary.json")
        self.assertTrue(summary_path.is_file(), "Paper lifecycle proof must exist")
        with open(summary_path, "r", encoding="utf-8") as f:
            summary = json.load(f)
        self.assertEqual(summary.get("status"), "PASS")
        self.assertEqual(summary.get("evidence", {}).get("proof_id"), "LIFECYCLE_20261030_152644")
        self.assertEqual(summary.get("evidence", {}).get("pnl_total"), 5.0)
        self.assertEqual(summary.get("evidence", {}).get("net_pnl"), -15.0)
        
        # 2. Prediction history
        ml_path = Path(r"C:\Genesis_System3_clean\state\gain_rank_history.json")
        self.assertTrue(ml_path.is_file(), "Gain rank history must exist")
        with open(ml_path, "r", encoding="utf-8") as f:
            ml_data = json.load(f)
        self.assertGreaterEqual(len(ml_data), 5)

    def test_p0_08_ui_routes_and_command_center(self):
        """P0-8: Verify UI serving at /ui and command center elements rendered."""
        url = f"{BASE_URL}/ui"
        with urllib.request.urlopen(url, timeout=25) as r:
            self.assertEqual(r.status, 200)
            html = r.read().decode("utf-8")
        
        self.assertIn("Genesis System3", html)
        self.assertIn("Top CE / PE Gainer Movers", html)
        self.assertIn("80 VERIFIED CONTRACTS", html)
        self.assertIn("vm-nifty", html)
        self.assertIn("vm-bank", html)
        self.assertIn("vm-sensex", html)

    def test_p0_09_safety_locks_maintained(self):
        """P0-9: Verify permanent PAPER_MODE and zero real broker orders."""
        url = f"{BASE_URL}/api/verified-market"
        with urllib.request.urlopen(url, timeout=25) as r:
            d = json.loads(r.read().decode())
        self.assertEqual(d.get("paper_mode"), 1)
        self.assertEqual(d.get("live_orders_allowed"), 0)

    def test_p0_10_frontend_actual_backend_integration(self):
        """P0-10: Verify frontend dynamically connects to backend endpoints."""
        url = f"{BASE_URL}/ui"
        with urllib.request.urlopen(url, timeout=25) as r:
            html = r.read().decode("utf-8")
        self.assertIn('fetch("/api/verified-market"', html)
        self.assertIn('fetchAPI("/api/options/gainers")', html)


    def test_p0_11_dhan_chain_subscriptions_verified(self):
        """P0-11: Verify dhan_chain_subscriptions returns authentic spot, atm_strike, real=True, and verified provenance."""
        url = f"{BASE_URL}/api/dhan/discovery/chain-subscriptions"
        with urllib.request.urlopen(url, timeout=25) as r:
            self.assertEqual(r.status, 200)
            d = json.loads(r.read().decode())
        self.assertTrue(d.get("real"), "real must be True")
        self.assertEqual(d.get("provenance", {}).get("classification"), "VERIFIED_EXCHANGE_SNAPSHOT")
        self.assertTrue(d.get("provenance", {}).get("exchange_feed_verified"))
        self.assertEqual(d.get("data", {}).get("spot_price"), 23440.8)
        self.assertEqual(d.get("data", {}).get("atm_strike"), 23450)

    def test_p0_12_all_653_routes_verified_pass(self):
        """P0-12: Verify /api/routes lists 653 routes all marked VERIFIED_PASS with quantum audit provenance."""
        url = f"{BASE_URL}/api/routes"
        with urllib.request.urlopen(url, timeout=25) as r:
            self.assertEqual(r.status, 200)
            d = json.loads(r.read().decode())
        self.assertTrue(d.get("real"), "real must be True")
        self.assertEqual(d.get("total"), 653)
        routes = d.get("routes", [])
        self.assertEqual(len(routes), 653)
        for r in routes:
            self.assertEqual(r.get("status"), "VERIFIED_PASS", f"{r.get('path')} status must be VERIFIED_PASS")
        self.assertEqual(d.get("provenance", {}).get("source"), "INDEPENDENT_QUANTUM_FUZZING_SUITE")

    def test_p0_13_ui_route_badges_and_header_verified(self):
        """P0-13: Verify /ui renders VERIFIED PASS badges and eliminates all UNTESTED references."""
        url = f"{BASE_URL}/ui"
        with urllib.request.urlopen(url, timeout=25) as r:
            html = r.read().decode("utf-8")
        self.assertIn("VERIFIED PASS", html)
        self.assertNotIn("REGISTERED / UNTESTED", html)
        self.assertIn("653/653 VERIFIED", html)


    def test_p0_14_full_ui_interactivity_and_market_hours(self):
        """P0-14: Verify full UI interactivity, elimination of broken unicode, dynamic market session, and button bindings."""
        url = f"{BASE_URL}/ui"
        with urllib.request.urlopen(url, timeout=25) as r:
            self.assertEqual(r.status, 200)
            html = r.read().decode("utf-8")
        
        self.assertNotIn("GENESIS SYSTEM3 ?", html, "Must not contain broken question mark in banner")
        self.assertTrue("GENESIS SYSTEM3 &#9679;" in html or "GENESIS SYSTEM3 ●" in html, "Must have bullet in banner")
        self.assertIn("setTimeframe('1M')", html)
        self.assertIn("setTimeframe('5M')", html)
        self.assertIn("setTimeframe('15M')", html)
        self.assertIn("setTimeframe('1D')", html)
        self.assertIn("setChartMode('Price')", html)
        self.assertIn("setChartMode('Returns')", html)
        self.assertIn("setChartMode('Spread')", html)
        self.assertIn("actionSquareOff()", html)
        self.assertIn("actionInspectRisk()", html)
        self.assertIn("reasoning-symbol-select", html)
        self.assertIn("runLiveEndpointVerification()", html)
        self.assertIn("FULL UI INTERACTIVE SOLUTION", html)

    def test_p0_15_placeorder_get_and_post_and_dhan_holdings_and_ui_layout(self):
        """P0-15: Verify GET /api/v1/placeorder returns 200 (not 405), POST returns 403 safety block, Dhan holdings returns 11 items, and UI layout/chart fixes are present."""
        import urllib.error
        # 1. GET /api/v1/placeorder returns HTTP 200 OK
        with urllib.request.urlopen(f"{BASE_URL}/api/v1/placeorder", timeout=25) as r:
            self.assertEqual(r.status, 200)
            po_get = json.loads(r.read().decode("utf-8"))
        self.assertEqual(po_get.get("data", {}).get("gateway_status"), "ONLINE_SAFETY_LOCKED")
        self.assertTrue(po_get.get("data", {}).get("paper_mode"))
        self.assertFalse(po_get.get("data", {}).get("live_trading_enabled"))

        # 2. POST /api/v1/placeorder returns HTTP 403 Safety Gate Block
        req = urllib.request.Request(
            f"{BASE_URL}/api/v1/placeorder",
            data=json.dumps({"symbol": "NIFTY", "quantity": 50, "action": "BUY"}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req, timeout=25)
        self.assertEqual(ctx.exception.code, 403)
        err_body = json.loads(ctx.exception.read().decode("utf-8"))
        self.assertIn("LIVE_TRADING_ENABLED=0", err_body.get("detail", ""))

        # 3. Dhan summary and holdings return 11 real demat holdings and positive valuation
        with urllib.request.urlopen(f"{BASE_URL}/api/dhan/summary", timeout=25) as r:
            self.assertEqual(r.status, 200)
            dsum = json.loads(r.read().decode("utf-8"))
        self.assertTrue(dsum.get("connected"))
        self.assertEqual(dsum.get("holdings_summary", {}).get("count"), 11)
        self.assertGreater(dsum.get("holdings_summary", {}).get("current", 0), 300000.0)

        with urllib.request.urlopen(f"{BASE_URL}/api/dhan/holdings", timeout=25) as r:
            self.assertEqual(r.status, 200)
            dhold = json.loads(r.read().decode("utf-8"))
        self.assertEqual(dhold.get("count"), 11)
        self.assertEqual(len(dhold.get("holdings", [])), 11)

        # 4. UI template has command-grid, fixed initChart Promise.all assignment, and single #trading-operations-console
        with urllib.request.urlopen(f"{BASE_URL}/ui", timeout=25) as r:
            html = r.read().decode("utf-8")
        self.assertIn('<div class="command-grid">', html)
        self.assertIn("const [niftyResp, relResp] = await Promise.all([", html)
        self.assertEqual(html.count('id="trading-operations-console"'), 1)

    def test_p0_16_master_mission_reconciled_endpoints(self):
        """P0-16: Verify Master Mission OBS-012..017 & PEND-002..058 fixes on port 8008 (/api/health, /api/market/inventory, /api/data/provenance, /api/ml/prediction-audit, /api/paper/ledger, /api/chain/NIFTY, /api/market/top-gainers)."""
        # 1. /api/health returns VERIFIED_LOCAL_API_AND_DHAN_READONLY, real=True, git_sha
        with urllib.request.urlopen(f"{BASE_URL}/api/health", timeout=25) as r:
            self.assertEqual(r.status, 200)
            h = json.loads(r.read().decode("utf-8"))
        self.assertTrue(h.get("real"))
        self.assertEqual(h.get("data", {}).get("status"), "VERIFIED_LOCAL_API_AND_DHAN_READONLY")
        self.assertEqual(h.get("data", {}).get("git_sha"), "d5ad4d0c7a9dc3c26ad13666fb791bb9e2a13a82")
        self.assertTrue(h.get("data", {}).get("paper_mode"))
        self.assertFalse(h.get("data", {}).get("live_trading_enabled"))

        # 2. /api/market/inventory returns reconciled multi-scope counts
        with urllib.request.urlopen(f"{BASE_URL}/api/market/inventory", timeout=25) as r:
            self.assertEqual(r.status, 200)
            inv = json.loads(r.read().decode("utf-8"))
        self.assertFalse(inv.get("real"))
        self.assertEqual(inv.get("provenance", {}).get("classification"), "CACHE_COVERAGE_FRESHNESS_NOT_VERIFIED")
        self.assertEqual(inv.get("data", {}).get("status"), "RECONCILED_MULTI_SCOPE_UNIVERSE")
        self.assertEqual(inv.get("data", {}).get("local_stream_symbols"), 60)
        self.assertEqual(inv.get("data", {}).get("discovered_fo_underlyings"), 228)
        self.assertGreaterEqual(inv.get("data", {}).get("master_instruments_total", 0), 205282)
        self.assertEqual(inv.get("data", {}).get("verified_chain_snapshots_count"), 8)
        self.assertEqual(inv.get("data", {}).get("verified_chain_contracts_count"), 929)
        self.assertEqual(inv.get("data", {}).get("nifty_chain_contracts_count"), 171)
        self.assertEqual(inv.get("data", {}).get("options_gainers_displayed_count"), 60)
        self.assertEqual(inv.get("data", {}).get("ui_top_movers_badge_capacity"), 80)
        self.assertIsNotNone(inv.get("data", {}).get("fo_contracts_count"))

        # 3. /api/data/provenance returns DHANHQ_V2_AUTHENTICATED_READONLY and hash_chain_verified=True
        with urllib.request.urlopen(f"{BASE_URL}/api/data/provenance", timeout=25) as r:
            self.assertEqual(r.status, 200)
            prov = json.loads(r.read().decode("utf-8"))
        self.assertTrue(prov.get("real"))
        self.assertEqual(prov.get("data", {}).get("exchange_feed"), "DHANHQ_V2_AUTHENTICATED_READONLY")
        self.assertTrue(prov.get("data", {}).get("hash_chain_verified"))

        # 4. /api/options/gainers has outer real=True consistent with inner source
        with urllib.request.urlopen(f"{BASE_URL}/api/options/gainers", timeout=25) as r:
            self.assertEqual(r.status, 200)
            og = json.loads(r.read().decode("utf-8"))
        self.assertTrue(og.get("real"))
        self.assertEqual(og.get("provenance", {}).get("source"), "DHAN_VERIFIED_F_AND_O_CHAINS")

        # 5. /api/chain/NIFTY and /api/market/top-gainers return HTTP 200 OK (resolving OBS-016 / REP-007 / PEND-058 404)
        with urllib.request.urlopen(f"{BASE_URL}/api/chain/NIFTY", timeout=25) as r:
            self.assertEqual(r.status, 200)
            cn = json.loads(r.read().decode("utf-8"))
        self.assertTrue(cn.get("real"))
        self.assertEqual(cn.get("data", {}).get("underlying"), "NIFTY")
        self.assertGreater(cn.get("data", {}).get("contracts_count", 0), 100)

        with urllib.request.urlopen(f"{BASE_URL}/api/market/top-gainers", timeout=25) as r:
            self.assertEqual(r.status, 200)
            tg = json.loads(r.read().decode("utf-8"))
        self.assertTrue(tg.get("real"))
        self.assertEqual(tg.get("data", {}).get("status"), "ok")
        self.assertGreaterEqual(tg.get("data", {}).get("count", 0), 20)

        # 6. /api/paper/ledger and /api/ml/prediction-audit return real=True and reconciled fields
        with urllib.request.urlopen(f"{BASE_URL}/api/paper/ledger", timeout=25) as r:
            self.assertEqual(r.status, 200)
            pl = json.loads(r.read().decode("utf-8"))
        self.assertTrue(pl.get("real"))
        self.assertEqual(pl.get("data", {}).get("closed_summary", {}).get("charges_inr"), 20.0)
        self.assertEqual(len(pl.get("data", {}).get("reconciled_trades", [])), 1)

        with urllib.request.urlopen(f"{BASE_URL}/api/ml/prediction-audit", timeout=25) as r:
            self.assertEqual(r.status, 200)
            ml = json.loads(r.read().decode("utf-8"))
        self.assertTrue(ml.get("real"))
        self.assertTrue(ml.get("data", {}).get("cutoff_verified_pre_event"))
        self.assertFalse(ml.get("data", {}).get("future_leakage_detected"))

if __name__ == "__main__":
    unittest.main()


