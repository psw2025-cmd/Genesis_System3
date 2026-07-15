# ── Stage 1: Build React frontend (Node.js only needed here) ──────────
FROM node:20-slim AS frontend-builder
WORKDIR /app/dashboard/frontend
COPY dashboard/frontend/package*.json ./
# Use the committed lockfile so Render cannot resolve a different dependency
# graph from the one reviewed in the repository.
RUN npm ci --legacy-peer-deps
COPY dashboard/frontend/ ./
# Fail the image build if the current React source cannot compile or if the
# analyzer-only Sim Live control is absent from the generated bundle. This
# prevents stale/incomplete frontend assets from being published as healthy.
# A deterministic, non-secret source fingerprint is also published with the
# static assets so live proof can distinguish deployment drift from UI failure.
RUN npm run build \
    && test -f dist/index.html \
    && grep -R -q --include='*.js' 'Sim Live' dist/assets \
    && sidebar_sha="$(sha256sum src/components/Sidebar.tsx | awk '{print $1}')" \
    && printf '{"schema":1,"sidebar_sha256":"%s","sim_live_required":true,"live_trading_enabled":false}\n' "$sidebar_sha" > dist/deploy-provenance.json

# ── Stage 2: Runtime (Python only, no Node.js) ────────────────────────
# Node.js removed from runtime image — saves ~200MB RAM on free tier.
# React dist is copied from stage 1, so /ui still serves correctly.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY . /app/

# Copy only the frontend produced by this image build. The builder stage is
# authoritative; a failed or missing build cannot silently fall back to a
# repository-carried dist directory.
RUN rm -rf /app/dashboard/frontend/dist
COPY --from=frontend-builder /app/dashboard/frontend/dist /app/dashboard/frontend/dist
RUN test -f /app/dashboard/frontend/dist/index.html \
    && test -f /app/dashboard/frontend/dist/deploy-provenance.json \
    && grep -R -q --include='*.js' 'Sim Live' /app/dashboard/frontend/dist/assets

RUN if [ -f /app/dashboard/backend/requirements.txt ]; then \
      python -m pip install --upgrade pip && \
      pip install --no-cache-dir -r /app/dashboard/backend/requirements.txt ; \
    else \
      echo "No requirements.txt found; skipping pip install"; \
    fi

RUN python scripts/sync_dhan_instruments_master.py --force || \
    python -c "print('[build] instrument sync skipped — will retry at startup')"

WORKDIR /app

RUN useradd --create-home --shell /bin/false appuser \
  && chown -R appuser:appuser /app

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -fsS http://localhost:8000/api/health || exit 1

# Memory-safe uvicorn config:
# --limit-max-requests 1000: restart after 1000 requests (prevents leaks)
# --timeout-keep-alive 20: faster connection cleanup
# --limit-concurrency 50: allow dashboard burst polling without uvicorn 503s
CMD ["uvicorn", "dashboard.backend.app:app", \
     "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "1", \
     "--timeout-keep-alive", "20", \
     "--limit-max-requests", "1000", \
     "--limit-concurrency", "50"]