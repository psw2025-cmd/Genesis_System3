# System3 Backend Production Restart Guide

**Date**: 2026-02-10  
**Status**: ✅ **PRODUCTION-READY**

---

## 🚀 Quick Start

### Option 1: Use PowerShell Script (Recommended)
```powershell
cd C:\Genesis_System3
.\restart_backend.ps1
```

### Option 2: Manual Restart
```powershell
# Kill all Python processes on port 8000
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Start backend (PRODUCTION MODE - no auto-reload)
cd C:\Genesis_System3\dashboard\backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

**⚠️ IMPORTANT**: Do NOT use `--reload` flag in production!
- `--reload` triggers file watchers that restart backend on every change
- Each restart = new Angel One login = rate limit hits
- Production mode (no reload) = stable connection

---

## ✅ Verification Commands

### 1. Check Backend Health
```powershell
python -c "import requests, json; r = requests.get('http://localhost:8000/api/health', timeout=5); print(json.dumps(r.json(), indent=2))"
```

**Expected Output**:
```json
{
  "status": "ok",
  "mode": "LIVE",
  "broker_status": "connected",
  "qc_status": "PASS"
}
```

### 2. Check Runner Status
```powershell
python -c "import requests, json; r = requests.get('http://localhost:8000/api/runner/status', timeout=5); print(json.dumps(r.json(), indent=2))"
```

**Expected Output**:
```json
{
  "runner": "STOPPED" | "RUNNING",
  "mode": "FULLY_AUTONOMOUS" | "PAPER",
  "pid": null | <process_id>,
  "heartbeat_age_seconds": <seconds>
}
```

### 3. Check QC Status
```powershell
python -c "import requests, json; r = requests.get('http://localhost:8000/api/qc', timeout=5); print(json.dumps(r.json(), indent=2))"
```

**Expected Output**:
```json
{
  "status": "PASS",
  "checks": {
    "data_freshness": "OK",
    "price_consistency": "OK",
    "oi_consistency": "OK",
    "volume_consistency": "OK"
  },
  "data_source": "synthetic" | "real"
}
```

---

## 🔒 Rate Limiting Protection

### What Was Fixed

1. **Login Retry Logic** (`_safe_generateSession`):
   - Exponential backoff: 2s, 4s, 8s delays
   - Detects rate limit errors: "Access denied", "exceeding access rate", "10054"
   - Max 3 retries before failing gracefully

2. **Profile Fetch Retry Logic** (`_safe_get_profile`):
   - Same exponential backoff pattern
   - Graceful fallback: Returns None instead of crashing
   - Prevents secondary getProfile calls from hitting rate limits

3. **API Call Delays**:
   - 1s delay before every SmartAPI call (getProfile, getLTP, getMarketData)
   - FastAPI middleware adds 0.1s delay per request
   - Prevents rapid-fire requests during startup

4. **Production Mode**:
   - No `--reload` flag = no file watchers = no auto-restarts
   - Stable connection = no repeated logins = no rate limit hits

---

## 📊 Dashboard Verification

After restart, verify in browser:

1. **Open Dashboard**: `http://localhost:3000` (or Electron app)
2. **Check Control Tab**:
   - Runner Status should show current state
   - Start/Stop buttons should work
3. **Check Overview Tab**:
   - Broker status should show "CONNECTED" (green)
   - QC Status should show "PASS"
4. **Check Model Tab**:
   - Data Quality should show "PASS" (green)

---

## 🐛 Troubleshooting

### Issue: "Access denied because of exceeding access rate"

**Solution**:
1. Wait 60 seconds (rate limits reset)
2. Restart backend using `restart_backend.ps1`
3. Verify no other processes are calling Angel One API

### Issue: Backend not responding

**Solution**:
```powershell
# Check if backend is running
netstat -ano | findstr ":8000.*LISTENING"

# If not running, restart
.\restart_backend.ps1
```

### Issue: Runner endpoints return 404

**Solution**:
- Backend needs restart to register new routes
- Run `restart_backend.ps1` or manual restart
- Verify routes: `python -c "import app; print([r.path for r in app.app.routes if 'runner' in r.path])"`

---

## 📝 Production Checklist

- [x] Backend restarts cleanly
- [x] No `--reload` flag (production mode)
- [x] Rate limiting protection active
- [x] QC health check passes
- [x] Runner endpoints accessible
- [x] Dashboard shows correct status
- [x] Angel One connection stable (no rate limit errors)

---

**Status**: ✅ **READY FOR PRODUCTION USE**
