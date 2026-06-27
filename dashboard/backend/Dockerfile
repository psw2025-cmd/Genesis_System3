FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    nodejs \
    npm \
  && rm -rf /var/lib/apt/lists/*

# Copy the repository so dashboard/backend/app.py can import project modules from /app.
COPY . /app/

# Build React frontend inside Docker (ensures dist/ is always fresh)
RUN cd /app/dashboard/frontend && \
    npm install --legacy-peer-deps 2>/dev/null && \
    npm run build && \
    echo "[build] React frontend built successfully" || \
    echo "[build] React frontend build failed — will serve legacy Vue"

RUN if [ -f /app/dashboard/backend/requirements.txt ]; then \
      python -m pip install --upgrade pip && \
      pip install --no-cache-dir -r /app/dashboard/backend/requirements.txt ; \
    else \
      echo "No dashboard/backend/requirements.txt found; skipping pip install"; \
    fi

# Bake official Dhan instrument master into image (production — no missing JSON at runtime)
RUN python scripts/sync_dhan_instruments_master.py --force || \
    python -c "print('[build] instrument sync skipped — will retry at startup')"

WORKDIR /app

# Run as non-root. The app writes to many directories across the repo at
# runtime (storage/, outputs/, logs/, state/, config/, reports/ etc.) so
# the whole tree is chown'd rather than risking a permission error on a
# path missed by an explicit list.
RUN useradd --create-home --shell /bin/false appuser \
  && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -fsS http://localhost:8000/api/health || exit 1

CMD ["uvicorn", "dashboard.backend.app:app", "--host", "0.0.0.0", "--port", "8000", "--limit-max-requests", "200"]
