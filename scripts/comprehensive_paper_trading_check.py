"""
Comprehensive Paper Trading System Check
Verifies all components are working correctly for automated paper trading
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def check_component(component_name, check_func):
    """Run a check and return result."""
    try:
        result = check_func()
        status = "OK" if result.get("status") == "OK" else "ISSUE"
        return {
            "component": component_name,
            "status": status,
            "details": result.get("details", ""),
            "issues": result.get("issues", []),
        }
    except Exception as e:
        return {"component": component_name, "status": "ERROR", "details": f"Check failed: {e}", "issues": [str(e)]}


def check_paper_executor():
    """Check PaperExecutor component."""
    issues = []
    try:
        from src.trading.paper_executor import PaperExecutor

        executor = PaperExecutor()

        # Check initialization
        if not hasattr(executor, "positions"):
            issues.append("Missing positions attribute")
        if not hasattr(executor, "execute_trade"):
            issues.append("Missing execute_trade method")
        if not hasattr(executor, "update_positions"):
            issues.append("Missing update_positions method")
        if not hasattr(executor, "get_positions_summary"):
            issues.append("Missing get_positions_summary method")

        # Check max positions
        if executor.max_positions <= 0:
            issues.append("Max positions should be > 0")

        return {
            "status": "OK" if not issues else "ISSUE",
            "details": f"PaperExecutor initialized: max_positions={executor.max_positions}, slippage={executor.slippage_pct}%",
            "issues": issues,
        }
    except Exception as e:
        return {"status": "ERROR", "details": f"Failed to import/check PaperExecutor: {e}", "issues": [str(e)]}


def check_pnl_tracker():
    """Check PnLTracker component."""
    issues = []
    try:
        from src.trading.pnl_tracker import PnLTracker

        tracker = PnLTracker()

        # Check initialization
        if not hasattr(tracker, "update"):
            issues.append("Missing update method")
        if not hasattr(tracker, "total_trades"):
            issues.append("Missing total_trades attribute")

        return {"status": "OK" if not issues else "ISSUE", "details": f"PnLTracker initialized", "issues": issues}
    except Exception as e:
        return {"status": "ERROR", "details": f"Failed to import/check PnLTracker: {e}", "issues": [str(e)]}


def check_trade_history_store():
    """Check TradeHistoryStore component."""
    issues = []
    try:
        from src.storage.trade_history import TradeHistoryStore

        store = TradeHistoryStore()

        # Check file paths
        if not hasattr(store, "trades_csv"):
            issues.append("Missing trades_csv path")
        if not hasattr(store, "save_trade"):
            issues.append("Missing save_trade method")
        if not hasattr(store, "save_positions"):
            issues.append("Missing save_positions method")
        if not hasattr(store, "save_pnl"):
            issues.append("Missing save_pnl method")

        return {
            "status": "OK" if not issues else "ISSUE",
            "details": f"TradeHistoryStore initialized: trades_csv={store.trades_csv.name}",
            "issues": issues,
        }
    except Exception as e:
        return {"status": "ERROR", "details": f"Failed to import/check TradeHistoryStore: {e}", "issues": [str(e)]}


def check_integration():
    """Check integration in run_live_chain.py."""
    issues = []
    try:
        from scripts.run_live_chain import LiveChainRunner

        # Check if components are initialized
        runner_code = Path(ROOT_DIR / "scripts" / "run_live_chain.py").read_text()

        if "self.paper_executor" not in runner_code:
            issues.append("PaperExecutor not initialized in LiveChainRunner")
        if "self.pnl_tracker" not in runner_code:
            issues.append("PnLTracker not initialized in LiveChainRunner")
        if "self.trade_history_store" not in runner_code:
            issues.append("TradeHistoryStore not initialized in LiveChainRunner")

        # Check if execute_trade is called
        if "paper_executor.execute_trade" not in runner_code:
            issues.append("execute_trade not called in run_cycle")

        # Check if update_positions is called
        if "paper_executor.update_positions" not in runner_code:
            issues.append("update_positions not called in run_cycle")

        # Check if PnL is updated
        if "pnl_tracker.update" not in runner_code:
            issues.append("PnL tracker update not called in run_cycle")

        # Check if trades are saved
        if "trade_history_store.save_trade" not in runner_code:
            issues.append("Trade save not called in run_cycle")

        return {
            "status": "OK" if not issues else "ISSUE",
            "details": f"Integration check: {len(issues)} issues found",
            "issues": issues,
        }
    except Exception as e:
        return {"status": "ERROR", "details": f"Failed to check integration: {e}", "issues": [str(e)]}


def check_output_files():
    """Check if output files are being generated."""
    issues = []
    outputs_dir = ROOT_DIR / "outputs"

    # Check PnL file
    pnl_file = outputs_dir / "pnl_live.json"
    if pnl_file.exists():
        try:
            pnl = json.load(open(pnl_file))
            required_keys = ["total_pnl", "total_realized_pnl", "total_unrealized_pnl", "total_trades"]
            for key in required_keys:
                if key not in pnl:
                    issues.append(f"PnL file missing key: {key}")
        except Exception as e:
            issues.append(f"PnL file invalid: {e}")
    else:
        issues.append("PnL file not found (may be normal if no trades yet)")

    # Check trades CSV
    trades_file = outputs_dir / "paper_trades_live.csv"
    if trades_file.exists():
        try:
            df = pd.read_csv(trades_file)
            # Check for key columns (may have different names)
            has_action = "action" in df.columns
            has_underlying = "underlying" in df.columns
            has_price = "price" in df.columns or "entry_price" in df.columns
            has_timestamp = "timestamp" in df.columns or "time_ist" in df.columns

            if not has_action:
                issues.append("Trades CSV missing 'action' column")
            if not has_underlying:
                issues.append("Trades CSV missing 'underlying' column")
            if not has_price:
                issues.append("Trades CSV missing price column (price or entry_price)")
            if not has_timestamp:
                issues.append("Trades CSV missing timestamp column (timestamp or time_ist)")
        except Exception as e:
            issues.append(f"Trades CSV invalid: {e}")

    # Check positions file
    pos_file = outputs_dir / "positions_live.json"
    if pos_file.exists():
        try:
            pos = json.load(open(pos_file))
            if "open_positions" not in pos:
                issues.append("Positions file missing 'open_positions' key")
        except Exception as e:
            issues.append(f"Positions file invalid: {e}")

    return {
        "status": "OK" if len(issues) == 0 else "ISSUE",
        "details": f"Output files check: {len(issues)} issues",
        "issues": issues,
    }


def check_data_flow():
    """Check if data flows correctly through the system."""
    issues = []

    # Check if replay engine generates data
    try:
        from src.sim.replay_engine import ReplayEngine

        replay = ReplayEngine()
        if not hasattr(replay, "generate_snapshot"):
            issues.append("ReplayEngine missing generate_snapshot method")
    except Exception as e:
        issues.append(f"ReplayEngine check failed: {e}")

    # Check if live chain runner processes data
    runner_code = Path(ROOT_DIR / "scripts" / "run_live_chain.py").read_text()
    if "run_cycle" not in runner_code:
        issues.append("LiveChainRunner missing run_cycle method")

    return {
        "status": "OK" if len(issues) == 0 else "ISSUE",
        "details": f"Data flow check: {len(issues)} issues",
        "issues": issues,
    }


def check_automation():
    """Check if everything is automated."""
    issues = []

    # Check if START_PAPER_TRADING.bat exists
    batch_file = ROOT_DIR / "START_PAPER_TRADING.bat"
    if not batch_file.exists():
        issues.append("START_PAPER_TRADING.bat not found")

    # Check if replay_test can run automatically
    replay_test = ROOT_DIR / "scripts" / "replay_test.py"
    if not replay_test.exists():
        issues.append("replay_test.py not found")

    return {
        "status": "OK" if len(issues) == 0 else "ISSUE",
        "details": f"Automation check: {len(issues)} issues",
        "issues": issues,
    }


def main():
    """Run all checks."""
    print("\n" + "=" * 80)
    print("  COMPREHENSIVE PAPER TRADING SYSTEM CHECK")
    print("=" * 80 + "\n")

    checks = [
        ("PaperExecutor", check_paper_executor),
        ("PnLTracker", check_pnl_tracker),
        ("TradeHistoryStore", check_trade_history_store),
        ("Integration", check_integration),
        ("Output Files", check_output_files),
        ("Data Flow", check_data_flow),
        ("Automation", check_automation),
    ]

    results = []
    total_issues = 0

    for name, check_func in checks:
        result = check_component(name, check_func)
        results.append(result)
        total_issues += len(result["issues"])

    # Print results
    for result in results:
        status_symbol = "[OK]" if result["status"] == "OK" else "[ISSUE]" if result["status"] == "ISSUE" else "[ERROR]"
        print(f"{status_symbol} {result['component']}")
        print(f"    {result['details']}")
        if result["issues"]:
            for issue in result["issues"]:
                print(f"      - {issue}")
        print()

    # Summary
    print("=" * 80)
    if total_issues == 0:
        print("  RESULT: [OK] ALL CHECKS PASSED - SYSTEM READY")
    else:
        print(f"  RESULT: [WARNING] {total_issues} ISSUES FOUND")
        print("  Review issues above and fix if needed")
    print("=" * 80 + "\n")

    return total_issues == 0


if __name__ == "__main__":
    main()
