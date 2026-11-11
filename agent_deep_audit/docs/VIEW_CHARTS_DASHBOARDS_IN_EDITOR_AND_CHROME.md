# Viewing Charts, Graphs & Dashboards in Cursor and Chrome

**Goal:** See all live dashboards and charts **inside Cursor** (no switching to external browser) and optionally in Chrome. Support agent autonomy via APIs so the agent can perform tasks without a human looking at the UI.

---

## 1. Live URLs (Genesis System3)

When services are running (e.g. via Run-All or manually), these URLs serve dashboards and APIs:

| URL | What it is | Charts/UI |
|-----|------------|------------|
| **http://127.0.0.1:8501** | Streamlit dashboard (Run-All: `streamlit run dashboard/app.py`) | Yes – main dashboard, charts, tables |
| **http://127.0.0.1:8000** | FastAPI backend (Run-All: `uvicorn app.main:app`) | API only |
| **http://127.0.0.1:8000/docs** | Swagger UI | Interactive API docs |
| **http://localhost:3000** | React frontend (if you run `npm start` in dashboard/frontend) | Yes – React app UI |

---

## 2. View Live URLs **Inside Cursor Editor**

### Option A: Simple Browser (built-in in VS Code / Cursor)

1. **Open Command Palette:** `Ctrl+Shift+P` (Windows) or `Cmd+Shift+P` (Mac).
2. Type: **`Simple Browser: Show`**.
3. Enter URL when prompted, e.g.:
   - `http://127.0.0.1:8501` (Streamlit dashboard)
   - `http://127.0.0.1:8000/docs` (API docs)

The page opens in a **tab inside Cursor**. You can have multiple Simple Browser tabs (one per URL). Charts and dashboards render as in a normal browser.

**Limitation:** Simple Browser may not support every JavaScript feature (e.g. some WebSocket or complex auth). If something breaks, use Chrome for that URL.

### Option B: Live Preview / Browser Preview extension

- Install an extension that embeds a browser in the editor, e.g.:
  - **Live Preview** (Microsoft): `ms-vscode.live-server` – can show a live URL in a side panel.
  - **Browser Preview** (if available in Cursor): embeds Chromium in a VS Code tab.

Then open the extension’s panel and navigate to `http://127.0.0.1:8501` or `http://127.0.0.1:8000/docs`. You get a full browser inside the editor.

### Option C: Jupyter notebooks in Cursor

- For **charts generated in Python** (Plotly, Matplotlib, etc.):
  - Use a **Jupyter notebook** (`.ipynb`) in the project.
  - Run cells that fetch data and plot; charts render **inline** in the notebook.
- The agent can create or edit notebooks and run cells; you see updated charts in the same editor.

---

## 3. View in Google Chrome (external)

- Start your services (e.g. Run-All or your usual start script).
- Open Chrome and go to:
  - **Streamlit:** http://127.0.0.1:8501  
  - **API docs:** http://127.0.0.1:8000/docs  
  - **React (if running):** http://localhost:3000  

Some scripts (e.g. `run_local.bat`) already start Chrome with `http://localhost:3000`. You can add a small script or task that opens the URLs you care about (e.g. 8501 + 8000/docs) in Chrome tabs.

---

## 4. One Place to Open All Live URLs

### In Cursor: Run Task (opens in your default browser, e.g. Chrome)

- **Terminal → Run Task…** (or `Ctrl+Shift+P` → “Tasks: Run Task”).
- Choose:
  - **Open Streamlit Dashboard (in default browser)** → opens http://127.0.0.1:8501
  - **Open Backend API Docs (in default browser)** → opens http://127.0.0.1:8000/docs
  - **Open all live URLs** → opens both in parallel

Tasks are defined in **`.vscode/tasks.json`**. On Windows they use `start <url>` (default browser); on Mac `open <url>`; on Linux `xdg-open <url>`.

### In-editor (no Chrome): Simple Browser

- `Ctrl+Shift+P` → **Simple Browser: Show** → enter `http://127.0.0.1:8501` or `http://127.0.0.1:8000/docs`.
- Charts and dashboards render inside a Cursor tab.

---

## 5. Agent Autonomy: Don’t Rely on “Seeing” the Dashboard

The Cursor **agent cannot see or click** the dashboard. It can:

- Run **terminal commands** (start/stop services, run scripts).
- **Edit files** and **read** project files.
- **Call HTTP APIs** if your backend exposes them.

So for **full autonomous tasks without user**:

1. **Expose every important action as an API**  
   - Dashboard actions (e.g. “run phase 231–260”, “generate report”, “refresh data”) should be callable via **POST/GET** on the FastAPI backend (e.g. `http://127.0.0.1:8000/api/...`).  
   - The agent can then run:  
     `curl -X POST http://127.0.0.1:8000/api/run-proof`  
     or use a small Python script that calls `requests.post(...)`.

2. **Use scripts for heavy or multi-step work**  
   - The agent already runs scripts like `python proof/run_231_260_proof.py` or `python tools/verify_cursor_agent_bugs.py`.  
   - Any “task” that the dashboard triggers (e.g. “run governance”, “generate chart data”) should also be runnable as a **CLI or script** so the agent can run it without needing the UI.

3. **Charts and reports as files**  
   - If the agent needs to “produce a chart”, the flow should be: script runs → generates image or HTML in `storage/`, `reports/`, or `proof/` → agent (or you) can open that file in Cursor.  
   - You can use **Simple Browser** to open a **local HTML file** (e.g. `reports/dashboard_snapshot.html`) that contains the chart, so you still see it in the editor.

4. **Health and status via API**  
   - Backend should expose e.g. `/api/health`, `/api/status`, `/api/agent/tasks` so the agent can check “is the system up?” and “what’s the last run result?” without opening the dashboard.

---

## 6. Recommendations

| What | Recommendation |
|------|-----------------|
| **See Streamlit/React in Cursor** | Use **Simple Browser** (Cmd/Ctrl+Shift+P → “Simple Browser: Show”) and open `http://127.0.0.1:8501` and `http://127.0.0.1:8000/docs`. Add a task or keybinding if you use them often. |
| **See same in Chrome** | Open the same URLs in Chrome; use a small script or task to open 8501 + 8000/docs in one go. |
| **Charts in editor** | For Python-generated charts: use **Jupyter** in Cursor (inline). For app dashboards: use Simple Browser or Live Preview to the app URL. For static reports: save as image/HTML and open the file in Cursor. |
| **Agent does everything without user** | (1) Expose dashboard actions as **backend APIs**. (2) Keep using **CLI/scripts** for proof and phase runs. (3) Agent calls APIs + runs scripts; no need to “see” the dashboard. (4) Optional: add an **agent-only** API route like `POST /api/agent/run-task` that runs a named task (e.g. `run_231_260_proof`) and returns the result JSON. |

---

## 7. Quick reference: open in Cursor

1. `Ctrl+Shift+P` → **Simple Browser: Show**  
2. URL: **http://127.0.0.1:8501** (Streamlit) or **http://127.0.0.1:8000/docs** (API).  
3. Charts and dashboards appear in the editor tab.  
4. For agent autonomy: add backend APIs for every action the dashboard does; agent uses those + existing scripts.
