# Quick Start Dashboard Guide (Updated with SSOT)

## 🆕 What's New

The dashboard now uses **Single Source of Truth (SSOT)** for consistent data across all pages:
- ✅ All pages show the same PnL, positions, QC status
- ✅ Realistic synthetic data (IV 8-40%, not 1900-2400%)
- ✅ Fixed risk limit logic
- ✅ Fixed timestamp issues
- ✅ Auto-sync every 5 seconds

## Quick Start

## Problem: Dashboard Not Accessible

If you see "This site can't be reached" or "ERR_CONNECTION_REFUSED" when accessing `http://localhost:3000`, the frontend is not running.

## Solution: Start the Frontend

### Option 1: Use the Batch File (Easiest)

1. **Double-click:** `START_FRONTEND_ONLY.bat`
   - This will automatically:
     - Check if frontend is running
     - Install dependencies if needed
     - Start the frontend server
     - Open your browser

2. **Wait for startup** (10-15 seconds)
   - A new window will open showing frontend logs
   - Look for: `Local: http://localhost:3000`

3. **Access the dashboard:**
   - Open: http://localhost:3000
   - Or the browser will open automatically

### Option 2: Start Both Backend and Frontend

1. **Double-click:** `START_ALL_SERVICES.bat`
   - This starts both backend and frontend
   - Backend: http://localhost:8000
   - Frontend: http://localhost:3000

### Option 3: Manual Start

1. **Open Command Prompt** in the project folder

2. **Start Backend:**
   ```cmd
   cd dashboard\backend
   python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Open a NEW Command Prompt** and start Frontend:
   ```cmd
   cd dashboard\frontend
   npm install
   npm run dev -- --host 0.0.0.0
   ```

4. **Wait for both to start**, then open: http://localhost:3000

## Verify Services Are Running

### Check Backend (Port 8000):
- Open: http://localhost:8000/api/health
- Should show JSON data

### Check Frontend (Port 3000):
- Open: http://localhost:3000
- Should show the dashboard

## Troubleshooting

### Frontend Not Starting?

1. **Check Node.js is installed:**
   ```cmd
   node --version
   npm --version
   ```

2. **Install dependencies:**
   ```cmd
   cd dashboard\frontend
   npm install
   ```

3. **Check if port 3000 is in use:**
   ```cmd
   netstat -ano | findstr ":3000"
   ```

4. **Kill process using port 3000:**
   ```cmd
   taskkill /F /PID <process_id>
   ```

### Backend Not Starting?

1. **Check Python is installed:**
   ```cmd
   python --version
   ```

2. **Install dependencies:**
   ```cmd
   pip install uvicorn[standard] fastapi
   ```

3. **Check if port 8000 is in use:**
   ```cmd
   netstat -ano | findstr ":8000"
   ```

## Quick Status Check

Run this to check both services:
```cmd
netstat -ano | findstr ":3000 :8000"
```

You should see:
- Port 8000: Backend (Python/uvicorn)
- Port 3000: Frontend (Node.js/vite)

## Dashboard URLs

Once running:
- **Dashboard:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## Need Help?

If services still don't start:
1. Check the error messages in the command windows
2. Verify all dependencies are installed
3. Make sure ports 3000 and 8000 are not blocked by firewall
4. Try restarting your computer if ports seem stuck

---

**Quick Fix:** Just run `START_FRONTEND_ONLY.bat` - it handles everything automatically!
