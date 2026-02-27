"""
PnL Tracker - Tracks profit/loss for paper trades
"""
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import pandas as pd
import pytz

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.utils.logger import logger


class PnLTracker:
    """
    Tracks profit/loss for paper trades.
    """
    
    def __init__(self):
        """Initialize PnL tracker."""
        ist = pytz.timezone('Asia/Kolkata')
        self.session_start_time = datetime.now(ist)
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_realized_pnl = 0.0
        self.total_unrealized_pnl = 0.0
        self.max_drawdown = 0.0
        self.max_profit = 0.0
        self.peak_equity = 0.0
        self.processed_positions = set()  # Track which positions have been counted
        
    def update(
        self,
        positions_summary: Dict,
        cycle_timestamp: str
    ) -> Dict:
        """
        Update PnL tracking with current positions.
        
        Args:
            positions_summary: Summary from PaperExecutor
            cycle_timestamp: Current cycle timestamp
            
        Returns:
            PnL summary dict
        """
        self.total_unrealized_pnl = positions_summary.get('total_unrealized_pnl', 0.0)
        self.total_realized_pnl = positions_summary.get('total_realized_pnl', 0.0)
        
        # Update trade counts (only count each position once)
        closed = positions_summary.get('closed_positions', [])
        for pos in closed:
            position_id = pos.get('position_id')
            if position_id and position_id not in self.processed_positions:
                self.processed_positions.add(position_id)
                if pos.get('realized_pnl', 0) > 0:
                    self.winning_trades += 1
                elif pos.get('realized_pnl', 0) < 0:
                    self.losing_trades += 1
        
        self.total_trades = self.winning_trades + self.losing_trades
        
        # Calculate win rate
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0.0
        
        # Update drawdown
        total_pnl = self.total_unrealized_pnl + self.total_realized_pnl
        if total_pnl > self.peak_equity:
            self.peak_equity = total_pnl
            self.max_profit = total_pnl
        
        drawdown = self.peak_equity - total_pnl
        if drawdown > self.max_drawdown:
            self.max_drawdown = drawdown
        
        # Calculate average PnL per trade
        avg_pnl = (self.total_realized_pnl / self.total_trades) if self.total_trades > 0 else 0.0
        
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        summary = {
            'timestamp': cycle_timestamp,
            'timestamp_ist': now.strftime('%Y-%m-%d %H:%M:%S IST'),
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': float(win_rate),
            'total_realized_pnl': float(self.total_realized_pnl),
            'total_unrealized_pnl': float(self.total_unrealized_pnl),
            'total_pnl': float(total_pnl),
            'avg_pnl_per_trade': float(avg_pnl),
            'max_profit': float(self.max_profit),
            'max_drawdown': float(self.max_drawdown),
            'open_positions': positions_summary.get('open_count', 0),
            'session_duration_minutes': (now - self.session_start_time).total_seconds() / 60
        }
        
        # Save to CSV (for PAPER_PNL_TRACKER requirement)
        try:
            import sys
            from pathlib import Path
            ROOT_DIR = Path(__file__).parent.parent.parent
            csv_file = ROOT_DIR / "outputs" / "paper_pnl.csv"
            
            # Append row to CSV
            csv_row = {
                'timestamp': summary['timestamp_ist'],
                'total_trades': summary['total_trades'],
                'winning_trades': summary['winning_trades'],
                'losing_trades': summary['losing_trades'],
                'win_rate': summary['win_rate'],
                'total_realized_pnl': summary['total_realized_pnl'],
                'total_unrealized_pnl': summary['total_unrealized_pnl'],
                'total_pnl': summary['total_pnl'],
                'avg_pnl_per_trade': summary['avg_pnl_per_trade'],
                'max_profit': summary['max_profit'],
                'max_drawdown': summary['max_drawdown'],
                'open_positions': summary['open_positions']
            }
            
            # Create DataFrame and append
            import pandas as pd
            df_row = pd.DataFrame([csv_row])
            
            # Append to CSV (create if doesn't exist)
            if csv_file.exists():
                df_row.to_csv(csv_file, mode='a', header=False, index=False)
            else:
                df_row.to_csv(csv_file, mode='w', header=True, index=False)
        except Exception as e:
            logger.error(f"Failed to save PnL CSV: {e}")
        
        # Save summary JSON
        try:
            import sys
            from pathlib import Path
            import json
            ROOT_DIR = Path(__file__).parent.parent.parent
            summary_file = ROOT_DIR / "outputs" / "paper_pnl_summary.json"
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save PnL summary: {e}")
        
        return summary
