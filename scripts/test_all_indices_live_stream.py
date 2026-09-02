"""Test all 6 indices live stream from Dhan."""

import asyncio
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from dashboard.backend.app import _get_chain_uncached

async def main():
    print("=" * 85)
    print("   GENESIS SYSTEM3 — ALL 6 INDICES REAL-TIME DATA STREAM VERIFICATION")
    print("=" * 85)

    indices = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX", "BANKEX"]
    for idx in indices:
        try:
            res = await _get_chain_uncached(idx)
            spot = float(res.get("spot") or 0)
            contracts = int(res.get("total_contracts") or 0)
            pcr = float(res.get("pcr") or 0)
            status = res.get("status") or "UNKNOWN"
            source = res.get("data_source") or "dhan"
            print(f"   [OK] {idx:<12} | Spot: {spot:>10.2f} | Contracts: {contracts:>4} | PCR: {pcr:>5.3f} | Status: {status:<12} | Source: {source}")
        except Exception as e:
            print(f"   [FAIL] {idx:<10} | Error: {e}")

    print("=" * 85)

if __name__ == "__main__":
    asyncio.run(main())
