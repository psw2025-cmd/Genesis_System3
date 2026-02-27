"""
Real-Time Monitoring Dashboard for Option Chain Automation System
===================================================================

This script provides real-time monitoring of the option chain automation system:
- System status and health
- Data fetch statistics
- Trading performance
- Position tracking
- PnL monitoring
- Error tracking
- Alert generation

Run: python monitor_option_chain_system.py
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import json
import time
from typing import Dict, Any, Optional
import pandas as pd

ROOT_DIR = Path(__file__).parent.absolute()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.live import Live
    from rich.layout import Layout
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Warning: 'rich' library not available. Install with: pip install rich")
    print("Falling back to simple text output.")


class OptionChainMonitor:
    """Real-time monitor for option chain automation system."""
    
    def __init__(self, refresh_interval: int = 5):
        """
        Initialize monitor.
        
        Args:
            refresh_interval: Refresh interval in seconds
        """
        self.refresh_interval = refresh_interval
        self.output_dir = ROOT_DIR / "outputs"
        self.console = Console() if RICH_AVAILABLE else None
        
    def load_status(self) -> Optional[Dict]:
        """Load system status from file."""
        status_file = self.output_dir / "system_status.json"
        if status_file.exists():
            try:
                with open(status_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading status: {e}")
        return None
    
    def load_health(self) -> Optional[Dict]:
        """Load health check data."""
        health_file = self.output_dir / "health_check.json"
        if health_file.exists():
            try:
                with open(health_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading health: {e}")
        return None
    
    def load_positions(self) -> Optional[Dict]:
        """Load current positions."""
        positions_file = self.output_dir / "positions_live.json"
        if positions_file.exists():
            try:
                with open(positions_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading positions: {e}")
        return None
    
    def load_pnl(self) -> Optional[Dict]:
        """Load PnL data."""
        pnl_file = self.output_dir / "pnl_live.json"
        if pnl_file.exists():
            try:
                with open(pnl_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading PnL: {e}")
        return None
    
    def format_status_table(self, status: Dict) -> str:
        """Format status as table."""
        if RICH_AVAILABLE:
            table = Table(title="System Status", show_header=True, header_style="bold magenta")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Running", "✅ Yes" if status.get('is_running') else "❌ No")
            table.add_row("Connected", "✅ Yes" if status.get('is_connected') else "❌ No")
            table.add_row("Total Cycles", str(status.get('total_cycles', 0)))
            table.add_row("Successful Fetches", str(status.get('successful_fetches', 0)))
            table.add_row("Failed Fetches", str(status.get('failed_fetches', 0)))
            table.add_row("Signals Generated", str(status.get('signals_generated', 0)))
            table.add_row("Trades Executed", str(status.get('trades_executed', 0)))
            table.add_row("Current Positions", str(status.get('current_positions', 0)))
            table.add_row("Total PnL", f"₹{status.get('total_pnl', 0):.2f}")
            table.add_row("Daily PnL", f"₹{status.get('daily_pnl', 0):.2f}")
            
            if status.get('last_data_fetch'):
                table.add_row("Last Data Fetch", status['last_data_fetch'])
            if status.get('last_signal_generated'):
                table.add_row("Last Signal", status['last_signal_generated'])
            if status.get('last_trade_executed'):
                table.add_row("Last Trade", status['last_trade_executed'])
            
            return table
        else:
            # Simple text output
            lines = [
                "=" * 60,
                "SYSTEM STATUS",
                "=" * 60,
                f"Running: {'Yes' if status.get('is_running') else 'No'}",
                f"Connected: {'Yes' if status.get('is_connected') else 'No'}",
                f"Total Cycles: {status.get('total_cycles', 0)}",
                f"Successful Fetches: {status.get('successful_fetches', 0)}",
                f"Failed Fetches: {status.get('failed_fetches', 0)}",
                f"Signals Generated: {status.get('signals_generated', 0)}",
                f"Trades Executed: {status.get('trades_executed', 0)}",
                f"Current Positions: {status.get('current_positions', 0)}",
                f"Total PnL: ₹{status.get('total_pnl', 0):.2f}",
                f"Daily PnL: ₹{status.get('daily_pnl', 0):.2f}",
            ]
            if status.get('last_data_fetch'):
                lines.append(f"Last Data Fetch: {status['last_data_fetch']}")
            return "\n".join(lines)
    
    def format_positions_table(self, positions: Dict) -> str:
        """Format positions as table."""
        if RICH_AVAILABLE:
            table = Table(title="Current Positions", show_header=True, header_style="bold blue")
            table.add_column("Position ID", style="cyan")
            table.add_column("Underlying", style="green")
            table.add_column("Symbol", style="yellow")
            table.add_column("Entry Price", style="magenta")
            table.add_column("Quantity", style="cyan")
            table.add_column("PnL", style="green")
            
            if isinstance(positions, dict):
                for pos_id, pos_data in positions.items():
                    if isinstance(pos_data, dict):
                        table.add_row(
                            str(pos_id),
                            str(pos_data.get('underlying', 'N/A')),
                            str(pos_data.get('symbol', 'N/A')),
                            f"₹{pos_data.get('entry_price', 0):.2f}",
                            str(pos_data.get('qty', 0)),
                            f"₹{pos_data.get('unrealized_pnl', 0):.2f}"
                        )
            
            return table
        else:
            lines = ["=" * 60, "CURRENT POSITIONS", "=" * 60]
            if isinstance(positions, dict):
                for pos_id, pos_data in positions.items():
                    if isinstance(pos_data, dict):
                        lines.append(f"{pos_id}: {pos_data.get('underlying', 'N/A')} - "
                                   f"Entry: ₹{pos_data.get('entry_price', 0):.2f}, "
                                   f"Qty: {pos_data.get('qty', 0)}, "
                                   f"PnL: ₹{pos_data.get('unrealized_pnl', 0):.2f}")
            return "\n".join(lines)
    
    def format_health_panel(self, health: Dict) -> str:
        """Format health check as panel."""
        if RICH_AVAILABLE:
            success_rate = health.get('success_rate', 0)
            health_status = "✅ Healthy" if success_rate > 80 else "⚠️ Degraded" if success_rate > 50 else "❌ Unhealthy"
            
            content = f"""
Status: {health_status}
Success Rate: {success_rate:.1f}%
Total Cycles: {health.get('total_cycles', 0)}
Current Positions: {health.get('current_positions', 0)}
Total PnL: ₹{health.get('total_pnl', 0):.2f}
Daily PnL: ₹{health.get('daily_pnl', 0):.2f}
"""
            return Panel(content, title="Health Check", border_style="green")
        else:
            success_rate = health.get('success_rate', 0)
            health_status = "Healthy" if success_rate > 80 else "Degraded" if success_rate > 50 else "Unhealthy"
            return f"""
{'=' * 60}
HEALTH CHECK
{'=' * 60}
Status: {health_status}
Success Rate: {success_rate:.1f}%
Total Cycles: {health.get('total_cycles', 0)}
Current Positions: {health.get('current_positions', 0)}
Total PnL: ₹{health.get('total_pnl', 0):.2f}
Daily PnL: ₹{health.get('daily_pnl', 0):.2f}
"""
    
    def display(self):
        """Display monitoring dashboard."""
        if RICH_AVAILABLE:
            with Live(console=self.console, refresh_per_second=1/self.refresh_interval) as live:
                while True:
                    try:
                        # Load data
                        status = self.load_status()
                        health = self.load_health()
                        positions = self.load_positions()
                        
                        # Create layout
                        layout = Layout()
                        layout.split_column(
                            Layout(name="header", size=3),
                            Layout(name="main"),
                            Layout(name="footer", size=3)
                        )
                        
                        layout["main"].split_row(
                            Layout(name="status"),
                            Layout(name="positions")
                        )
                        
                        # Header
                        layout["header"].update(Panel(
                            "[bold cyan]Option Chain Automation System - Real-Time Monitor[/bold cyan]",
                            border_style="blue"
                        ))
                        
                        # Status
                        if status:
                            layout["status"].update(self.format_status_table(status))
                        else:
                            layout["status"].update(Panel("No status data available", border_style="red"))
                        
                        # Positions
                        if positions:
                            layout["positions"].update(self.format_positions_table(positions))
                        else:
                            layout["positions"].update(Panel("No positions", border_style="yellow"))
                        
                        # Footer
                        if health:
                            layout["footer"].update(self.format_health_panel(health))
                        else:
                            layout["footer"].update(Panel("No health data", border_style="yellow"))
                        
                        live.update(layout)
                        time.sleep(self.refresh_interval)
                        
                    except KeyboardInterrupt:
                        break
                    except Exception as e:
                        self.console.print(f"[red]Error: {e}[/red]")
                        time.sleep(self.refresh_interval)
        else:
            # Simple text output
            while True:
                try:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    
                    status = self.load_status()
                    health = self.load_health()
                    positions = self.load_positions()
                    
                    print("\n" + "=" * 80)
                    print("OPTION CHAIN AUTOMATION SYSTEM - REAL-TIME MONITOR")
                    print("=" * 80)
                    print(f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    
                    if status:
                        print(self.format_status_table(status))
                        print()
                    
                    if health:
                        print(self.format_health_panel(health))
                        print()
                    
                    if positions:
                        print(self.format_positions_table(positions))
                        print()
                    
                    print("=" * 80)
                    print("Press Ctrl+C to exit")
                    print("=" * 80)
                    
                    time.sleep(self.refresh_interval)
                    
                except KeyboardInterrupt:
                    print("\n\nExiting monitor...")
                    break
                except Exception as e:
                    print(f"Error: {e}")
                    time.sleep(self.refresh_interval)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Option Chain System Monitor")
    parser.add_argument("--refresh", type=int, default=5, help="Refresh interval in seconds")
    
    args = parser.parse_args()
    
    monitor = OptionChainMonitor(refresh_interval=args.refresh)
    monitor.display()


if __name__ == "__main__":
    main()
