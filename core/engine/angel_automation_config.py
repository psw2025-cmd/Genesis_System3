"""
Angel One Index Options - Automation Configuration

Controls automatic execution of trades and PnL simulation.
"""

from dataclasses import dataclass


@dataclass
class AutomationConfig:
    """Configuration for automated trading pipeline."""

    # Auto-execute trades after trade plan is created
    auto_execute_trades: bool = False  # Set to True to enable auto-execution (DRY RUN only for now)

    # Auto-run PnL simulator periodically
    auto_simulate_pnl: bool = False  # Set to True to auto-simulate PnL every N snapshots

    # How often to run PnL simulation (every N snapshots)
    pnl_sim_interval: int = 10  # Run PnL sim every 10 snapshots

    # Maximum trades per day (safety limit)
    max_trades_per_day: int = 20  # Safety limit

    # Maximum trades per underlying per day
    max_trades_per_underlying_per_day: int = 5  # Safety limit


# Global automation config
AUTOMATION_CONFIG = AutomationConfig()
