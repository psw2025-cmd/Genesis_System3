"""
NSE/BSE Equity Trading Holiday Calendar
==========================================
Source of truth for "is today an NSE/BSE trading holiday" checks used by
the job scheduler (core/engine/system3_phase82_job_scheduler.py) and any
other code that needs to distinguish "market closed because weekend/
holiday" from "market closed because outside trading hours".

2026 dates sourced from Zerodha's official market-intel holiday calendar
(https://zerodha.com/marketintel/holiday-calendar/), which mirrors NSE's
own circular. Equity/derivatives segment only (excludes MCX-only,
settlement-only holidays, and the special Sunday Nov-08 Muhurat Trading
session, which is a real trading session despite the date).

IMPORTANT: this list must be updated annually. NSE publishes the next
year's calendar in December via circular. There is no reliable free API
for this — Render's worker has outbound internet but NSE's holiday page
is not a stable scrape target for production use, so this is a
maintained static list with provenance per entry, re-verified at need.

If a job runs and the year is not in HOLIDAYS_BY_YEAR, is_trading_holiday
returns False (fail-open to "not a holiday") rather than blocking all
jobs — but logs a warning so the gap is visible, consistent with how
core/engine/system3_phase173_holiday_detection.py's old stub silently
returned False without ever raising a flag.
"""

import logging
from datetime import date

logger = logging.getLogger("nse_holidays")

# NSE + BSE equity/derivatives segment holidays, source: Zerodha market-intel
# holiday calendar (mirrors NSE official circular), fetched 2026-06-30.
HOLIDAYS_BY_YEAR = {
    2026: {
        date(2026, 1, 15): "Municipal Corporation Elections in Maharashtra",
        date(2026, 1, 26): "Republic Day",
        date(2026, 3, 3):  "Holi",
        date(2026, 3, 26): "Shri Ram Navami",
        date(2026, 3, 31): "Shri Mahavir Jayanti",
        date(2026, 4, 3):  "Good Friday",
        date(2026, 4, 14): "Dr. Baba Saheb Ambedkar Jayanti",
        date(2026, 5, 1):  "Maharashtra Day",
        date(2026, 5, 28): "Bakri Eid",
        date(2026, 6, 26): "Moharram",
        date(2026, 9, 14): "Ganesh Chaturthi",
        date(2026, 10, 2): "Mahatma Gandhi Jayanti",
        date(2026, 10, 20): "Dussehra",
        date(2026, 11, 10): "Diwali-Balipratipada",
        date(2026, 11, 24): "Prakash Gurpurb Sri Guru Nanak Dev",
        date(2026, 12, 25): "Christmas",
    },
}


def is_trading_holiday(d: date) -> tuple:
    """
    Returns (is_holiday: bool, reason: str|None).
    Checks ONLY the equity/derivatives holiday list — weekend detection
    is the caller's responsibility (most callers already check
    weekday() < 5 separately, e.g. job scheduler's weekdays_only flag).
    """
    year_map = HOLIDAYS_BY_YEAR.get(d.year)
    if year_map is None:
        logger.warning(
            f"nse_holidays: no holiday calendar loaded for year {d.year} — "
            f"treating as non-holiday by default. Update HOLIDAYS_BY_YEAR "
            f"in core/utils/nse_holidays.py with next year's NSE circular."
        )
        return False, None
    name = year_map.get(d)
    if name:
        return True, name
    return False, None


def is_trading_day(d: date) -> tuple:
    """
    Combined check: weekday AND not a holiday. Returns (is_trading_day, reason).
    """
    if d.weekday() >= 5:
        return False, f"Weekend ({d.strftime('%A')})"
    is_hol, hol_name = is_trading_holiday(d)
    if is_hol:
        return False, f"NSE/BSE holiday: {hol_name}"
    return True, "Trading day"


if __name__ == "__main__":
    import sys
    today = date.today()
    ok, reason = is_trading_day(today)
    print(f"{today.isoformat()}: {'TRADING DAY' if ok else 'CLOSED'} — {reason}")
    sys.exit(0)
