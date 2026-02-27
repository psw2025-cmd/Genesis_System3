# Agent Console – Full Folder & Code Investigation

This document maps what you see in the **Agent Console** tab to the codebase and folder structure.

---

## 1. What You See in the App

| UI Element | Source |
|------------|--------|
| **Title** "Agent Console" | Frontend component title |
| **Download Proof Pack** button | Triggers proof-pack download (ZIP) |
| **Pause Agent** button | Toggles upgrade agent auto-apply (pause/resume) |
| **Version** "1.0.0" | Hardcoded in `AgentConsole.tsx` |
| **Build Date** | `new Date().toLocaleDateString()` (today in browser) |
| **Run ID** (e.g. RUN_001) | From `agent_memory/tasks.json` → `run_id` |
| **Agent Memory Status** (Total Tasks, Completed, In Progress, Last Updated) | From `agent_memory/tasks.json` → `tasks[]` and `last_updated` |

---

## 2. Frontend (What Renders the Screen)

| File | Role |
|------|------|
| `dashboard/frontend/src/components/AgentConsole.tsx` | Full Agent Console UI: header, buttons, System Version card, Agent Memory Status card, Upgrade Plan, Detected Issues. |
| `dashboard/frontend/src/App.tsx` | Route `/agent` → `<AgentConsole />`. Nav link "Agent" in the top bar. |

**Data flow (UI):**

- **Electron app:** Uses `window.electronAPI.getAgentMemory()` → main process reads `agent_memory/tasks.json` and returns it.
- **Browser / no Electron:** Uses HTTP `GET ${API_BASE}/api/agent/memory` → backend reads same file and returns JSON.
- **Run ID:** `agentMemory?.run_id` (from that JSON).
- **Total/Completed/In Progress:** Derived from `agentMemory.tasks` (count, filter by `status === 'completed'` or `'in_progress'`).
- **Last Updated:** `agentMemory.last_updated`.

**Buttons:**

- **Download Proof Pack:** Electron → `downloadProofPack` IPC, then opens `/api/proof-pack` in browser; otherwise opens `/api/proof-pack` directly. Backend builds a ZIP from `agent_memory` and serves it.
- **Pause Agent:** `POST /api/agent/pause` → backend toggles `upgrade_agent.auto_apply_enabled`.

---

## 3. Backend (API & Data)

| File | Role |
|------|------|
| `dashboard/backend/app.py` | Defines all Agent and proof-pack endpoints. |

**Relevant endpoints:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/agent/memory` | GET | Returns contents of `agent_memory/tasks.json` (run_id, tasks, last_updated). |
| `/api/agent/issues` | GET | Returns detected issues (currently returns `issues: []`). |
| `/api/agent/upgrade-plan` | GET | Returns latest upgrade plan from `agent_memory/upgrade_plan_*.json` if status is draft/ready. |
| `/api/agent/pause` | POST | Toggles upgrade agent pause (auto_apply on/off). |
| `/api/proof-pack` | GET | Builds ZIP via `upgrade_agent.create_proof_pack()` and returns it as download. |

**Upgrade agent (used by proof-pack and plans):**

- `dashboard/backend/upgrade_agent.py` – `UpgradeAgent` class, uses `agent_memory` directory.
- `create_proof_pack()` writes a ZIP under `agent_memory/proof_packs/` and includes e.g. `tasks.json`, `plan.md`, and other files from `agent_memory`.

---

## 4. Agent Memory Folder (Data Behind the Screen)

**Location:** `C:\Genesis_System3\agent_memory\` (project root).  
In the **installed** Electron app, this is the packaged copy under app resources (e.g. `resources/agent_memory`).

| Path | Purpose |
|------|---------|
| `agent_memory/tasks.json` | **Main data for Agent Console:** `run_id`, `started`, `last_updated`, `tasks[]` (id, status, description, completed_at, etc.). |
| `agent_memory/plan.md` | Upgrade plan (text). |
| `agent_memory/architecture_current.md` | Architecture snapshot. |
| `agent_memory/inventory.md` | Inventory. |
| `agent_memory/decisions.log` | Decisions log. |
| `agent_memory/upgrade_plan_*.json` | Upgrade plans (draft/ready/applied). Used by Upgrade Plan section and apply/rollback. |
| `agent_memory/test_runs/` | Test results per plan (`test_<plan_id>.json`). |
| `agent_memory/proof_packs/` | Generated proof-pack ZIPs. |
| `agent_memory/diffs/` | Diffs. |
| `agent_memory/state_snapshots/` | State snapshots. |

**Why you see "RUN_001", 10 tasks, 6 completed, 1 in progress:**

- `tasks.json` contains `"run_id": "RUN_001"` and 10 task objects.
- Six have `"status": "completed"`, one has `"status": "in_progress"` (e.g. `electron_app`), rest are `"pending"`.
- `last_updated` in that file is what the UI shows as "Last Updated".

---

## 5. Desktop App (Electron)

| File | Role |
|------|------|
| `desktop_app/main.js` | Sets `AGENT_MEMORY_DIR` (dev: `../agent_memory`, installed: `resources/agent_memory`). Implements `get-agent-memory` (reads `tasks.json` from that dir) and `download-proof-pack` (triggers backend or creates pack). |
| `desktop_app/preload.js` | Exposes `getAgentMemory`, `downloadProofPack`, etc., to the renderer (AgentConsole). |

When the app runs installed, the **agent_memory** folder is the one bundled in the installer (from `extraResources` in `desktop_app/package.json`). So the same structure and `tasks.json` you have in the project root are what the packaged app uses until the user or the app writes new files there.

---

## 6. End-to-End Flow Summary

1. You open the app → Electron loads the React app → you click **Agent** in the nav.
2. **AgentConsole.tsx** mounts and calls `getAgentMemory()` (Electron) or `GET /api/agent/memory` (backend).
3. Data comes from **agent_memory/tasks.json** (run_id, tasks, last_updated).
4. UI shows **System Version** (version 1.0.0, build date from browser, Run ID from JSON) and **Agent Memory Status** (counts from `tasks`).
5. **Download Proof Pack** → backend (or Electron) creates a ZIP from `agent_memory` and serves it via `/api/proof-pack`.
6. **Pause Agent** → `POST /api/agent/pause` toggles the upgrade agent’s auto-apply flag.

---

## 7. Quick Reference – Important Paths

| What | Path |
|------|------|
| Agent Console UI | `dashboard/frontend/src/components/AgentConsole.tsx` |
| Agent API & proof-pack | `dashboard/backend/app.py` (search for `/api/agent` and `/api/proof-pack`) |
| Upgrade agent logic | `dashboard/backend/upgrade_agent.py` |
| Agent memory data (run id, tasks) | `agent_memory/tasks.json` |
| Electron agent memory & proof pack | `desktop_app/main.js` (AGENT_MEMORY_DIR, get-agent-memory, download-proof-pack), `desktop_app/preload.js` |

To change what the Agent Console shows (e.g. Run ID, task counts, or add new fields), you edit either the frontend (AgentConsole.tsx), the backend (app.py and/or upgrade_agent.py), or the data in **agent_memory/tasks.json** (and/or other files in **agent_memory/**).
