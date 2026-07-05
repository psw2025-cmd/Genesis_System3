"""
Find and Fix Zero Value Issues
Identifies why PnL, trades, etc. are showing 0
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pytz

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.trading.advanced_position_sizing import AdvancedPositionSizing
from src.trading.paper_executor import PaperExecutor
from src.trading.pnl_tracker import PnLTracker


class ZeroValueIssueFinder:
    """Find and fix zero value issues."""

    def __init__(self):
        self.ist = pytz.timezone("Asia/Kolkata")
        self.issues = []

    def test_paper_executor_quantity(self):
        """Test why quantity is 0."""
        print("\n[ISSUE 1] Testing Paper Executor Quantity")
        print("-" * 80)

        executor = PaperExecutor()

        # Create valid trade signal
        trade_signal = {
            "action": "TRADE",
            "strategy": "BUY_CE",
            "underlying": "NIFTY",
            "tokens": ["12345"],
            "strikes": [25000],
            "entry_mid": 100.0,
        }

        # Create valid market data
        current_data = pd.DataFrame(
            {
                "token": ["12345"],
                "symbol": ["NIFTY24FEB2625000CE"],
                "strike": [25000],
                "option_type": ["CE"],
                "ltp": [100.0],
                "mid_price": [100.0],
                "bidPrice": [99.5],
                "offerPrice": [100.5],
                "volume": [10000],
                "oi": [100000],
            }
        )

        position = executor.execute_trade(
            trade_signal, current_data, datetime.now(self.ist).strftime("%Y-%m-%d %H:%M:%S IST")
        )

        print(f"  Position Created: {position is not None}")
        if position:
            print(f"  Quantity: {position.get('quantity', 'N/A')}")
            print(f"  Entry Price: {position.get('entry_price', 'N/A')}")
            print(f"  Position ID: {position.get('position_id', 'N/A')}")

            if position.get("quantity", 0) == 0:
                self.issues.append(
                    {
                        "issue": "Paper Executor returning quantity=0",
                        "position": position,
                        "fix": "Check position sizing calculation",
                    }
                )
                print("  PROBLEM: Quantity is 0!")

                # Check position sizing
                sizing = AdvancedPositionSizing()
                size_result = sizing.calculate_optimal_size(
                    entry_price=100.0, stop_loss_price=96.0, confidence=0.8, iv=0.20
                )
                print(f"  Position Sizing Result: {size_result}")

                if size_result["quantity"] > 0:
                    print("  FIX: Position sizing works, issue in executor")
                else:
                    print("  FIX: Position sizing also returns 0")
            else:
                print("  OK: Quantity > 0")
        else:
            print("  PROBLEM: No position created!")
            self.issues.append({"issue": "Paper Executor not creating position", "fix": "Check executor logic"})

    def test_pnl_tracker(self):
        """Test why PnL is 0."""
        print("\n[ISSUE 2] Testing PnL Tracker")
        print("-" * 80)

        executor = PaperExecutor()
        tracker = PnLTracker()

        # Create and execute trade
        trade_signal = {
            "action": "TRADE",
            "strategy": "BUY_CE",
            "underlying": "NIFTY",
            "tokens": ["12345"],
            "strikes": [25000],
            "entry_mid": 100.0,
        }

        current_data = pd.DataFrame(
            {
                "token": ["12345"],
                "symbol": ["NIFTY24FEB2625000CE"],
                "strike": [25000],
                "option_type": ["CE"],
                "ltp": [100.0],
                "mid_price": [100.0],
                "bidPrice": [99.5],
                "offerPrice": [100.5],
                "volume": [10000],
                "oi": [100000],
            }
        )

        position = executor.execute_trade(
            trade_signal, current_data, datetime.now(self.ist).strftime("%Y-%m-%d %H:%M:%S IST")
        )

        print(f"  Positions: {len(executor.positions)}")
        print(f"  Position Details: {executor.positions}")

        # Get positions summary
        positions_summary = executor.get_positions_summary()
        print(f"  Positions Summary: {positions_summary}")

        # Update PnL
        pnl_data = tracker.update(positions_summary, datetime.now(self.ist).isoformat())

        print(f"  PnL Data: {pnl_data}")

        if pnl_data:
            total_pnl = pnl_data.get("total_pnl", 0)
            print(f"  Total PnL: {total_pnl}")

            if total_pnl == 0:
                self.issues.append(
                    {
                        "issue": "PnL Tracker returning 0",
                        "pnl_data": pnl_data,
                        "positions": executor.positions,
                        "fix": "Check PnL calculation logic",
                    }
                )
                print("  PROBLEM: Total PnL is 0!")

                # Check if positions have current_price
                for pos_id, pos in executor.positions.items():
                    print(f"    Position {pos_id}:")
                    print(f"      Entry: {pos.get('entry_price', 'N/A')}")
                    print(f"      Current: {pos.get('current_price', 'N/A')}")
                    print(f"      Quantity: {pos.get('quantity', 'N/A')}")
            else:
                print("  OK: PnL > 0")
        else:
            print("  PROBLEM: No PnL data!")
            self.issues.append({"issue": "PnL Tracker returning None", "fix": "Check tracker logic"})

    def find_all_issues(self):
        """Find all zero value issues."""
        print("=" * 80)
        print("  FINDING ZERO VALUE ISSUES")
        print("=" * 80)

        self.test_paper_executor_quantity()
        self.test_pnl_tracker()

        # Summary
        print("\n" + "=" * 80)
        print("  ISSUE SUMMARY")
        print("=" * 80)

        if self.issues:
            print(f"\nFound {len(self.issues)} issues:")
            for i, issue in enumerate(self.issues, 1):
                print(f"\n{i}. {issue['issue']}")
                print(f"   Fix: {issue.get('fix', 'N/A')}")
        else:
            print("\nNo issues found!")

        # Save report
        report_path = ROOT_DIR / "outputs" / "zero_value_issues_report.json"
        with open(report_path, "w") as f:
            json.dump(self.issues, f, indent=2, default=str)

        print(f"\n\nReport saved to: {report_path}")

        return len(self.issues)


def main():
    """Main execution."""
    finder = ZeroValueIssueFinder()
    issue_count = finder.find_all_issues()
    return issue_count


if __name__ == "__main__":
    sys.exit(main())
