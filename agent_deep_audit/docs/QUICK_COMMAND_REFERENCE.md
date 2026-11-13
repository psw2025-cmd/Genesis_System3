# Quick Command Reference - Auto-Fetch Option Chain

## 🚀 Python Commands to Run

### 1. Auto-Fetch (During Market Hours)

```bash
venv\Scripts\python.exe -m core.engine.auto_fetch_option_chain_hourly
```

**What it does**:
- Auto-detects if market is open (9:15 AM - 3:30 PM IST)
- Fetches all 5 indices (NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY, SENSEX)
- Adds timestamps to each row
- Appends to `storage/live/option_chain_ALL_INDICES.csv`
- Skips if market is closed

---

### 2. Force Fetch (Even if Market Closed - for Testing)

```bash
venv\Scripts\python.exe -m core.engine.auto_fetch_option_chain_hourly --force
```

**What it does**:
- Fetches data even when market is closed
- Useful for testing
- Same functionality as above, but ignores market hours check

---

### 3. Fetch All Strikes (Not Just ATM)

```bash
venv\Scripts\python.exe -m core.engine.auto_fetch_option_chain_hourly --all-strikes
```

**What it does**:
- Fetches ALL available strikes (not just ATM ±5%)
- Takes longer but gets complete option chain
- Useful for comprehensive analysis

---

### 4. Custom Output File

```bash
venv\Scripts\python.exe -m core.engine.auto_fetch_option_chain_hourly -o storage/live/my_custom_file.csv
```

**What it does**:
- Saves to custom file instead of default
- Default: `storage/live/option_chain_ALL_INDICES.csv`

---

### 5. Check Market Status

```bash
venv\Scripts\python.exe -c "from core.engine.auto_fetch_option_chain_hourly import get_market_status; import json; print(json.dumps(get_market_status(), indent=2))"
```

**What it does**:
- Shows current market status
- Shows if market is open/closed
- Shows time until market opens/closes

---

## 📋 Other Useful Commands

### Fetch Single Index (Manual)

```bash
venv\Scripts\python.exe -m core.engine.test_angelone_option_chain NIFTY
```

### Fetch All Indices (One-Time, No Timestamps)

```bash
venv\Scripts\python.exe -m core.engine.fetch_all_indices_option_chain
```

### Validate CSV Data

```bash
venv\Scripts\python.exe -m core.validation.option_chain_validator storage/live/option_chain_ALL_INDICES.csv --underlying NIFTY --exchange NFO
```

---

## 🎯 Recommended Daily Command

**For hourly auto-fetch during market hours**:

```bash
venv\Scripts\python.exe -m core.engine.auto_fetch_option_chain_hourly
```

**Set this up in Windows Task Scheduler to run every hour at :15 minutes** (9:15, 10:15, 11:15, etc.)

---

## 📝 Notes

- **Market Hours**: 9:15 AM - 3:30 PM IST, Monday to Friday
- **Default**: Fetches ATM strikes only (within 5% of spot)
- **Output**: `storage/live/option_chain_ALL_INDICES.csv`
- **Timestamps**: Automatically added to each row

---

**Quick Start**: Just run the first command above during market hours!
