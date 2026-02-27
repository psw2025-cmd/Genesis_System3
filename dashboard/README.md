# System3 Ultra Dashboard

Real-time web dashboard for monitoring and controlling the System3 options paper-trading system.

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- npm (comes with Node.js)

### Installation & Run

**Single command (recommended):**
```powershell
.\scripts\run_dashboard.ps1
```

This will:
1. Check prerequisites
2. Create/activate Python venv
3. Install backend dependencies
4. Install frontend dependencies
5. Start backend (http://localhost:8000)
6. Start frontend (http://localhost:3000)

### Manual Setup

**Backend:**
```powershell
cd dashboard\backend
python -m venv ..\..\venv
..\..\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

**Frontend:**
```powershell
cd dashboard\frontend
npm install
npm run dev
```

## Verification

Run the verifier:
```powershell
.\scripts\verify_dashboard.ps1
```

Expected output: `DASHBOARD_STATUS=PASS`

## Features

### Real-time System Overview
- Mode (LIVE/SIM)
- Broker status
- Market status (open/closed)
- Cycle count, refresh interval
- QC status with failure reasons
- Trades executed, open positions
- Total PnL, daily PnL
- Performance SLA metrics with live charts

### Option Chain Analytics
- Multi-underlying support (NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY, SENSEX)
- ATM strike identification
- CE/PE LTP, OI, IV, volume
- Put-Call ratio (PCR)
- Liquidity scores
- Live chain table with filters:
  - Strike range
  - Near ATM only
  - Liquidity threshold
  - Show invalid rows

### Signals & Recommendations
- Top trade signal display
- Explainability panel (reasons, confidence)
- QC gating status
- "What blocked trading?" panel
- Strategy details (legs, strikes, entry, SL, target)
- Export signal snapshot as JSON

### Paper Trading Console
- Open positions table
- PnL charts:
  - Equity curve
  - Realized vs unrealized
  - Win-rate gauge
- Trade blotter
- Risk panel (max positions, exposure, kill switch)

### Model & System Behavior
- Model status (ensemble vs fallback)
- Data quality metrics
- Performance metrics
- Errors & warnings (tail of logs with redaction)
- Security audit (secrets scan)

### Control Plane
- Start/Stop runner (UI controls)
- Set refresh interval
- Mode selection (SIM/LIVE)
- Download proof pack

## API Endpoints

- `GET /api/health` - System health overview
- `GET /api/qc` - QC report
- `GET /api/chain/{underlying}` - Option chain for underlying
- `GET /api/signal/top` - Top trade signal
- `GET /api/positions` - Open positions
- `GET /api/pnl` - PnL data
- `GET /api/perf` - Performance metrics
- `GET /api/logs/tail?lines=200` - Tail of logs (redacted)
- `GET /api/audit/secrets` - Secrets scan
- `WS /ws/stream` - WebSocket for real-time updates

## Security

- Secrets redaction in all logs and API responses
- Secrets scanner checks outputs/
- CORS restricted to localhost only
- No secrets displayed in UI

## Troubleshooting

**Backend won't start:**
- Check Python version: `python --version` (need 3.8+)
- Check port 8000 is free: `netstat -an | findstr 8000`
- Activate venv: `venv\Scripts\Activate.ps1`

**Frontend won't start:**
- Check Node.js version: `node --version` (need 18+)
- Check port 3000 is free: `netstat -an | findstr 3000`
- Delete node_modules and reinstall: `rm -r node_modules && npm install`

**No data showing:**
- Ensure system has run at least once: `python option_chain_automation_master.py --sim --cycles 1`
- Check outputs/ directory has files
- Check browser console for errors

**WebSocket not updating:**
- Check browser console for connection errors
- Verify backend is running
- Check CORS settings if accessing from different origin

## Architecture

- **Backend**: FastAPI (Python)
  - Reads outputs/ files
  - Provides REST API
  - WebSocket for real-time updates
  - File watcher for change detection
  - SQLite time-series storage
  - Event sourcing/audit log

- **Frontend**: React + Vite + TypeScript
  - Recharts for visualization
  - Axios for API calls
  - React Router for navigation
  - Dark mode support

## Additional Features

- SQLite time-series storage for historical charts
- Event sourcing/audit log for forensics
- Secrets redaction and scanning
- Market hours intelligence
- Performance SLA tracking
