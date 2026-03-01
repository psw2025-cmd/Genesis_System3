"""
Market Hours Detection for Indian Stock Market
"""
from datetime import datetime, time, timedelta, date
import pytz
from typing import Optional, Tuple, List


IST = pytz.timezone('Asia/Kolkata')

# Market hours (IST)
MARKET_OPEN = time(9, 15)  # 9:15 AM
MARKET_CLOSE = time(15, 30)  # 3:30 PM
PRE_MARKET_START = time(9, 0)  # 9:00 AM (pre-market window)

# Special trading days (when market is open on weekends/holidays)
# Format: (year, month, day) - Add special trading days here
SPECIAL_TRADING_DAYS: List[date] = [
    date(2026, 2, 1),  # Budget Day 2026 (Sunday)
    # Add more special trading days as needed
    # date(2026, 3, 15),  # Example: Another special trading day
]


def is_market_open(now_ist: Optional[datetime] = None) -> Tuple[bool, str]:
    """
    Check if market is open.
    
    Args:
        now_ist: Current time in IST (default: now)
    
    Returns:
        Tuple of (is_open, reason)
    """
    if now_ist is None:
        now_ist = datetime.now(IST)
    elif now_ist.tzinfo is None:
        now_ist = IST.localize(now_ist)
    else:
        now_ist = now_ist.astimezone(IST)
    
    # Check if today is a special trading day (e.g., Budget Day)
    today_date = now_ist.date()
    is_special_trading_day = today_date in SPECIAL_TRADING_DAYS
    
    # Check day of week (0=Monday, 6=Sunday)
    weekday = now_ist.weekday()
    
    # Allow weekend trading only if it's a special trading day
    if weekday >= 5:  # Saturday (5) or Sunday (6)
        if is_special_trading_day:
            # Special trading day - check time only
            pass  # Continue to time check below
        else:
            return False, f"Market closed: Weekend ({now_ist.strftime('%A')})"
    
    current_time = now_ist.time()
    
    # Check if within market hours (09:15 to 15:30 IST)
    if MARKET_OPEN <= current_time <= MARKET_CLOSE:
        if is_special_trading_day:
            return True, f"Market open (Special Trading Day - {today_date.strftime('%Y-%m-%d')})"
        return True, "Market open"
    
    # Pre-market window (9:00 - 9:15) - market not open yet
    if PRE_MARKET_START <= current_time < MARKET_OPEN:
        return False, "Pre-market window (9:00-9:15 AM) - Market not open"
    
    # After market close
    if current_time > MARKET_CLOSE:
        return False, f"Market closed: After hours (closed at {MARKET_CLOSE.strftime('%H:%M')})"
    
    # Before pre-market
    return False, f"Market closed: Before pre-market (opens at {MARKET_OPEN.strftime('%H:%M')})"


def get_next_market_open(now_ist: Optional[datetime] = None) -> datetime:
    """
    Get next market open time.
    
    Args:
        now_ist: Current time in IST
    
    Returns:
        Next market open datetime
    """
    if now_ist is None:
        now_ist = datetime.now(IST)
    elif now_ist.tzinfo is None:
        now_ist = IST.localize(now_ist)
    else:
        now_ist = now_ist.astimezone(IST)
    
    # If today is weekday and before market close, check if market opens today
    weekday = now_ist.weekday()
    current_time = now_ist.time()
    
    if weekday < 5:  # Monday-Friday
        if current_time < MARKET_OPEN:
            # Market opens today
            next_open = now_ist.replace(hour=MARKET_OPEN.hour, minute=MARKET_OPEN.minute, second=0, microsecond=0)
            if next_open > now_ist:
                return next_open
    
    # Find next weekday
    days_ahead = 1
    while True:
        next_date = now_ist.date() + timedelta(days=days_ahead)
        if next_date.weekday() < 5:  # Monday-Friday
            next_open = IST.localize(datetime.combine(next_date, MARKET_OPEN))
            return next_open
        days_ahead += 1


def get_market_status(now_ist: Optional[datetime] = None) -> dict:
    """
    Get detailed market status.
    
    Args:
        now_ist: Current time in IST
    
    Returns:
        Dict with status information including market_mode: live|closed|preopen
    """
    if now_ist is None:
        now_ist = datetime.now(IST)
    elif now_ist.tzinfo is None:
        now_ist = IST.localize(now_ist)
    else:
        now_ist = now_ist.astimezone(IST)

    is_open, reason = is_market_open(now_ist)
    current_time = now_ist.time()

    # market_mode: live (9:15-15:30), preopen (9:00-9:15), closed (otherwise)
    if MARKET_OPEN <= current_time <= MARKET_CLOSE:
        market_mode = "live"
    elif PRE_MARKET_START <= current_time < MARKET_OPEN:
        market_mode = "preopen"
    else:
        market_mode = "closed"

    result = {
        "is_open": is_open,
        "reason": reason,
        "market_mode": market_mode,
        "current_time_ist": now_ist.strftime('%Y-%m-%d %H:%M:%S IST'),
    }

    if not is_open:
        next_open = get_next_market_open(now_ist)
        result["next_open"] = next_open.strftime('%Y-%m-%d %H:%M:%S IST')
        result["seconds_until_open"] = (next_open - now_ist).total_seconds()

    return result
