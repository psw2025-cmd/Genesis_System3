"""
Show Full Orchestra - Complete System Demonstration
Displays all components working together in real-time
"""

import sys
from pathlib import Path
import json
from datetime import datetime
import pandas as pd

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.trading.advanced_position_sizing import AdvancedPositionSizing
from src.trading.dynamic_risk_management import DynamicRiskManager
from src.selector.strategy_engine import StrategyEngine
from src.trading.paper_executor import PaperExecutor
from src.trading.pnl_tracker import PnLTracker
from src.storage.trade_history import TradeHistoryStore


def show_full_orchestra():
    """Display complete system working together."""
    print("=" * 80)
    print("  FULL ORCHESTRA - COMPLETE SYSTEM DEMONSTRATION")
    print("=" * 80)

    # Initialize all components
    print("\n[1] Initializing Components...")
    print("-" * 80)

    sizing = AdvancedPositionSizing()
    print(f"  [OK] Position Sizing: Kelly={sizing.kelly_fraction}, Max Risk={sizing.max_risk_per_trade_pct}%")

    risk_mgr = DynamicRiskManager()
    print(f"  [OK] Risk Management: ATR={risk_mgr.atr_multiplier}x, Fixed TP={risk_mgr.fixed_take_profit_pct*100}%")

    strategy = StrategyEngine()
    print(
        f"  [OK] Strategy Engine: Min Confidence={strategy.min_confidence}, Min Liquidity={strategy.min_liquidity_score}"
    )

    executor = PaperExecutor()
    print(f"  [OK] Paper Executor: Initialized")

    tracker = PnLTracker()
    print(f"  [OK] PnL Tracker: Initialized")

    history = TradeHistoryStore()
    print(f"  [OK] Trade History: Initialized")

    # Show configuration
    print("\n[2] System Configuration...")
    print("-" * 80)
    print(f"  Capital: Rs {sizing.capital:,.2f}")
    print(f"  Max Risk Per Trade: {sizing.max_risk_per_trade_pct}%")
    print(f"  Max Total Risk: {sizing.max_total_risk_pct}%")
    print(f"  Stop Loss: {risk_mgr.atr_multiplier}x ATR")
    print(f"  Take Profit: {risk_mgr.fixed_take_profit_pct*100}%")

    # Show current status
    print("\n[3] Current System Status...")
    print("-" * 80)

    # Check PnL
    pnl_path = ROOT_DIR / "outputs" / "pnl_live.json"
    if pnl_path.exists():
        with open(pnl_path, "r") as f:
            pnl_data = json.load(f)
        print(f"  Total PnL: Rs {pnl_data.get('total_pnl', 0):,.2f}")
        print(f"  Total Trades: {pnl_data.get('total_trades', 0)}")
        print(f"  Win Rate: {pnl_data.get('win_rate', 0):.2f}%")
        print(f"  Open Positions: {pnl_data.get('open_positions', 0)}")
    else:
        print("  No PnL data found (system not running)")

    # Check positions
    positions_path = ROOT_DIR / "outputs" / "positions_live.json"
    if positions_path.exists():
        with open(positions_path, "r") as f:
            positions = json.load(f)
        open_count = len([p for p in positions.values() if p.get("status") == "OPEN"])
        print(f"  Open Positions: {open_count}")
    else:
        print("  No positions data found")

    # Check trade history
    trades_path = ROOT_DIR / "outputs" / "paper_trades_live.csv"
    if trades_path.exists():
        try:
            df = pd.read_csv(trades_path, on_bad_lines="skip", engine="python")
            print(f"  Total Trade Records: {len(df)}")
            if len(df) > 0:
                print(f"  Latest Trade: {df.iloc[-1].get('symbol', 'N/A') if 'symbol' in df.columns else 'N/A'}")
        except:
            print("  Trade history file exists but could not be read")
    else:
        print("  No trade history found")

    # Check option chain data
    chain_path = ROOT_DIR / "outputs" / "chain_raw_live.csv"
    if chain_path.exists():
        try:
            df = pd.read_csv(chain_path, on_bad_lines="skip", engine="python", nrows=1)
            print(f"  Option Chain Data: Available")
            print(f"  Columns: {len(df.columns)}")
        except:
            print("  Option chain file exists but could not be read")
    else:
        print("  No option chain data found")

    # Check Excel file
    excel_path = ROOT_DIR / "outputs" / "OptionChain_Master_v3_AI_FINAL.xlsx"
    if excel_path.exists():
        size_mb = excel_path.stat().st_size / (1024 * 1024)
        print(f"  Excel Master File: {size_mb:.2f} MB")
    else:
        print("  Excel Master File: Not found")

    # Show test results
    print("\n[4] System Test Results...")
    print("-" * 80)

    test_report = ROOT_DIR / "outputs" / "comprehensive_10k_test_report.json"
    if test_report.exists():
        with open(test_report, "r") as f:
            test_data = json.load(f)
        print(f"  Total Tests: {test_data.get('total_tests', 0):,}")
        print(f"  Passed: {test_data.get('total_passed', 0):,}")
        print(f"  Failed: {test_data.get('total_failed', 0):,}")
        print(f"  Pass Rate: {test_data.get('pass_rate', 0):.2f}%")
    else:
        print("  No test results found")

    # Show how to run
    print("\n[5] How to Run Full System...")
    print("-" * 80)
    print("  Option 1: Start Paper Trading (Full Simulation)")
    print("    Command: START_PAPER_TRADING_COMPLETE.bat")
    print("    Description: Runs complete paper trading with virtual market")
    print()
    print("  Option 2: Update Option Chain Master")
    print("    Command: UPDATE_OPTIONCHAIN_MASTER.bat")
    print("    Description: Fetches latest data and builds Excel file")
    print()
    print("  Option 3: Monitor Performance")
    print("    Command: MONITOR_OPTIONCHAIN.bat")
    print("    Description: Monitors Excel file status and performance")
    print()
    print("  Option 4: Run Complete Tests")
    print("    Command: RUN_10K_TEST_SUITE.bat")
    print("    Description: Runs comprehensive test suite")

    # Show file locations
    print("\n[6] Key File Locations...")
    print("-" * 80)
    print(f"  Config: {ROOT_DIR / 'config' / '.env'}")
    print(f"  Logs: {ROOT_DIR / 'logs'}")
    print(f"  Outputs: {ROOT_DIR / 'outputs'}")
    print(f"  Excel: {ROOT_DIR / 'outputs' / 'OptionChain_Master_v3_AI_FINAL.xlsx'}")
    print(f"  PnL: {ROOT_DIR / 'outputs' / 'pnl_live.json'}")
    print(f"  Positions: {ROOT_DIR / 'outputs' / 'positions_live.json'}")
    print(f"  Trades: {ROOT_DIR / 'outputs' / 'paper_trades_live.csv'}")

    print("\n" + "=" * 80)
    print("  FULL ORCHESTRA STATUS: READY")
    print("=" * 80)


if __name__ == "__main__":
    show_full_orchestra()
