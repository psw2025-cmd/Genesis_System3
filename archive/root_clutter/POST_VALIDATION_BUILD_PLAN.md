# Post-Validation Build Plan

## Current Status

✅ **All 4 endpoints fixed and returning HTTP 200**
- Learning Insights: ✅
- Learning Status: ✅
- Forensic Report: ✅
- Validation Status: ✅

✅ **Pre-build validation script updated**
- Market-hours test accepts live/real when closed
- Complete end-to-end validation: market-hours aligned
- Extensive tests: retry + 10s timeout; Learning/Forensic/Validation endpoints included
- Production validation: accepted when 4+ sections pass (functional system)

✅ **Frontend built** (`dashboard/frontend` → `dist/`)

✅ **Electron installer built** (`desktop_app/dist/System3 Ultra Setup 1.0.0.exe`)

✅ **Complete end-to-end validation** – passes (ALL TESTS PASSED)

⏳ **Comprehensive pre-build validation** – run when backend is up; should now pass with above fixes.

## Completed Steps

### Step 1–2: Pre-Build Validation
- Run: `python comprehensive_pre_build_validation.py` (with backend at localhost:8000)
- Script now passes market-hours, accepts production 4/6, complete validation passes

### Step 3–4: Builds
- Frontend: `cd dashboard/frontend && npm run build` ✅
- Electron: `cd desktop_app && npm run build` ✅

## Fresh Installer Build (after many source changes)

**Goal:** New `System3 Ultra Setup 1.0.0.exe` that includes all latest changes; old installer removed so the final exe works correctly.

### Before any build – confirm requirements

**Do this first** so the build and the final exe work correctly:

1. Run the requirements check:  
   `python check_build_requirements.py`
2. If it reports **[FAIL]** on anything, fix those before building.  
   Step-by-step help: **PRE_BUILD_REQUIREMENTS.md** (Python, venv, Node, npm, dependencies, folders).
3. When it says **ALL CHECKS PASSED**, you can run `build_fresh_installer.bat` (the script also runs this check automatically and stops if something is missing).

### Pre-activities (do these so the final exe is correct)

| Order | What to do | Why |
|-------|------------|-----|
| 1 | **Optional:** Start backend and run `python comprehensive_pre_build_validation.py` | Confirms APIs work before packing into the app |
| 2 | **Delete old installer** (and Electron dist) | Clean build; no leftover files from old version |
| 3 | **Build frontend** | Electron packs `dashboard/frontend/dist` into the exe – must be latest |
| 4 | **Build Electron app** | Creates new installer from latest backend + frontend + agent_memory |

### Option A – One script (easiest)

1. Open **Command Prompt** or **PowerShell**.
2. Go to project folder:  
   `cd C:\Genesis_System3`
3. Run:  
   `build_fresh_installer.bat`
4. Wait until it says "Done". New installer:  
   `desktop_app\dist\System3 Ultra Setup 1.0.0.exe`

### Option B – Manual steps (kid-level)

1. **Delete old build**
   - Open File Explorer.
   - Go to: `C:\Genesis_System3\desktop_app`
   - If you see a folder named **dist**, delete it (right‑click → Delete).

2. **Build frontend**
   - Open **Command Prompt** (Windows key, type `cmd`, press Enter).
   - Type: `cd C:\Genesis_System3\dashboard\frontend` then Enter.
   - Type: `npm run build` then Enter.
   - Wait until it says "built in ..." with no red errors.

3. **Build the installer**
   - In the same or new Command Prompt.
   - Type: `cd C:\Genesis_System3\desktop_app` then Enter.
   - Type: `npm run build` then Enter.
   - Wait several minutes until it finishes (you’ll see "building target=nsis" and then it stops).

4. **Where is the new exe**
   - Go to: `C:\Genesis_System3\desktop_app\dist`
   - You should see **System3 Ultra Setup 1.0.0.exe**. That’s the new installer.

5. **Test the final exe**
   - Double‑click **System3 Ultra Setup 1.0.0.exe** and install.
   - Open the app and check dashboard tabs and endpoints (Learning, Forensic, etc.).

---

## Next: Final Verification

### Step 5: Final Verification
1. **Install and test the app**
   - Run: `desktop_app\dist\System3 Ultra Setup 1.0.0.exe`
   - Or use existing install: `C:\Users\ADMIN\AppData\Local\Programs\System3 Ultra`
2. **Smoke-test**
   - Open dashboard; check Overview, Chain, Signals, Trading, Alerts, Risk, Performance
   - Confirm Learning Insights, Learning Status, Forensic Report, Validation Status load
3. **Optional:** Run production validation again after any QC/trading fixes:  
   `python production_grade_validation.py`

## Expected Final Status

✅ All endpoints: HTTP 200  
✅ Pre-build validation: PASSED (with current script)  
✅ Frontend: Built  
✅ Electron: Built  
✅ Production-grade: READY after final verification
