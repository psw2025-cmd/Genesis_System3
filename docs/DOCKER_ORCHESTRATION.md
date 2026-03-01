# Docker Orchestration (P2.1)

Startup orchestration for Genesis System3 dashboard via Docker Compose.

## Prerequisites

- Docker Desktop (or Docker Engine + Docker Compose)
- Git (for cloning)

## Quick Start

```powershell
# From project root
docker compose up -d

# Backend:  http://localhost:8000
# Frontend: http://localhost:3000
# Health:   http://localhost:8000/api/health
```

## Services

| Service  | Port | Description                    |
|----------|------|--------------------------------|
| backend  | 8000 | FastAPI + uvicorn             |
| frontend | 3000 | React/Vite (built, served by nginx) |

**Endpoints:** `/api/health` (deep health), `/metrics` (Prometheus)

## Volumes

- `./outputs` → backend reads/writes health.json, chain data, etc.
- `./logs` → backend writes logs
- `./config` → read-only broker config (if present)

## Commands

```powershell
# Start
docker compose up -d

# Stop
docker compose down

# Rebuild after code changes
docker compose up -d --build

# View logs
docker compose logs -f backend
docker compose logs -f frontend
```

## Health Check

Backend includes a healthcheck. Frontend waits for backend to be healthy before starting.

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing
```

## Notes

- **Broker credentials**: Mount `config/` with your AngelOne config. Backend runs in REAL_ONLY mode.
- **Trading system**: Not included by default. Run separately: `python option_chain_automation_master.py`
- **Dev mode**: For hot-reload, use `RESTART_DASHBOARD.bat` or `START_FULL_SYSTEM_WITH_DASHBOARD.ps1` instead of Docker.
