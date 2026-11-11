import urllib.request
import re

url = "http://127.0.0.1:8008/ui"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=5) as resp:
    html = resp.read().decode("utf-8")

print(f"UI HTML length: {len(html)} bytes")

# 1. Check for broken ? in banner
has_question_mark_banner = "GENESIS SYSTEM3 ?" in html
has_bullet_banner = "GENESIS SYSTEM3 &#9679;" in html or "GENESIS SYSTEM3 ●" in html
print(f"Broken question mark in banner: {has_question_mark_banner} (Expected: False)")
print(f"Correct bullet in banner: {has_bullet_banner} (Expected: True)")

# 2. Check for timeframe buttons
tf_1m = "onclick=\"setTimeframe('1M')\"" in html
tf_5m = "onclick=\"setTimeframe('5M')\"" in html
tf_15m = "onclick=\"setTimeframe('15M')\"" in html
tf_1d = "onclick=\"setTimeframe('1D')\"" in html
print(f"Timeframe 1M onclick: {tf_1m}")
print(f"Timeframe 5M onclick: {tf_5m}")
print(f"Timeframe 15M onclick: {tf_15m}")
print(f"Timeframe 1D onclick: {tf_1d}")

# 3. Check for chart mode & duration buttons
cm_price = "onclick=\"setChartMode('Price')\"" in html
cm_returns = "onclick=\"setChartMode('Returns')\"" in html
cm_spread = "onclick=\"setChartMode('Spread')\"" in html
cd_1d = "onclick=\"setChartDuration('1D')\"" in html
print(f"Chart mode Price: {cm_price}")
print(f"Chart mode Returns: {cm_returns}")
print(f"Chart mode Spread: {cm_spread}")
print(f"Chart duration 1D: {cd_1d}")

# 4. Check for Tab action buttons
tab2_sqoff = "onclick=\"actionSquareOff()\"" in html
tab2_risk = "onclick=\"actionInspectRisk()\"" in html
tab3_sel = "id=\"reasoning-symbol-select\"" in html
tab4_run = "onclick=\"runLiveEndpointVerification()\"" in html
print(f"Tab 2 Square-Off action: {tab2_sqoff}")
print(f"Tab 2 Risk action: {tab2_risk}")
print(f"Tab 3 Symbol select: {tab3_sel}")
print(f"Tab 4 Quantum run button: {tab4_run}")

# 5. Check for synchronized ticker elements
has_nifty_sync = "id=\"t-nifty-val\"" in html
has_bank_sync = "id=\"t-bank-val\"" in html
has_sensex_sync = "id=\"t-sensex-val\"" in html
has_reliance_sync = "id=\"t-reliance-val\"" in html
print(f"Top ticker NIFTY element: {has_nifty_sync}")
print(f"Top ticker BANK element: {has_bank_sync}")
print(f"Top ticker SENSEX element: {has_sensex_sync}")
print(f"Top ticker RELIANCE element: {has_reliance_sync}")

# 6. Check for full JS suite
has_suite = "FULL UI INTERACTIVE SOLUTION" in html
print(f"Full JS interactive suite present: {has_suite}")

assert not has_question_mark_banner, "Must not have broken question mark banner"
assert has_bullet_banner, "Must have bullet banner"
assert tf_1m and tf_5m and tf_15m and tf_1d, "All timeframe buttons must have onclick"
assert cm_price and cm_returns and cm_spread, "All chart mode buttons must have onclick"
assert tab2_sqoff and tab2_risk and tab3_sel and tab4_run, "All tab action controls must exist"
assert has_suite, "Full JS suite must be present"

print("\nALL UI INTERACTIVITY ASSERTIONS PASSED!")
