# Dashboard Demo Testing (Outside Market Hours)

This guide explains how to test the dashboard so it looks like it does during market hours, when you don't have live data.

---

## Quick Start: One-Command Demo

```powershell
powershell -ExecutionPolicy Bypass -File scripts\populate_demo_data_for_dashboard.ps1
```

Then refresh the dashboard (or restart backend if it was already running). All tabs should show data.

---

## What Gets Populated

| Tab | Data Source | What the Script Does |
|-----|-------------|----------------------|
| **Chain** | `outputs/chain_raw_live.csv` | Generates 200+ synthetic option contracts (NIFTY, BANKNIFTY, etc.) |
| **Charts** | Uses chain data | Heatmap, IV surface, Greeks, PCR all work with chain data |
| **Signals** | `outputs/top_trade_signal.json` | Generates TRADE or NO_TRADE signal |
| **Model** | `outputs/qc_report_live.json` | QC report (PASS) |
| **ML** | `outputs/ml_performance.json` | Sample model comparison (Ensemble, XGBoost, LightGBM) |
| **Model (Logs)** | `logs/*.log` | Creates a sample log file |

---

## Alternative: API-Level Synthetic (No Files)

If you prefer not to create files, you can use **synthetic mode** at the API level:

1. Set environment variable before starting the backend:
   ```powershell
   $env:SYSTEM3_REAL_ONLY = "0"
   python -m uvicorn dashboard.backend.app:app --host 127.0.0.1 --port 8000
   ```

2. Or in a batch file:
   ```batch
   set SYSTEM3_REAL_ONLY=0
   python -m uvicorn dashboard.backend.app:app --host 127.0.0.1 --port 8000
   ```

**Effect:** When market is closed, the API returns synthetic data for:
- Chain (`/api/chain/NIFTY`)
- Signals (`/api/signal/top`)
- QC (`/api/qc`)
- Health (synthetic health when market closed)

**Limitation:** Charts still need chain data (they call `get_chain` internally, so they get synthetic data when `REAL_ONLY=0`). ML and Logs still need the demo script to create their files.

---

## Option 1: Full Demo (Recommended)

Run the populate script, then start the dashboard:

```powershell
# 1. Populate all demo data
powershell -File scripts\populate_demo_data_for_dashboard.ps1

# 2. Start dashboard (or use START_FULL_DASHBOARD_SYSTEM.bat)
START_FULL_DASHBOARD_SYSTEM.bat
```

---

## Option 2: Chain + Charts Only

If you only need Chain and Charts:

```powershell
python scripts\generate_synthetic_live_data.py
```

This creates `chain_raw_live.csv`, `top_trade_signal.json`, `qc_report_live.json`, and updates `health.json`.

---

## Option 3: ML Tab Only

Create `outputs/ml_performance.json` manually or run the full demo script. The ML tab reads from this file.

---

## Option 4: Logs Tab Only

Create any `.log` file in `logs/`:

```powershell
echo "[2026-02-28 15:00:00] INFO - Demo log line" > logs\demo.log
```

The backend finds the most recently modified `.log` file in `logs/` (including subdirs).

---

## During Real Market Hours

When the market is open (Mon–Fri 9:15 AM – 3:30 PM IST):

1. Run the trading system: `option_chain_automation_master.py` or `scripts/run_live_chain.py`
2. It will populate `chain_raw_live.csv`, `health.json`, `top_trade_signal.json`, etc. with real data
3. The dashboard will show live data automatically

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Chain still shows "Chain data not found" | Run `python scripts\generate_synthetic_live_data.py` from repo root |
| Charts show "No chain data" | Chain and Charts share data; ensure chain_raw_live.csv exists |
| ML shows "No model comparison" | Run `populate_demo_data_for_dashboard.ps1` to create ml_performance.json |
| Logs show "No logs available" | Create a `.log` file in `logs/` or run the demo script |
| Backend not picking up new files | Restart the backend (files are read on each request, so usually no restart needed) |
