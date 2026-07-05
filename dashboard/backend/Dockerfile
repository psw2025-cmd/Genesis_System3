# ── Stage 1: Build React frontend (Node.js only needed here) ──────────
FROM node:20-slim AS frontend-builder
WORKDIR /app/dashboard/frontend
COPY dashboard/frontend/package*.json ./
RUN npm install --legacy-peer-deps 2>/dev/null
COPY dashboard/frontend/ ./
RUN npm run build && echo "[build] React frontend built successfully" ||     echo "[build] React frontend build failed"

# ── Stage 2: Runtime (Python only, no Node.js) ────────────────────────
# Node.js removed from runtime image — saves ~200MB RAM on free tier.
# React dist is copied from stage 1, so /ui still serves correctly.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends     curl   && rm -rf /var/lib/apt/lists/*

COPY . /app/

# Copy pre-built React dist from stage 1 (no Node.js in runtime)
COPY --from=frontend-builder /app/dashboard/frontend/dist /app/dashboard/frontend/dist

RUN if [ -f /app/dashboard/backend/requirements.txt ]; then       python -m pip install --upgrade pip &&       pip install --no-cache-dir -r /app/dashboard/backend/requirements.txt ;     else       echo "No requirements.txt found; skipping pip install";     fi

RUN python scripts/sync_dhan_instruments_master.py --force ||     python -c "print('[build] instrument sync skipped — will retry at startup')"

WORKDIR /app

RUN useradd --create-home --shell /bin/false appuser   && chown -R appuser:appuser /app

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3   CMD curl -fsS http://localhost:8000/api/health || exit 1

# Memory-safe uvicorn config:
# --limit-max-requests 1000: restart after 1000 requests (prevents leaks)
# --timeout-keep-alive 20: faster connection cleanup
# --limit-concurrency 50: allow dashboard burst polling without uvicorn 503s
CMD ["uvicorn", "dashboard.backend.app:app",      "--host", "0.0.0.0", "--port", "8000",      "--workers", "1",      "--timeout-keep-alive", "20",      "--limit-max-requests", "1000",      "--limit-concurrency", "50"]
