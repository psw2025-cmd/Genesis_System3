# Agent Dashboard Verification (Playwright) – No User Screenshots Needed

**Purpose:** Let the **agent** test the dashboard and capture visual/structural issues **automatically**, so the **user** can verify everything from the report and saved screenshots without having to take or send images to the agent.

---

## 1. How it works

1. **You (or the agent) ensure backend and dashboard are running**  
   - Backend: `http://127.0.0.1:8000`  
   - Streamlit: `http://127.0.0.1:8501`  
   (e.g. via Run-All or your usual start script.)

2. **Agent runs the Playwright verification script:**
   ```bash
   python tools/playwright_dashboard_verification.py
   ```

3. **The script:**
   - Opens each URL (API docs, Streamlit, optionally React) in a **headless Chromium** browser.
   - Takes **full-page screenshots** and saves them under `proof/archive/dashboard_screenshots_YYYYMMDD_HHMMSS/`.
   - Runs **basic checks** (page loads, no obvious error text, key content).
   - Writes a **JSON report** to `proof/archive/dashboard_verification_YYYYMMDD_HHMMSS.json` with:
     - `passed`: true/false
     - `checks`: list of { name, passed, detail }
     - `issues`: list of strings (what went wrong or looked wrong)
     - `screenshots`: list of file paths

4. **Agent reads the report** and can tell the user:
   - “Dashboard verification: **passed** / **failed**.”
   - “Issues: [list].”
   - “Screenshots saved at: `proof/archive/dashboard_screenshots_...` (you can open these in Cursor or file explorer to verify visually).”

So the **user** can verify the dashboard using the **same screenshots and report** the agent used, without ever sending a screenshot to the agent.

---

## 2. One-time setup (Playwright)

```bash
# From repo root, with .venv activated
pip install playwright
playwright install chromium
```

Optional: add `playwright` to `requirements-dev.txt` (already added). After `pip install -r requirements-dev.txt`, still run `playwright install chromium` once.

---

## 3. What the agent should do (workflow)

When the user asks to “verify the dashboard” or “test the dashboard and report visual issues”:

1. **Ensure services are up** (or tell the user to start them):
   - Backend on 8000, Streamlit on 8501.
2. **Run:**
   ```bash
   python tools/playwright_dashboard_verification.py
   ```
3. **Read the latest report** in `proof/archive/` (e.g. `dashboard_verification_*.json`).
4. **Summarize for the user:**
   - Passed / failed.
   - List of issues (if any).
   - Path to the screenshots folder so the user can open images in Cursor or Chrome.
5. **Optionally:** list the screenshot filenames (e.g. `api_docs.png`, `streamlit_dashboard.png`) so the user knows what each image is.

No step requires the user to provide a screenshot; the agent drives the browser and captures evidence itself.

---

## 4. Extending checks (more “visual” or structural)

You can extend `tools/playwright_dashboard_verification.py` to:

- **Click** specific tabs or buttons (e.g. “Signals”, “Control Plane”) and take a screenshot after each.
- **Assert** on visible text (e.g. “Dashboard” or “Health: OK”) so failures are in the report.
- **Check for error toasts** or error divs (e.g. `page.locator("[data-testid='error']")` or similar).
- **Compare** a baseline screenshot (e.g. layout regression) if you add a reference image and a diff step.

Then the agent still runs the same single command and gets a richer report and more screenshots.

---

## 5. Where things are saved

| Output | Path (example) |
|--------|-----------------|
| Screenshots | `proof/archive/dashboard_screenshots_20260226_143022/api_docs.png`, `streamlit_dashboard.png`, etc. |
| Report JSON | `proof/archive/dashboard_verification_20260226_143022.json` |

The user can open the PNGs in Cursor (image preview) or in Chrome; the agent uses the JSON to summarize and list issues.

---

## 6. Summary

- **Agent** runs `python tools/playwright_dashboard_verification.py` and reads the generated report.
- **User** verifies using the **same** report and screenshots (no need to send images to the agent).
- **Playwright** does the “Playwright-type” task: drive browser, capture screenshots, run checks, so the agent can do all manual-like verification automatically.
