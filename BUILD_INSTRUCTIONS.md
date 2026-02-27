# How to run the build (avoid PowerShell errors)

**Do not paste script output into the terminal.** If you paste the *output* of a command (the lines that say `[OK]`, `--- 1. Python ---`, etc.) into PowerShell, it will try to run each line as a command and you will see many errors.

---

## Option 1: Run the batch file from Command Prompt (recommended)

1. Press **Win + R**, type **cmd**, press Enter.
2. In the Command Prompt window, run these **two commands** (type or copy the lines below, then press Enter after each):

```cmd
cd C:\Genesis_System3
build_fresh_installer.bat
```

The batch file will:
- Run the requirements check
- Clean old dist, build frontend, build Electron
- Print the path to the new installer when done

---

## Option 2: Run from PowerShell (run commands, don’t paste output)

1. Open **PowerShell** (e.g. from Start menu).
2. **Activate venv** (optional but recommended):

```powershell
cd C:\Genesis_System3
.\venv\Scripts\Activate.ps1
```

3. **Run the build script** (this runs the check and then the batch file):

```powershell
.\run_build.ps1
```

Or run the batch file directly via cmd so its output is not interpreted by PowerShell:

```powershell
cd C:\Genesis_System3
cmd /c build_fresh_installer.bat
```

---

## Option 3: Run check and build as separate commands (PowerShell)

Run these **one at a time** (press Enter after each). Do **not** paste the output of the first command into the terminal before running the second.

```powershell
cd C:\Genesis_System3
python check_build_requirements.py
```

If that shows **ALL CHECKS PASSED**, then run:

```powershell
cmd /c build_fresh_installer.bat
```

---

## What went wrong in your run

- The lines you saw (`--- 1. Python ---`, `[OK] Python 3.14.0`, `Frontend build done.`, etc.) are **output** from the scripts.
- Those lines were **pasted** into PowerShell.
- PowerShell tried to execute them as commands (e.g. `[OK]` as a type, `---` as an operator), which caused the errors.
- **Fix:** Run the **commands** (`python check_build_requirements.py` and `build_fresh_installer.bat` or `.\run_build.ps1`), and only **read** the output; do not paste it back into the terminal.

---

## After a successful build

The installer will be at:

```
C:\Genesis_System3\desktop_app\dist\System3 Ultra Setup 1.0.0.exe
```

Double-click that file to install, or run it from Command Prompt:

```cmd
"C:\Genesis_System3\desktop_app\dist\System3 Ultra Setup 1.0.0.exe"
```
