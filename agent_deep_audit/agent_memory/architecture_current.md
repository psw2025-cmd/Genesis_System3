# Current Architecture - System3 Ultra Dashboard

## System Overview

```
┌─────────────────────────────────────────────────┐
│         System3 Ultra Dashboard                  │
│                                                 │
│  ┌──────────────┐      ┌──────────────┐        │
│  │   Frontend   │──────│   Backend    │        │
│  │  (React)     │      │  (FastAPI)   │        │
│  │  :3000       │      │  :8000       │        │
│  └──────────────┘      └──────────────┘        │
│         │                      │                │
│         │                      │                │
│         └──────────┬───────────┘                │
│                    │                            │
│            ┌───────▼────────┐                   │
│            │  SSOT Store    │                   │
│            │  (State Sync)  │                   │
│            └───────┬────────┘                   │
│                    │                            │
│         ┌──────────┼──────────┐                 │
│         │          │          │                 │
│    ┌────▼───┐ ┌───▼────┐ ┌───▼────┐           │
│    │ Broker │ │Synthetic│ │ Runner │           │
│    │ (Angel)│ │  Data   │ │ Engine │           │
│    └────────┘ └─────────┘ └────────┘           │
└─────────────────────────────────────────────────┘
```

## Data Flow

1. **Runner Cycle:**
   - Fetch data (broker or synthetic)
   - Run QC
   - Generate signals
   - Update positions
   - Compute risk
   - Create SSOT snapshot (state_version++)

2. **Frontend:**
   - Polls `/api/state` every 3-5 seconds
   - All pages read from same SSOT
   - Shows consistent data

3. **State Sync:**
   - Background service syncs from files every 5 seconds
   - Updates SSOT store
   - Auto-generates alerts

## Current State

### ✅ Completed
- SSOT core (runtime_state_store.py)
- State sync service
- Frontend SSOT integration
- Synthetic data realism
- Risk limit fixes
- UI fixes (Invalid Date, Close All, etc.)

### 🔄 In Progress
- Electron desktop app
- Upgrade Agent
- Proof Pack

### 📋 Pending
- Control page
- Agent Console
- Full test suite
- EXE build

## Target Architecture (Desktop App)

```
┌─────────────────────────────────────────────┐
│      Electron Desktop App (EXE)              │
│                                              │
│  ┌──────────────────────────────────────┐  │
│  │      React UI (Embedded)              │  │
│  │  - Overview                           │  │
│  │  - Signals                            │  │
│  │  - Trading                            │  │
│  │  - Risk                                │  │
│  │  - ML                                  │  │
│  │  - Alerts                              │  │
│  │  - Chain                               │  │
│  │  - Control                             │  │
│  │  - Agent Console                       │  │
│  └──────────────────────────────────────┘  │
│              │                               │
│              │ (IPC)                         │
│  ┌───────────▼───────────┐                  │
│  │  Electron Main        │                  │
│  │  - Auto-start backend │                  │
│  │  - Tray icon          │                  │
│  │  - Notifications      │                  │
│  └───────────┬───────────┘                  │
│              │                               │
│  ┌───────────▼───────────┐                  │
│  │  Backend Service       │                  │
│  │  (Child Process)       │                  │
│  │  - FastAPI             │                  │
│  │  - SSOT                │                  │
│  │  - Runner Engine       │                  │
│  └───────────────────────┘                  │
│                                              │
│  ┌───────────────────────┐                  │
│  │  Upgrade Agent         │                  │
│  │  - Watches issues      │                  │
│  │  - Plans upgrades      │                  │
│  │  - Tests & deploys     │                  │
│  └───────────────────────┘                  │
└─────────────────────────────────────────────┘
```
