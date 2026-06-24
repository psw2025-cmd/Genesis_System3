"""Verify system is running and updating files"""

import sys
import time
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
outputs_dir = ROOT_DIR / "outputs"
chain_file = outputs_dir / "chain_raw_live.csv"

print("=" * 80)
print("  SYSTEM STATUS VERIFICATION")
print("=" * 80)
print()

print(f"File exists: {chain_file.exists()}")
if chain_file.exists():
    m1 = chain_file.stat().st_mtime
    age1 = (datetime.now().timestamp() - m1) / 60
    size1 = chain_file.stat().st_size

    print(f"Current age: {age1:.1f} minutes")
    print(f"Size: {size1:,} bytes")
    print()
    print("Monitoring for 15 seconds...")

    time.sleep(15)

    if chain_file.exists():
        m2 = chain_file.stat().st_mtime
        age2 = (datetime.now().timestamp() - m2) / 60
        size2 = chain_file.stat().st_size

        print()
        if m2 > m1:
            print("✅ FILE IS UPDATING - SYSTEM WORKING!")
            print(f"   Updated during monitoring")
            print(f"   New age: {age2:.1f} minutes")
            print(f"   Size: {size1:,} → {size2:,} bytes")
        else:
            print("⚠️  FILE NOT UPDATING")
            print(f"   Still {age2:.1f} minutes old")
            print("   System may be stuck")
    else:
        print("❌ FILE DISAPPEARED")
else:
    print("❌ FILE NOT FOUND")
    print("   System may not have started yet")

print()
print("=" * 80)
