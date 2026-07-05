"""
Market Calendar - Holiday Detection and Market Hours Intelligence

Provides market state detection including holidays, weekends, and special trading days.
"""

import logging
from datetime import date, datetime
from datetime import time as dt_time
from datetime import timedelta
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Indian NSE Holiday Calendar 2025 (add more as needed)
NSE_HOLIDAYS_2025 = [
    date(2025, 1, 26),  # Republic Day
    date(2025, 3, 14),  # Holi
    date(2025, 3, 31),  # Id-Ul-Fitr
    date(2025, 4, 10),  # Mahavir Jayanti
    date(2025, 4, 14),  # Dr. Ambedkar Jayanti
    date(2025, 4, 18),  # Good Friday
    date(2025, 5, 1),  # Maharashtra Day
    date(2025, 8, 15),  # Independence Day
    date(2025, 8, 27),  # Ganesh Chaturthi
    date(2025, 10, 2),  # Mahatma Gandhi Jayanti
    date(2025, 10, 20),  # Dussehra
    date(2025, 11, 5),  # Diwali Laxmi Pujan
    date(2025, 11, 6),  # Diwali Balipratipada
    date(2025, 11, 24),  # Gurunanak Jayanti
    date(2025, 12, 25),  # Christmas
]

# Market hours (IST)
MARKET_OPEN = dt_time(9, 15)
MARKET_CLOSE = dt_time(15, 30)
PRE_MARKET_START = dt_time(7, 0)
POST_MARKET_END = dt_time(18, 0)


class MarketState:
    """Market state enumeration"""

    CLOSED_WEEKEND = "CLOSED_WEEKEND"
    CLOSED_HOLIDAY = "CLOSED_HOLIDAY"
    PRE_MARKET = "PRE_MARKET"
    LIVE_MARKET = "LIVE_MARKET"
    POST_MARKET = "POST_MARKET"
    CLOSED_NIGHT = "CLOSED_NIGHT"


def is_trading_holiday(check_date: Optional[date] = None) -> bool:
    """Check if given date is a trading holiday."""
    if check_date is None:
        check_date = datetime.now().date()
    return check_date in NSE_HOLIDAYS_2025


def is_weekend(check_date: Optional[date] = None) -> bool:
    """Check if given date is weekend (Saturday=5, Sunday=6)."""
    if check_date is None:
        check_date = datetime.now().date()
    return check_date.weekday() >= 5


def get_market_state(check_time: Optional[datetime] = None) -> Tuple[str, str]:
    """
    Get current market state.

    Returns:
        Tuple of (state, description)
    """
    if check_time is None:
        check_time = datetime.now()

    check_date = check_time.date()
    current_time = check_time.time()

    # Check weekend
    if is_weekend(check_date):
        return MarketState.CLOSED_WEEKEND, f"Market closed (Weekend - {check_time.strftime('%A')})"

    # Check holiday
    if is_trading_holiday(check_date):
        return MarketState.CLOSED_HOLIDAY, "Market closed (Trading Holiday)"

    # Check time of day
    if current_time < PRE_MARKET_START:
        return MarketState.CLOSED_NIGHT, "Market closed (Before pre-market)"
    elif current_time < MARKET_OPEN:
        return MarketState.PRE_MARKET, "Pre-market period"
    elif current_time < MARKET_CLOSE:
        return MarketState.LIVE_MARKET, "Market open (Live trading)"
    elif current_time < POST_MARKET_END:
        return MarketState.POST_MARKET, "Post-market period"
    else:
        return MarketState.CLOSED_NIGHT, "Market closed (After hours)"


def should_run_autopilot(check_time: Optional[datetime] = None) -> Tuple[bool, str]:
    """
    Determine if autopilot should be running.

    Returns:
        Tuple of (should_run, reason)
    """
    state, description = get_market_state(check_time)

    if state in [MarketState.CLOSED_WEEKEND, MarketState.CLOSED_HOLIDAY]:
        return False, description

    if state == MarketState.LIVE_MARKET:
        return True, "Market is live - autopilot should run"

    if state == MarketState.PRE_MARKET:
        return False, "Pre-market - autopilot waits for 9:15 AM"

    return False, description


def get_next_market_open() -> datetime:
    """Get the next market open time."""
    now = datetime.now()
    check_date = now.date()

    # If we're before market open today and it's a trading day
    if now.time() < MARKET_OPEN and not is_weekend(check_date) and not is_trading_holiday(check_date):
        return datetime.combine(check_date, MARKET_OPEN)

    # Otherwise, check next days
    for days_ahead in range(1, 8):  # Check up to 7 days ahead
        next_date = check_date + timedelta(days=days_ahead)
        if not is_weekend(next_date) and not is_trading_holiday(next_date):
            return datetime.combine(next_date, MARKET_OPEN)

    # Fallback - should never reach here unless all days ahead are holidays
    return datetime.combine(check_date + timedelta(days=7), MARKET_OPEN)


if __name__ == "__main__":
    from datetime import timedelta

    # Test current state
    state, desc = get_market_state()
    print(f"Current State: {state}")
    print(f"Description: {desc}")

    should_run, reason = should_run_autopilot()
    print(f"\nShould run autopilot: {should_run}")
    print(f"Reason: {reason}")

    next_open = get_next_market_open()
    print(f"\nNext market open: {next_open.strftime('%Y-%m-%d %H:%M:%S %A')}")

    # Test various scenarios
    print("\n" + "=" * 60)
    print("Testing various times:")
    print("=" * 60)

    test_times = [
        datetime(2025, 12, 8, 8, 0),  # Pre-market
        datetime(2025, 12, 8, 9, 30),  # Market open
        datetime(2025, 12, 8, 15, 0),  # Market close
        datetime(2025, 12, 8, 16, 0),  # Post-market
        datetime(2025, 12, 7, 10, 0),  # Saturday
        datetime(2025, 1, 26, 10, 0),  # Holiday (Republic Day)
    ]

    for test_time in test_times:
        state, desc = get_market_state(test_time)
        print(f"{test_time.strftime('%Y-%m-%d %H:%M %A')}: {state} - {desc}")
