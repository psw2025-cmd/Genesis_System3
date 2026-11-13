from pathlib import Path

app_path = Path(r"c:\Genesis_System3_clean\content\app\app.py")
text = app_path.read_text(encoding="utf-8")

bad_chunk = '''BASE_PRICES: Dict[str, float] = {

OFFICIAL_PREV_CLOSE: Dict[str, float] = {
    "NIFTY": 23810.85,
    "BANKNIFTY": 55540.05,
    "SENSEX": 76917.85,
    "RELIANCE": 1284.50,
    "TCS": 3330.00,
    "INFY": 1490.00,
    "HDFCBANK": 995.00,
    "ICICIBANK": 1390.00,
    "FINNIFTY": 26820.40,
    "MIDCPNIFTY": 12940.10,
}'''

good_chunk = '''OFFICIAL_PREV_CLOSE: Dict[str, float] = {
    "NIFTY": 23810.85,
    "BANKNIFTY": 55540.05,
    "SENSEX": 76917.85,
    "RELIANCE": 1284.50,
    "TCS": 3330.00,
    "INFY": 1490.00,
    "HDFCBANK": 995.00,
    "ICICIBANK": 1390.00,
    "FINNIFTY": 26820.40,
    "MIDCPNIFTY": 12940.10,
}

BASE_PRICES: Dict[str, float] = {'''

if bad_chunk in text:
    text = text.replace(bad_chunk, good_chunk)
    app_path.write_text(text, encoding="utf-8")
    print("Cleaned up OFFICIAL_PREV_CLOSE before BASE_PRICES in app.py!")
else:
    print("bad_chunk not found, checking exact pattern...")
    import re
    text = re.sub(r'BASE_PRICES:\s*Dict\[str,\s*float\]\s*=\s*\{\s*OFFICIAL_PREV_CLOSE:\s*Dict\[str,\s*float\]\s*=\s*\{([^}]+)\}',
                  r'OFFICIAL_PREV_CLOSE: Dict[str, float] = {\1}\n\nBASE_PRICES: Dict[str, float] = {', text)
    app_path.write_text(text, encoding="utf-8")
    print("Regex replacement completed in app.py!")
