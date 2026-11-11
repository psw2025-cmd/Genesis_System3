from pathlib import Path

p = Path(r"C:\Genesis_System3_clean\tests\test_ui_p0_recovery_mission.py")
text = p.read_text(encoding="utf-8")

old_code = """        # 2. State cache exists
        market_top = Path(r"C:\\Genesis_System3_clean\\state\\market_top_ce_pe.json")
        self.assertTrue(market_top.is_file(), "market_top_ce_pe.json state file must exist")"""

new_code = """        # 2. Verify options gainers route returns live data without disk cache
        gainers_url = f"{BASE_URL}/api/options/gainers"
        with urllib.request.urlopen(gainers_url, timeout=10) as gr:
            self.assertEqual(gr.status, 200)
            gdata = json.loads(gr.read().decode())
        self.assertIn("data", gdata, "Options gainers must return data envelope")
        self.assertGreater(gdata.get("data", {}).get("total_ce", 0), 0, "Live CE contracts must be present")"""

text_norm = text.replace("\r\n", "\n")
old_norm = old_code.replace("\r\n", "\n")
new_norm = new_code.replace("\r\n", "\n")

if old_norm in text_norm:
    text_norm = text_norm.replace(old_norm, new_norm, 1)
    p.write_text(text_norm, encoding="utf-8")
    print("Successfully replaced line 36 assertion in test_ui_p0_recovery_mission.py")
else:
    print("old_norm not found in file!")
