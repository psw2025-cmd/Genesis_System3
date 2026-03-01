# Governance: Dual .in + .txt Requirements (SYSTEM3_OMEGA_ULTRA)

This project uses a **dual requirements setup** for production-grade, reproducible dependency management.

## Rule summary

| Item | Rule |
|------|------|
| **Sources** | `.in` files are the **editable sources** (unpinned or loosely pinned). |
| **Locked files** | `.txt` files are **generated** with `pip-compile` and are **fully pinned**. |
| **Install** | **Never** install from `.in`. **Always** install from `.txt`. |
| **Adding a dependency** | Edit the appropriate `.in`, then regenerate the `.txt` with `pip-compile`. |

## Files

| File | Purpose |
|------|--------|
| `requirements_runtime.in` | Source for runtime dependencies. |
| `requirements_runtime.txt` | Locked runtime deps (generated). |
| `requirements-dev.in` | Source for dev dependencies (includes runtime via `-r requirements_runtime.txt`). |
| `requirements-dev.txt` | Locked dev deps (generated). |

## Regenerating .txt from .in

**Option A – script (recommended)**  
From repo root with venv active:
```powershell
.\.venv\Scripts\activate.ps1
scripts\compile_requirements.bat
```
This installs `pip-tools`, then runs `pip-compile` for both runtime and dev.

**Option B – manual**  
1. Install pip-tools: `pip install pip-tools`  
2. Compile runtime: `pip-compile requirements_runtime.in -o requirements_runtime.txt`  
3. Compile dev: `pip-compile requirements-dev.in -o requirements-dev.txt`  

4. **Install** (unchanged; Run-All or manual):
   ```powershell
   pip install -r requirements_runtime.txt
   pip install -r requirements-dev.txt
   ```

## Governance constraints (keep in .in)

- **Streamlit 1.37 + wheel 0.46.2**: `packaging>=24,<25` (P1 security fixes).
- **Playwright**: comment reminder `# run: playwright install chromium`.
- **libmagic**: `python-magic` on non-Windows, `python-magic-bin` on Windows.
- **Patch notes**: keep comments for any version patched for compatibility (e.g. setuptools, wheel).

## QA Guardian and proof artifacts

- Run **Black, Flake8, Bandit, Safety, Pytest, Pip-Audit** on every build.
- Proof artifacts go under **`logs/inspector/`** (e.g. `pip_audit.json`, `safety_report.txt`, transcripts).
- Do not declare success until checks have run and artifacts exist or failure is reported with remediation.

## Fail fast

- If dependency resolution fails, **log reason and remediation steps** (e.g. in `proof/archive/RUN_ALL_FAIL_*.json`).
- Validate `.in` vs `.txt` consistency before proceeding; if in doubt, re-run `pip-compile`.
