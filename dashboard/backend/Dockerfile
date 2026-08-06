FROM node:20-slim AS frontend-builder
WORKDIR /app/dashboard/frontend

ARG SYSTEM3_FRONTEND_BUILD_EPOCH=20260806_gcp_token_rotation_proof
ENV SYSTEM3_FRONTEND_BUILD_EPOCH=${SYSTEM3_FRONTEND_BUILD_EPOCH}

COPY dashboard/frontend/package*.json ./
RUN npm ci --legacy-peer-deps
COPY dashboard/frontend/ ./
RUN printf '%s\n' "$SYSTEM3_FRONTEND_BUILD_EPOCH" > .system3-frontend-build-epoch \
    && npm run build \
    && test -f dist/index.html \
    && grep -R -q --include='*.js' 'Sim Live' dist/assets \
    && grep -R -q --include='*.js' 'CLOUD BUILD' dist/assets \
    && grep -R -q --include='*.js' 'SESSION SNAPSHOT' dist/assets \
    && grep -R -q --include='*.js' 'TOKEN ROTATION PROOF' dist/assets \
    && sidebar_sha="$(sha256sum src/components/Sidebar.tsx | awk '{print $1}')" \
    && printf '{"schema":2,"sidebar_sha256":"%s","sim_live_required":true,"live_trading_enabled":false,"cloud_build_badge":true,"session_snapshot_ui":true,"token_rotation_proof_ui":true,"build_epoch":"%s"}\n' "$sidebar_sha" "$SYSTEM3_FRONTEND_BUILD_EPOCH" > dist/assets/deploy-provenance.json

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY . /app/

RUN rm -rf /app/dashboard/frontend/dist
COPY --from=frontend-builder /app/dashboard/frontend/dist /app/dashboard/frontend/dist
RUN test -f /app/dashboard/frontend/dist/index.html \
    && test -f /app/dashboard/frontend/dist/assets/deploy-provenance.json \
    && grep -R -q --include='*.js' 'Sim Live' /app/dashboard/frontend/dist/assets \
    && grep -R -q --include='*.js' 'TOKEN ROTATION PROOF' /app/dashboard/frontend/dist/assets

RUN if [ -f /app/dashboard/backend/requirements.txt ]; then \
      python -m pip install --upgrade pip && \
      pip install --no-cache-dir -r /app/dashboard/backend/requirements.txt ; \
    else \
      echo "No requirements.txt found; skipping pip install"; \
    fi

RUN python scripts/sync_dhan_instruments_master.py --force || \
    python -c "print('[build] instrument sync skipped — will retry at startup')"

RUN useradd --create-home --shell /bin/false appuser \
  && chown -R appuser:appuser /app

USER appuser
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -fsS "http://localhost:${PORT:-8080}/api/health" || exit 1

CMD ["python", "scripts/start_cloud_run.py"]
