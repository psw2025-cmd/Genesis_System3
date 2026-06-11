#!/usr/bin/env python
"""Quick verification script for option chain functionality"""
import sys
import os

sys.path.insert(0, '.')

print("=" * 60)
print("OPTION CHAIN VERIFICATION")
print("=" * 60)

# Test 1: Imports
print("\n1. Testing imports...")
try:
    from core.brokers.angel_one.broker import AngelOneBroker
    print("   ✓ AngelOneBroker imported")
except Exception as e:
    print(f"   ✗ Import failed: {e}")
    sys.exit(1)

try:
    from core.engine.test_angelone_option_chain import main, format_option_chain
    print("   ✓ Test script imported")
except Exception as e:
    print(f"   ✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Check dependencies
print("\n2. Testing dependencies...")
try:
    from SmartApi import SmartConnect
    print("   ✓ SmartApi available")
except Exception as e:
    print(f"   ✗ SmartApi missing: {e}")
    sys.exit(1)

try:
    import pyotp
    print("   ✓ pyotp available")
except Exception as e:
    print(f"   ✗ pyotp missing: {e}")
    sys.exit(1)

try:
    import pandas as pd
    print("   ✓ pandas available")
except Exception as e:
    print(f"   ✗ pandas missing: {e}")
    sys.exit(1)

# Test 3: Check credentials (don't fail if missing)
print("\n3. Checking credentials...")
from core.utils.env_loader import get_angelone_credentials
creds = get_angelone_credentials()
missing = [k for k, v in creds.items() if not v]
if missing:
    print(f"   ⚠ Missing credentials: {', '.join(missing)}")
    print("   (Script will fail at runtime without credentials)")
else:
    print("   ✓ All credentials present")

# Test 4: Check instruments file
print("\n4. Checking instruments master...")
instruments_path = "storage/instruments/OpenAPIScripMaster.json"
if os.path.exists(instruments_path):
    size = os.path.getsize(instruments_path)
    print(f"   ✓ Instruments file exists ({size:,} bytes)")
else:
    print(f"   ⚠ Instruments file missing: {instruments_path}")
    print("   (Script will fail without instruments master)")

# Test 5: Check code structure
print("\n5. Checking code structure...")
broker_file = "core/brokers/angel_one/broker.py"
if os.path.exists(broker_file):
    with open(broker_file, 'r') as f:
        content = f.read()
        if 'get_option_chain_by_underlying' in content:
            print("   ✓ get_option_chain_by_underlying method exists")
        else:
            print("   ✗ get_option_chain_by_underlying method missing")
        
        if 'allow_data_only' in content:
            print("   ✓ allow_data_only parameter exists")
        else:
            print("   ✗ allow_data_only parameter missing")

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)
print("\nTo test with actual data, run:")
print("  python -m core.engine.test_angelone_option_chain NIFTY")
print("\n(Requires valid credentials in config/.env)")
