from pathlib import Path

vm_path = Path(r"c:\Genesis_System3_clean\content\app\verified_market.py")
text = vm_path.read_text(encoding="utf-8")

bad_chunk = '''    default_ids = {"NIFTY": 13, "BANKNIFTY": 25, "SENSEX": 51}

# Official previous day closing prices (Benchmark Google Finance / NSE / BSE)
OFFICIAL_PREV_CLOSE = {
    "NIFTY": 23810.85,
    "BANKNIFTY": 55540.05,
    "SENSEX": 76917.85,
    "RELIANCE": 1284.50,
    "FINNIFTY": 26820.40,
    "MIDCPNIFTY": 12940.10,
}

    resolved_ids = ids or default_ids'''

good_chunk = '''# Official previous day closing prices (Benchmark Google Finance / NSE / BSE)
OFFICIAL_PREV_CLOSE = {
    "NIFTY": 23810.85,
    "BANKNIFTY": 55540.05,
    "SENSEX": 76917.85,
    "RELIANCE": 1284.50,
    "FINNIFTY": 26820.40,
    "MIDCPNIFTY": 12940.10,
}


def _get_eod_fallback(meta=None, ids=None, fallback_reason="Cached verified Dhan quote snapshot (rate-limit or after-hours fallback); no order requests sent"):
    now = datetime.now(timezone.utc)
    default_ids = {"NIFTY": 13, "BANKNIFTY": 25, "SENSEX": 51}
    resolved_ids = ids or default_ids'''

# Check if def _get_eod_fallback is above bad_chunk
if bad_chunk in text:
    # Remove the earlier def _get_eod_fallback line right before bad_chunk
    def_line = 'def _get_eod_fallback(meta=None, ids=None, fallback_reason="Cached verified Dhan quote snapshot (rate-limit or after-hours fallback); no order requests sent"):\n    now = datetime.now(timezone.utc)\n'
    if def_line in text:
        text = text.replace(def_line + bad_chunk, good_chunk)
    else:
        text = text.replace(bad_chunk, good_chunk)
    vm_path.write_text(text, encoding="utf-8")
    print("Fixed OFFICIAL_PREV_CLOSE position in verified_market.py!")
else:
    print("bad_chunk not matched, inspecting lines...")
    import re
    # Clean up any bad OFFICIAL_PREV_CLOSE placement
    text = re.sub(r'# Official previous day closing prices[^\n]*\nOFFICIAL_PREV_CLOSE\s*=\s*\{[^\}]+\}\n*', '', text)
    # Insert at top level before _get_eod_fallback
    text = text.replace('def _get_eod_fallback(', '''# Official previous day closing prices (Benchmark Google Finance / NSE / BSE)
OFFICIAL_PREV_CLOSE = {
    "NIFTY": 23810.85,
    "BANKNIFTY": 55540.05,
    "SENSEX": 76917.85,
    "RELIANCE": 1284.50,
    "FINNIFTY": 26820.40,
    "MIDCPNIFTY": 12940.10,
}


def _get_eod_fallback(''')
    vm_path.write_text(text, encoding="utf-8")
    print("Cleaned up and placed OFFICIAL_PREV_CLOSE properly in verified_market.py!")
