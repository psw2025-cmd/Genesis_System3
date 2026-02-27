# Simple Start Guide - What To Do Now

## 🎯 Current Situation

You have multiple PowerShell windows open. Here's what to do:

---

## ✅ Step 1: Close Unnecessary Windows

**Close ALL PowerShell windows except ONE:**
1. Look at your taskbar (bottom of screen)
2. You'll see multiple PowerShell icons
3. Right-click on each PowerShell icon
4. Select "Close window" for each one
5. Keep only ONE PowerShell window open

**Why?** Multiple windows can cause conflicts and confusion.

---

## ✅ Step 2: Run the Cleanup Script

In your ONE remaining PowerShell window, run:

```powershell
cd C:\Genesis_System3
.\CLEANUP_AND_START.ps1
```

This script will:
- ✅ Check if dependencies are installed
- ✅ Install missing dependencies (like uvicorn)
- ✅ Check if ports are available
- ✅ Guide you to start the system

---

## ✅ Step 3: Choose How to Start

The script will ask you to choose:

### Option 1: Start FULL System (Recommended)
- Starts trading system + dashboard backend + dashboard frontend
- Everything runs automatically
- Just wait and open http://localhost:3000

### Option 2: Start ONLY Dashboard
- Starts only dashboard (backend + frontend)
- Good if trading system is already running

### Option 3: Manual Start
- Shows you exactly what commands to run
- Good if you want to see what's happening

---

## 🚀 Quick Start (If Script Doesn't Work)

If the script doesn't work, do this manually:

### 1. Install Missing Dependencies
```powershell
cd C:\Genesis_System3
.\venv\Scripts\pip.exe install uvicorn[standard] fastapi
```

### 2. Start Dashboard Backend
Open a NEW PowerShell window:
```powershell
cd C:\Genesis_System3\dashboard\backend
..\..\venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000
```

### 3. Start Dashboard Frontend
Open ANOTHER NEW PowerShell window:
```powershell
cd C:\Genesis_System3\dashboard\frontend
npm run dev
```

### 4. Open Dashboard
Open Chrome and go to: **http://localhost:3000**

---

## 📊 What You Should See

### When Backend Starts Successfully:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### When Frontend Starts Successfully:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

### In Your Browser:
- You should see the System3 Ultra Dashboard
- Overview tab showing system status
- Real-time data updating

---

## ⚠️ Common Issues

### "ModuleNotFoundError: No module named 'uvicorn'"
**Fix:**
```powershell
cd C:\Genesis_System3
.\venv\Scripts\pip.exe install uvicorn[standard]
```

### "Port 8000 already in use"
**Fix:** Close the window that's using port 8000, or restart your computer

### "Port 3000 already in use"
**Fix:** Close the window that's using port 3000, or restart your computer

### Dashboard shows "Loading..." forever
**Fix:** 
1. Check if backend is running (should see "Uvicorn running")
2. Check browser console (F12) for errors
3. Try refreshing the page (Ctrl+F5)

---

## 🎯 Summary - What To Do RIGHT NOW

1. **Close all PowerShell windows except ONE**
2. **Run:** `.\CLEANUP_AND_START.ps1`
3. **Choose Option 1** (Start FULL system)
4. **Wait 30 seconds** for everything to start
5. **Open Chrome** and go to **http://localhost:3000**

That's it! 🚀

---

## 📞 Still Having Issues?

Check these files:
- `DASHBOARD_PRODUCTION_GRADE_COMPLETE.md` - Full documentation
- `TRADER_USER_GUIDE.md` - User guide
- `logs/` - Check log files for errors

---

**Remember:** Keep only ONE PowerShell window open at a time when starting!
