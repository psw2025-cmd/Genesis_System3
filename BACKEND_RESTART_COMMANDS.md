# Backend Restart Commands - Quick Reference

## 🚀 QUICK RESTART (EASIEST)

### **Option 1: Use Batch File**
```bash
RESTART_BACKEND.bat
```

### **Option 2: Use Fix & Start**
```bash
FIX_PORT_AND_START.bat
```
(Use this if port 8000 is in use)

---

## 📝 MANUAL COMMANDS

### **PowerShell/Command Prompt:**
```bash
cd dashboard\backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### **With Port Clear (PowerShell):**
```powershell
# Kill existing processes
Get-Process | Where-Object { $_.CommandLine -like '*uvicorn*' } | Stop-Process -Force
netstat -ano | Select-String ":8000.*LISTENING" | ForEach-Object { 
    $pid = ($_ -split '\s+')[-1]
    if ($pid -match '^\d+$') { Stop-Process -Id $pid -Force }
}

# Start backend
cd dashboard\backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

---

## ✅ VERIFY BACKEND IS RUNNING

### **Check Health:**
```bash
curl http://localhost:8000/api/health
```

### **Or in Browser:**
- Health: http://localhost:8000/api/health
- API Docs: http://localhost:8000/docs

---

## 🔍 WHAT TO LOOK FOR IN LOGS

### **✅ Good Signs:**
- `Application startup complete`
- `Uvicorn running on http://0.0.0.0:8000`
- `WebSocket /ws/stream [accepted]`
- `GET /api/health HTTP/1.1" 200 OK`

### **⚠️ Normal (Not Errors):**
- `GET / HTTP/1.1" 404` - No root endpoint (normal)
- `GET /favicon.ico HTTP/1.1" 404` - Browser request (normal)

---

## 📋 AVAILABLE BATCH FILES

1. **RESTART_BACKEND.bat** - Simple restart
2. **RESTART_BACKEND_WITH_FIXES.bat** - Restart with fixes
3. **FIX_PORT_AND_START.bat** - Clear port and start
4. **START_ALL_SERVICES.bat** - Start backend + frontend
5. **RUN_AND_TRACK_ALL.bat** - Full system with tracking

---

**Quick Command**: `RESTART_BACKEND.bat`
