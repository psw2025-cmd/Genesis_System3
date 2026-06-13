"""
Comprehensive End-to-End Verification
- Fetch all indices
- Verify all calculations
- Test paper trading
- Multi-validation
- QC audit
- Parallel processing verification
"""

import sys
from pathlib import Path
from datetime import datetime
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

try:
    import pytz
    import pandas as pd
    _NUMERIC_AVAILABLE = True
except ImportError:
    pytz = None
    pd = None
    _NUMERIC_AVAILABLE = False

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from core.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

_SCRIPT_DISABLED_REASON = (
    "comprehensive_end_to_end_verification: Dhan broker path is disabled. "
    "System3 is Dhan-only. This script cannot run live data verification."
)
from src.validation.qc_validator import QCValidator
from src.trading.paper_executor import PaperExecutor
from src.trading.pnl_tracker import PnLTracker
from core.utils.option_chain_calculations import add_calculated_columns

# All indices to verify
ALL_INDICES = [
    {"name": "NIFTY", "exchange": "NFO", "index_exchange": "NSE"},
    {"name": "BANKNIFTY", "exchange": "NFO", "index_exchange": "NSE"},
    {"name": "FINNIFTY", "exchange": "NFO", "index_exchange": "NSE"},
    {"name": "MIDCPNIFTY", "exchange": "NFO", "index_exchange": "NSE"},
    {"name": "SENSEX", "exchange": "BFO", "index_exchange": "BSE"},
]


def verify_index_fetch(index_config):
    """Verify fetching data for a single index."""
    name = index_config["name"]
    exchange = index_config["exchange"]

    print(f"\n  [INDEX] {name} ({exchange})")

    return {"index": name, "status": "DISABLED", "count": 0, "error": _SCRIPT_DISABLED_REASON}


def verify_calculations(df):
    """Verify all calculations are correct."""
    issues = []

    # Verify pOI calculation
    if "pOI" in df.columns and "oi" in df.columns and "ltp" in df.columns:
        mask = df["pOI"].notna() & df["oi"].notna() & df["ltp"].notna() & (df["ltp"] > 0)
        if mask.any():
            expected_pOI = (df.loc[mask, "oi"] * df.loc[mask, "ltp"]).astype(int)
            actual_pOI = df.loc[mask, "pOI"].astype(int)
            mismatches = (expected_pOI != actual_pOI).sum()
            if mismatches > 0:
                issues.append(f"pOI calculation: {mismatches} mismatches")

    # Verify pVolume calculation
    if "pVolume" in df.columns and "volume" in df.columns and "ltp" in df.columns:
        mask = df["pVolume"].notna() & df["volume"].notna() & df["ltp"].notna() & (df["ltp"] > 0)
        if mask.any():
            expected_pVolume = (df.loc[mask, "volume"] * df.loc[mask, "ltp"]).astype(int)
            actual_pVolume = df.loc[mask, "pVolume"].astype(int)
            mismatches = (expected_pVolume != actual_pVolume).sum()
            if mismatches > 0:
                issues.append(f"pVolume calculation: {mismatches} mismatches")

    # Verify delta range
    if "delta" in df.columns and "option_type" in df.columns:
        ce_invalid = (
            (df["option_type"] == "CE") & (df["delta"].notna()) & ((df["delta"] < 0) | (df["delta"] > 1))
        ).sum()
        pe_invalid = (
            (df["option_type"] == "PE") & (df["delta"].notna()) & ((df["delta"] > 0) | (df["delta"] < -1))
        ).sum()
        if ce_invalid > 0 or pe_invalid > 0:
            issues.append(f"Delta range: {ce_invalid} CE invalid, {pe_invalid} PE invalid")

    # Verify IV range
    if "iv" in df.columns:
        invalid_iv = ((df["iv"] <= 0) | (df["iv"] > 2.0) & df["iv"].notna()).sum()
        if invalid_iv > 0:
            issues.append(f"IV range: {invalid_iv} invalid values")

    # Verify bid <= ask
    if "bidPrice" in df.columns and "offerPrice" in df.columns:
        invalid_spread = ((df["bidPrice"] > df["offerPrice"]) & df["bidPrice"].notna() & df["offerPrice"].notna()).sum()
        if invalid_spread > 0:
            issues.append(f"Bid/Ask: {invalid_spread} invalid spreads")

    return issues


def verify_paper_trading():
    """Verify paper trading components work."""
    print("\n" + "=" * 80)
    print("  VERIFYING PAPER TRADING")
    print("=" * 80)

    issues = []

    try:
        # Test PaperExecutor
        executor = PaperExecutor()
        print("  [OK] PaperExecutor initialized")

        # Test PnLTracker
        tracker = PnLTracker()
        print("  [OK] PnLTracker initialized")

        # Test trade execution
        position = executor.execute_trade(
            trading_symbol="NIFTY24FEB2625000CE",
            strike=25000.0,
            option_type="CE",
            action="BUY",
            quantity=1,
            entry_price=100.0,
            underlying="NIFTY",
            spot_price=25300.0,
        )
        if position:
            print(f"  [OK] Trade execution: Position {position.get('position_id')} created")
        else:
            issues.append("Trade execution failed")

        # Test PnL update
        positions_summary = executor.get_positions_summary()
        tracker.update(positions_summary)
        pnl = tracker.get_summary()
        print(f"  [OK] PnL tracking: Total PnL = Rs {pnl.get('total_pnl', 0):.2f}")

    except Exception as e:
        issues.append(f"Paper trading error: {e}")
        import traceback

        traceback.print_exc()

    return issues


def run_qc_audit(df):
    """Run QC audit on the data."""
    print("\n" + "=" * 80)
    print("  QC AUDIT")
    print("=" * 80)

    try:
        qc_validator = QCValidator(sim_mode=False)
        # QC validator expects a dict of DataFrames, not a single DataFrame
        if isinstance(df, pd.DataFrame):
            # Create a dict with all indices combined
            result = qc_validator.validate_all({"ALL": df})
        else:
            result = qc_validator.validate_all(df)

        if result.get("overall_passed") or result.get("overall_status") == "PASS":
            print("  [OK] QC Audit: PASSED")
            return True, []
        else:
            print(f"  [WARNING] QC Audit: {result.get('overall_status', 'FAILED')}")
            failures = result.get("failed_checks", [])
            for failure in failures:
                print(f"    - {failure}")
            return False, failures

    except Exception as e:
        print(f"  [ERROR] QC Audit failed: {e}")
        import traceback

        traceback.print_exc()
        return False, [str(e)]


def main():
    """Main verification function."""
    print("=" * 80)
    print("  COMPREHENSIVE END-TO-END VERIFICATION")
    print("=" * 80)
    print("\nThis will verify:")
    print("  1. All indices data fetching")
    print("  2. All calculations correctness")
    print("  3. Paper trading functionality")
    print("  4. Parallel processing")
    print("  5. Multi-validation")
    print("  6. QC audit")
    print("  7. End-to-end process")

    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    print(f"\nStart Time: {now.strftime('%Y-%m-%d %H:%M:%S IST')}")

    all_results = {}
    all_issues = []

    # Step 1: Verify all indices fetching (parallel)
    print("\n" + "=" * 80)
    print("  [STEP 1] VERIFYING ALL INDICES DATA FETCHING (PARALLEL)")
    print("=" * 80)

    start_time = time.time()

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_index = {executor.submit(verify_index_fetch, idx): idx["name"] for idx in ALL_INDICES}

        for future in as_completed(future_to_index):
            index_name = future_to_index[future]
            try:
                result = future.result()
                all_results[index_name] = result
                status_icon = (
                    "[OK]" if result["status"] == "OK" else "[PARTIAL]" if result["status"] == "PARTIAL" else "[FAIL]"
                )
                print(f"  {status_icon} {index_name:12s}: {result['count']:4d} contracts - {result['status']}")
                if "error" in result:
                    print(f"      Error: {result['error']}")
                    all_issues.append(f"{index_name}: {result['error']}")
            except Exception as e:
                print(f"  [ERROR] {index_name:12s}: ERROR - {e}")
                all_issues.append(f"{index_name}: {e}")

    elapsed = time.time() - start_time
    print(f"\n  [INFO] Parallel fetch completed in {elapsed:.2f} seconds")

    # Step 2: Verify calculations
    print("\n" + "=" * 80)
    print("  [STEP 2] VERIFYING ALL CALCULATIONS")
    print("=" * 80)

    # Load chain_raw_live.csv
    csv_path = ROOT_DIR / "outputs" / "chain_raw_live.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        calc_issues = verify_calculations(df)
        if calc_issues:
            print("  [WARNING] Calculation issues found:")
            for issue in calc_issues:
                print(f"    - {issue}")
                all_issues.append(f"Calculation: {issue}")
        else:
            print("  [OK] All calculations verified correct")
    else:
        print("  [WARNING] chain_raw_live.csv not found")
        all_issues.append("chain_raw_live.csv not found")

    # Step 3: Verify paper trading
    paper_issues = verify_paper_trading()
    if paper_issues:
        all_issues.extend(paper_issues)

    # Step 4: QC Audit
    if csv_path.exists():
        qc_passed, qc_issues = run_qc_audit(df)
        if qc_issues:
            all_issues.extend([f"QC: {issue}" for issue in qc_issues])
    else:
        qc_passed = False
        all_issues.append("QC: Cannot run - CSV not found")

    # Step 5: Multi-validation summary
    print("\n" + "=" * 80)
    print("  [STEP 5] MULTI-VALIDATION SUMMARY")
    print("=" * 80)

    total_contracts = sum(r.get("count", 0) for r in all_results.values())
    successful_indices = sum(1 for r in all_results.values() if r.get("status") == "OK")
    partial_indices = sum(1 for r in all_results.values() if r.get("status") == "PARTIAL")

    print(f"\n  Indices Status:")
    print(f"    Total Indices: {len(ALL_INDICES)}")
    print(f"    Successful: {successful_indices}")
    print(f"    Partial: {partial_indices}")
    print(f"    Failed: {len(ALL_INDICES) - successful_indices - partial_indices}")
    print(f"    Total Contracts: {total_contracts}")

    print(f"\n  Data Completeness:")
    for idx_name, result in all_results.items():
        if "checks" in result:
            checks = result["checks"]
            print(f"    {idx_name:12s}:")
            print(f"      Contracts: {result['count']}")
            print(f"      pOI: {result.get('pOI_count', 0)}")
            print(f"      Delta: {result.get('delta_count', 0)}")
            print(f"      Timestamps: {result.get('timestamp_count', 0)}")

    # Final Summary
    print("\n" + "=" * 80)
    print("  FINAL SUMMARY")
    print("=" * 80)

    if all_issues:
        print(f"\n  [WARNINGS] {len(all_issues)} issues found:")
        for issue in all_issues[:10]:  # Show first 10
            print(f"    - {issue}")
        if len(all_issues) > 10:
            print(f"    ... and {len(all_issues) - 10} more")
    else:
        print("\n  [SUCCESS] All verifications passed!")

    print(f"\n  Status: {'PASS' if len(all_issues) == 0 else 'REVIEW REQUIRED'}")
    print(f"  End Time: {datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S IST')}")

    # Save results (convert non-serializable types)
    results_path = ROOT_DIR / "outputs" / "verification_results.json"

    # Convert results to JSON-serializable format
    serializable_results = {}
    for idx_name, result in all_results.items():
        serializable_results[idx_name] = {
            "index": result.get("index"),
            "status": result.get("status"),
            "count": result.get("count"),
            "pOI_count": result.get("pOI_count", 0),
            "delta_count": result.get("delta_count", 0),
            "timestamp_count": result.get("timestamp_count", 0),
            "error": result.get("error") if "error" in result else None,
        }
        if "checks" in result:
            serializable_results[idx_name]["checks"] = {
                k: bool(v) if isinstance(v, (bool, pd.Series)) else v for k, v in result["checks"].items()
            }

    results_data = {
        "timestamp": datetime.now(ist).isoformat(),
        "indices_results": serializable_results,
        "total_contracts": int(total_contracts),
        "issues": all_issues,
        "qc_passed": bool(qc_passed),
        "status": "PASS" if len(all_issues) == 0 else "REVIEW REQUIRED",
    }

    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results_data, f, indent=2, ensure_ascii=False)

    print(f"\n  Results saved to: {results_path}")
    print("=" * 80)

    return len(all_issues) == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
