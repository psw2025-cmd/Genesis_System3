# Auto-Fetch Option Chain - Hourly Setup Guide

**Status**: ✅ **READY TO USE**

This guide explains how to set up automatic hourly fetching of option chain data during market hours.

---

## 🎯 Features

- ✅ **Auto-detects market hours** (9:15 AM - 3:30 PM IST, Mon-Fri)
- ✅ **Fetches every hour** during market hours
- ✅ **Adds timestamp** to each row
- ✅ **Appends to same file** (maintains history)
- ✅ **Skips when market closed** (no unnecessary API calls)

---

## 📋 Setup Instructions

### Option 1: Windows Task Scheduler (Recommended)

#### Step 1: Create Batch File

Create a file `run_auto_fetch.bat` in project root:

```batch
@echo off
cd /d C:\Genesis_System3
call venv\Scripts\activate.bat
python -m core.engine.auto_fetch_option_chain_hourly
deactivate
```

#### Step 2: Schedule Task

1. Open **Task Scheduler** (search "Task Scheduler" in Windows)
2. Click **Create Basic Task**
3. **Name**: "Auto Fetch Option Chain Hourly"
4. **Description**: "Fetches option chain data every hour during market hours"
5. **Trigger**: 
   - Select **Daily**
   - Start date: Today
   - Time: 9:15 AM
   - Recur every: 1 day
6. **Action**: 
   - Select **Start a program**
   - Program/script: `C:\Genesis_System3\run_auto_fetch.bat`
7. **Conditions**:
   - ✅ Start the task only if the computer is on AC power (uncheck if on battery)
   - ✅ Wake the computer to run this task (optional)
8. **Settings**:
   - ✅ Allow task to be run on demand
   - ✅ Run task as soon as possible after a scheduled start is missed
   - ✅ If the task fails, restart every: 1 hour
   - ✅ Stop the task if it runs longer than: 10 minutes

#### Step 3: Add Multiple Triggers (Every Hour)

1. After creating task, right-click and select **Properties**
2. Go to **Triggers** tab
3. Click **New** to add additional triggers:
   - **10:15 AM** (every day)
   - **11:15 AM** (every day)
   - **12:15 PM** (every day)
   - **1:15 PM** (every day)
   - **2:15 PM** (every day)
   - **3:15 PM** (every day)

**Note**: The script itself checks market hours, so it will skip if market is closed.

---

### Option 2: Python Schedule Library (Alternative)

Create a file `run_auto_fetch_scheduler.py`:

```python
import schedule
import time
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent

def fetch_data():
    """Run the auto-fetch script"""
    cmd = [
        sys.executable,
        "-m", "core.engine.auto_fetch_option_chain_hourly"
    ]
    subprocess.run(cmd, cwd=ROOT_DIR)

# Schedule every hour
schedule.every().hour.at(":15").do(fetch_data)

print("Auto-fetch scheduler started. Running every hour at :15 minutes.")
print("Press Ctrl+C to stop.")

try:
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute
except KeyboardInterrupt:
    print("\nScheduler stopped.")
```

Run with:
```bash
venv\Scripts\python.exe run_auto_fetch_scheduler.py
```

---

## 🚀 Manual Testing

### Test Market Hours Detection

```bash
venv\Scripts\python.exe -c "from core.engine.auto_fetch_option_chain_hourly import get_market_status; import json; print(json.dumps(get_market_status(), indent=2))"
```

### Test Fetch (Market Hours)

```bash
venv\Scripts\python.exe -m core.engine.auto_fetch_option_chain_hourly
```

### Force Fetch (Even if Market Closed)

```bash
venv\Scripts\python.exe -m core.engine.auto_fetch_option_chain_hourly --force
```

---

## 📊 Output File

**File**: `storage/live/option_chain_ALL_INDICES.csv`

### New Columns Added

- `fetch_timestamp`: Human-readable timestamp (e.g., "2025-12-05 10:15:00 IST")
- `fetch_timestamp_iso`: ISO format timestamp
- `fetch_date`: Date only (e.g., "2025-12-05")
- `fetch_time`: Time only (e.g., "10:15:00")

### Data Structure

Each fetch appends new rows with:
- Same option data (underlying, strike, LTP, etc.)
- New timestamp columns
- All data from that hour

### Example

```
fetch_timestamp,fetch_timestamp_iso,fetch_date,fetch_time,underlying,exchange,...
2025-12-05 09:15:00 IST,2025-12-05T09:15:00+05:30,2025-12-05,09:15:00,NIFTY,NFO,...
2025-12-05 10:15:00 IST,2025-12-05T10:15:00+05:30,2025-12-05,10:15:00,NIFTY,NFO,...
2025-12-05 11:15:00 IST,2025-12-05T11:15:00+05:30,2025-12-05,11:15:00,NIFTY,NFO,...
```

---

## ⚙️ Configuration

### Market Hours

Market hours are defined in `is_market_open()` function:

```python
# Market hours: 9:15 AM - 3:30 PM IST
# Days: Monday to Friday
```

To modify, edit `core/engine/auto_fetch_option_chain_hourly.py`.

### Fetch Frequency

Default: Every hour at :15 minutes (9:15, 10:15, 11:15, etc.)

To change:
- **Task Scheduler**: Modify trigger times
- **Python Schedule**: Modify `schedule.every().hour.at(":15")`

### Strikes

Default: ATM strikes only (within 5% of spot)

To fetch all strikes:
```bash
python -m core.engine.auto_fetch_option_chain_hourly --all-strikes
```

---

## 📈 Data Analysis

### Query Latest Data

```python
import pandas as pd

df = pd.read_csv('storage/live/option_chain_ALL_INDICES.csv')

# Get latest fetch
latest_timestamp = df['fetch_timestamp'].max()
latest_data = df[df['fetch_timestamp'] == latest_timestamp]

print(f"Latest fetch: {latest_timestamp}")
print(f"Options in latest fetch: {len(latest_data)}")
```

### Track Changes Over Time

```python
# Group by timestamp and underlying
hourly_summary = df.groupby(['fetch_timestamp', 'underlying']).agg({
    'ltp': 'mean',
    'oi': 'sum',
    'volume': 'sum'
}).reset_index()

print(hourly_summary)
```

---

## 🔍 Monitoring

### Check Last Fetch

```bash
venv\Scripts\python.exe -c "import pandas as pd; df = pd.read_csv('storage/live/option_chain_ALL_INDICES.csv'); print('Last fetch:', df['fetch_timestamp'].max() if 'fetch_timestamp' in df.columns else 'No timestamp column')"
```

### Check Fetch Count

```bash
venv\Scripts\python.exe -c "import pandas as pd; df = pd.read_csv('storage/live/option_chain_ALL_INDICES.csv'); print('Total fetches:', df['fetch_timestamp'].nunique() if 'fetch_timestamp' in df.columns else 'N/A'); print('Total rows:', len(df))"
```

---

## ⚠️ Important Notes

1. **Market Hours**: Script automatically skips when market is closed
2. **File Size**: CSV file will grow over time. Consider archiving old data periodically
3. **API Limits**: Be aware of Dhan API rate limits
4. **Errors**: Script logs errors but continues with other indices
5. **Weekends**: Script will skip weekends automatically

---

## 🛠️ Troubleshooting

### Task Not Running

1. Check Task Scheduler for errors
2. Verify batch file path is correct
3. Check Python virtual environment path
4. Review Windows Event Viewer for errors

### No Data Appended

1. Check if market is open
2. Verify broker credentials
3. Check logs for API errors
4. Test manual fetch first

### Duplicate Headers

- Script handles this automatically
- First write creates header
- Subsequent writes append data only

---

## ✅ Verification

After setup, verify it's working:

1. **Check Task Scheduler**: Task should be listed and enabled
2. **Wait for next hour**: Let it run automatically
3. **Check CSV file**: Should have new rows with timestamps
4. **Verify timestamps**: Each row should have `fetch_timestamp` column

---

## 📝 Summary

✅ **Auto-detects market hours**  
✅ **Fetches every hour during market**  
✅ **Adds timestamp to each row**  
✅ **Appends to same file**  
✅ **Skips when market closed**  
✅ **Ready for Windows Task Scheduler**  

**Status**: ✅ **READY FOR PRODUCTION**
