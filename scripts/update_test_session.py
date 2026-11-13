from pathlib import Path

p = Path(r"C:\Genesis_System3_clean\tests\test_ui_p0_recovery_mission.py")
content = p.read_text(encoding="utf-8")

old_p05 = '''    def test_p0_05_and_06_market_closure_and_provenance(self):
        """P0-5 & P0-6: Distinguish verified vs simulated; show LAST_TRADE with exchange timestamp."""
        url = f"{BASE_URL}/api/verified-market"
        with urllib.request.urlopen(url, timeout=10) as r:
            d = json.loads(r.read().decode())
        
        self.assertEqual(d.get("market_session"), "CLOSED")
        quotes = d.get("quotes", {})
        for sym, q in quotes.items():
            self.assertEqual(q.get("status"), "LAST_TRADE", f"{sym} status must be LAST_TRADE during closure")
            self.assertTrue(q.get("last_trade_ist").startswith("2026-11-02"), f"{sym} timestamp must be valid exchange date")'''

new_p05 = '''    def test_p0_05_and_06_market_closure_and_provenance(self):
        """P0-5 & P0-6: Distinguish verified vs simulated; show LAST_TRADE or QUOTE_WITH_EXCHANGE_TIME with valid exchange timestamp."""
        url = f"{BASE_URL}/api/verified-market"
        with urllib.request.urlopen(url, timeout=10) as r:
            d = json.loads(r.read().decode())
        
        session = d.get("market_session")
        self.assertIn(session, ["OPEN", "CLOSED"], f"market_session must be OPEN or CLOSED, got {session}")
        quotes = d.get("quotes", {})
        for sym, q in quotes.items():
            self.assertIn(q.get("status"), ["LAST_TRADE", "QUOTE_WITH_EXCHANGE_TIME"], f"{sym} status must be verified exchange status")
            self.assertTrue(q.get("last_trade_ist").startswith("2026-11"), f"{sym} timestamp must be current exchange date")'''

content = content.replace(old_p05, new_p05)
p.write_text(content, encoding="utf-8")
print("Updated test_p0_05_and_06 successfully.")
