"""
Verify Parallel Processing for All Indices
"""

import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import pandas as pd

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.brokers.angel_one.broker import AngelOneBroker

ALL_INDICES = [
    {"name": "NIFTY", "exchange": "NFO"},
    {"name": "BANKNIFTY", "exchange": "NFO"},
    {"name": "FINNIFTY", "exchange": "NFO"},
    {"name": "MIDCPNIFTY", "exchange": "NFO"},
    {"name": "SENSEX", "exchange": "BFO"},
]


def fetch_index_parallel(index_config):
    """Fetch data for one index."""
    name = index_config["name"]
    exchange = index_config["exchange"]

    try:
        broker = AngelOneBroker(allow_data_only=True)
        chain_data = broker.get_option_chain_by_underlying(name, exchange=exchange)

        if chain_data:
            df = pd.DataFrame(chain_data)
            return {
                "index": name,
                "success": True,
                "count": len(df),
                "has_greeks": df["delta"].notna().any(),
                "has_pOI": df["pOI"].notna().any() if "pOI" in df.columns else False,
            }
        else:
            return {"index": name, "success": False, "count": 0}
    except Exception as e:
        return {"index": name, "success": False, "error": str(e)}


def test_parallel():
    """Test parallel fetching."""
    print("=" * 80)
    print("  PARALLEL PROCESSING VERIFICATION")
    print("=" * 80)

    # Sequential
    print("\n[TEST 1] Sequential Fetching...")
    start = time.time()
    sequential_results = []
    for idx in ALL_INDICES:
        result = fetch_index_parallel(idx)
        sequential_results.append(result)
    sequential_time = time.time() - start
    print(f"  Time: {sequential_time:.2f} seconds")

    # Parallel
    print("\n[TEST 2] Parallel Fetching...")
    start = time.time()
    parallel_results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(fetch_index_parallel, idx): idx["name"] for idx in ALL_INDICES}
        for future in as_completed(futures):
            result = future.result()
            parallel_results.append(result)
    parallel_time = time.time() - start
    print(f"  Time: {parallel_time:.2f} seconds")

    # Comparison
    speedup = sequential_time / parallel_time if parallel_time > 0 else 0
    print(f"\n[RESULT] Speedup: {speedup:.2f}x faster with parallel processing")

    # Verify all succeeded
    all_success = all(r.get("success", False) for r in parallel_results)
    total_contracts = sum(r.get("count", 0) for r in parallel_results)

    print(f"\n  All indices fetched: {'YES' if all_success else 'NO'}")
    print(f"  Total contracts: {total_contracts}")

    for result in parallel_results:
        status = "✓" if result.get("success") else "✗"
        print(f"    {status} {result['index']:12s}: {result.get('count', 0)} contracts")

    return all_success


if __name__ == "__main__":
    test_parallel()
