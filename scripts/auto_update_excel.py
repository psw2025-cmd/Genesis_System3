"""
Auto Update Excel - Runs continuously and updates Excel every 5 minutes
"""

import sys
from pathlib import Path
import time
from datetime import datetime
import pytz

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.build_advanced_excel_with_ai_predictions import AdvancedExcelBuilder
from src.utils.market_hours import is_market_open


def auto_update_excel():
    """Continuously update Excel every 5 minutes during market hours."""
    print("=" * 80)
    print("  EXCEL AUTO-UPDATER - RUNNING IN BACKGROUND")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Update interval: 5 minutes")
    print("Will update during market hours only")
    print("=" * 80)

    builder = AdvancedExcelBuilder()
    excel_path = ROOT_DIR / "outputs" / "OptionChain_Master_v3_AI_FINAL.xlsx"
    ist = pytz.timezone("Asia/Kolkata")
    update_count = 0

    try:
        while True:
            now = datetime.now(ist)

            # Check if market is open
            if is_market_open(now):
                try:
                    print(f"\n[{now.strftime('%H:%M:%S')}] Updating Excel...")
                    builder.create_excel_file(excel_path)
                    update_count += 1
                    print(f"  [OK] Excel updated (Update #{update_count})")
                except Exception as e:
                    print(f"  [ERROR] Failed to update Excel: {e}")
            else:
                # Market closed - wait longer
                if update_count == 0:
                    print(f"\n[{now.strftime('%H:%M:%S')}] Market closed, waiting...")

            # Wait 5 minutes (300 seconds)
            time.sleep(300)

    except KeyboardInterrupt:
        print(f"\n\nStopped after {update_count} updates")
    except Exception as e:
        print(f"\n\nError: {e}")


if __name__ == "__main__":
    auto_update_excel()
