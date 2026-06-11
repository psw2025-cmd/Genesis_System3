# Special Trading Days Configuration

## Overview

The system now supports **special trading days** when the market is open on weekends or holidays (e.g., Budget Day).

## Current Special Trading Days

### Budget Day 2026
- **Date**: February 1, 2026 (Sunday)
- **Status**: ✅ Configured

## How to Add More Special Trading Days

Edit `src/utils/market_hours.py` and add dates to the `SPECIAL_TRADING_DAYS` list:

```python
SPECIAL_TRADING_DAYS: List[date] = [
    date(2026, 2, 1),  # Budget Day 2026 (Sunday)
    date(2026, 3, 15),  # Add your special trading day here
    # Add more as needed
]
```

## How It Works

1. **Normal Days**: Market is open Mon-Fri, 09:15 - 15:30 IST
2. **Weekends**: Market is closed (Saturday/Sunday)
3. **Special Trading Days**: Market is open even on weekends/holidays
4. **Time Check**: Still applies (09:15 - 15:30 IST)

## Verification

When you run the system on a special trading day:
- System will detect it's a special trading day
- Market hours check will pass (if within 09:15-15:30 IST)
- Trading will proceed normally

## Example

For Budget Day 2026 (Feb 1, Sunday):
- Date: 2026-02-01 (Sunday)
- Market Hours: 09:15 - 15:30 IST
- Status: ✅ Market will be treated as OPEN

---

**Note**: Always verify with NSE/BSE official announcements for special trading days.
