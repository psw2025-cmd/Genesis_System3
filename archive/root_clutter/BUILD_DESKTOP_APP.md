# Build System3 Ultra Desktop Application

## Quick Start

### Step 1: Setup Environment
```bash
# Run setup script
scripts\setup_all.bat
```

This will:
- Check Python and Node.js
- Install all dependencies
- Build frontend
- Add upgrade agent endpoints

### Step 2: Build Desktop App
```bash
# Build Windows EXE
cd desktop_app
npm run build:win
```

Or use the batch script:
```bash
scripts\build_win.bat
```

### Step 3: Run Desktop App
```bash
# Development mode
cd desktop_app
npm start

# Or run the built EXE
desktop_app\dist\System3 Ultra Setup 1.0.0.exe
```

## What Gets Built

The build process creates:
- **Windows EXE:** `desktop_app/dist/System3 Ultra Setup 1.0.0.exe`
- **Installer:** NSIS installer with auto-update support
- **Portable:** All dependencies bundled

## Features

### Desktop App Includes:
- ✅ React UI embedded
- ✅ Backend auto-starts
- ✅ System tray icon
- ✅ Desktop notifications
- ✅ Auto-restart on crash
- ✅ Upgrade Agent
- ✅ Proof Pack download

## Development Mode

For development, run:
```bash
# Terminal 1: Backend
cd dashboard\backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Frontend
cd dashboard\frontend
npm run dev

# Terminal 3: Electron
cd desktop_app
npm start
```

## Troubleshooting

### Build Fails
- Check Node.js version (>= 18)
- Check Python version (>= 3.8)
- Run `npm install` in desktop_app
- Check frontend build succeeds first

### EXE Doesn't Start
- Check backend dependencies installed
- Check Python in PATH
- Check logs in `desktop_app/logs/`

### Backend Not Starting
- Check port 8000 is free
- Check Python dependencies installed
- Check `dashboard/backend/app.py` exists

---

**Status:** Ready to build!
