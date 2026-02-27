"""
Comprehensive Trade Logger - Logs all trade events with timestamps
"""
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import pytz

ROOT_DIR = Path(__file__).parent.parent.parent
OUTPUTS_DIR = ROOT_DIR / "outputs"
AUDIT_DIR = OUTPUTS_DIR / "audit"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

IST = pytz.timezone('Asia/Kolkata')
EVENT_LOG_FILE = AUDIT_DIR / "event_log.jsonl"
TRADE_LOG_FILE = OUTPUTS_DIR / "trade_execution_log.jsonl"


def log_trade_event(
    event_type: str,
    position_id: Optional[str] = None,
    underlying: Optional[str] = None,
    symbol: Optional[str] = None,
    strike: Optional[float] = None,
    option_type: Optional[str] = None,
    action: Optional[str] = None,
    entry_price: Optional[float] = None,
    exit_price: Optional[float] = None,
    qty: Optional[int] = None,
    pnl: Optional[float] = None,
    strategy: Optional[str] = None,
    exit_reason: Optional[str] = None,
    timestamp: Optional[str] = None,
    **kwargs
):
    """
    Log a trade event to both event log and trade execution log.
    
    Event types:
    - TRADE_EXECUTED: Trade entry executed
    - TRADE_CLOSED: Trade exit executed
    - POSITION_OPENED: Position opened
    - POSITION_CLOSED: Position closed
    """
    if timestamp is None:
        timestamp = datetime.now(IST).isoformat()
    
    time_ist = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')
    
    event = {
        "timestamp": timestamp,
        "time_ist": time_ist,
        "event_type": event_type,
        "position_id": position_id,
        "underlying": underlying,
        "symbol": symbol,
        "strike": strike,
        "option_type": option_type,
        "action": action,
        "entry_price": entry_price,
        "exit_price": exit_price,
        "qty": qty,
        "pnl": pnl,
        "strategy": strategy,
        "exit_reason": exit_reason,
        **kwargs
    }
    
    # Remove None values for cleaner logs
    event = {k: v for k, v in event.items() if v is not None}
    
    # Log to event log
    try:
        with open(EVENT_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event, default=str) + '\n')
    except Exception as e:
        print(f"Failed to write to event log: {e}")
    
    # Log to trade execution log (only trade-related events)
    if event_type in ['TRADE_EXECUTED', 'TRADE_CLOSED', 'POSITION_OPENED', 'POSITION_CLOSED']:
        try:
            with open(TRADE_LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event, default=str) + '\n')
        except Exception as e:
            print(f"Failed to write to trade log: {e}")
    
    return event


def get_trades_by_date(date_str: str, start_time: Optional[str] = None, end_time: Optional[str] = None) -> list:
    """
    Get all trades for a specific date, optionally filtered by time range.
    
    Args:
        date_str: Date in format 'YYYY-MM-DD'
        start_time: Start time in format 'HH:MM' (24-hour, IST)
        end_time: End time in format 'HH:MM' (24-hour, IST)
    
    Returns:
        List of trade events
    """
    trades = []
    
    if not TRADE_LOG_FILE.exists():
        return trades
    
    try:
        with open(TRADE_LOG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        event = json.loads(line)
                        event_time_ist = event.get('time_ist', '')
                        
                        # Check if date matches
                        if date_str in event_time_ist:
                            # Check time range if provided
                            if start_time or end_time:
                                # Extract time from time_ist (format: 'YYYY-MM-DD HH:MM:SS IST')
                                time_part = event_time_ist.split()[1] if len(event_time_ist.split()) > 1 else ''
                                if time_part:
                                    event_hour_min = time_part[:5]  # HH:MM
                                    
                                    if start_time and event_hour_min < start_time:
                                        continue
                                    if end_time and event_hour_min > end_time:
                                        continue
                            
                            trades.append(event)
                    except:
                        continue
    except Exception as e:
        print(f"Error reading trade log: {e}")
    
    return trades


def get_all_trades() -> list:
    """Get all trades from trade execution log."""
    trades = []
    
    if not TRADE_LOG_FILE.exists():
        return trades
    
    try:
        with open(TRADE_LOG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        event = json.loads(line)
                        trades.append(event)
                    except:
                        continue
    except Exception as e:
        print(f"Error reading trade log: {e}")
    
    return trades
