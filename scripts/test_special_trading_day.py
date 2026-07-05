"""Test special trading day detection"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from datetime import datetime

import pytz

from src.utils.market_hours import is_market_open

ist = pytz.timezone("Asia/Kolkata")
now = datetime.now(ist)
open, reason = is_market_open(now)

print("=" * 80)
print("  SPECIAL TRADING DAY TEST")
print("=" * 80)
print(f"\nCurrent Date: {now.strftime('%Y-%m-%d %A')}")
print(f"Current Time: {now.strftime('%H:%M:%S IST')}")
print(f"\nMarket Status: {'OPEN' if open else 'CLOSED'}")
print(f"Reason: {reason}")
print("\n" + "=" * 80)
