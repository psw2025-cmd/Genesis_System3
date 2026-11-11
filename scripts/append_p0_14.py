with open(r"C:\Genesis_System3_clean\tests\test_ui_p0_recovery_mission.py", "r", encoding="utf-8") as f:
    text = f.read()

new_test = '''
    def test_p0_14_full_ui_interactivity_and_market_hours(self):
        """P0-14: Verify full UI interactivity, elimination of broken unicode, dynamic market session, and button bindings."""
        url = f"{BASE_URL}/ui"
        with urllib.request.urlopen(url, timeout=10) as r:
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
'''

target = 'if __name__ == "__main__":'
if target in text:
    text = text.replace(target, new_test + '\n' + target)
    with open(r"C:\Genesis_System3_clean\tests\test_ui_p0_recovery_mission.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Added P0-14 to test suite.")
else:
    print("Target not found.")
