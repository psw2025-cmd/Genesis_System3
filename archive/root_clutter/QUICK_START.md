# 🚀 Genesis System3 - Quick Start Guide

## One-Click Startup

### Windows
```batch
scripts\run_local.bat
```

### Linux/Mac
```bash
bash scripts/run_local.sh
```

This will:
- ✅ Check system health
- ✅ Install/verify dependencies
- ✅ Clear ports if needed
- ✅ Start backend (port 8000)
- ✅ Start frontend (port 3000)
- ✅ Open dashboard in browser

## Manual Startup

### 1. Check System Health
```bash
python scripts\doctor.py
```

### 2. Start Backend
```bash
cd dashboard\backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Start Frontend (new terminal)
```bash
cd dashboard\frontend
npm run dev -- --host 0.0.0.0
```

### 4. Access Dashboard
- **Dashboard:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Status:** http://localhost:8000/api/status

## Environment Setup (Optional)

For live market data, create `config/.env` from `config/.env.example`:

```bash
copy config\.env.example config\.env
```

Then edit `config/.env` and add your Angel One credentials:
- `ANGELONE_API_KEY`
- `ANGELONE_CLIENT_ID`
- `ANGELONE_PIN` or `ANGELONE_PASSWORD`
- `ANGELONE_TOTP`

**Note:** System works without credentials (uses synthetic data when market closed).

## Health Checks

### Run Smoke Tests
```bash
python scripts\smoke_test.py
```

### Run Doctor Check
```bash
python scripts\doctor.py
```

### Run Dashboard Tests
```bash
python scripts\comprehensive_dashboard_test.py
```

## Troubleshooting

### Port Already in Use
```bash
# Windows - Kill process on port 8000
netstat -ano | findstr :8000
taskkill /F /PID <PID>

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Frontend Not Building
```bash
cd dashboard\frontend
rm -rf node_modules
npm install
npm run build
```

### Backend Not Starting
```bash
pip install uvicorn[standard] fastapi
python scripts\doctor.py
```

## System Status

Check comprehensive system status:
```bash
curl http://localhost:8000/api/status
```

Or visit: http://localhost:8000/api/status

## Support

- **Logs:** `logs/` directory
- **Outputs:** `outputs/` directory
- **Agent Runs:** `outputs/agent_runs/` directory

## Next Steps

1. ✅ System is production-ready
2. ⚠️ Add Angel One credentials (optional, for live data)
3. 📊 Monitor dashboard at http://localhost:3000
4. 🔍 Check `/api/status` for system health
