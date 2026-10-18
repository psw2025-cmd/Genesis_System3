# SYSTEM3_ROOT_DOCKERFILE_NONPRODUCTION: legacy/developer image ONLY.
# DO NOT use this file for GCP System3 Cloud Run production. It uses the
# legacy backend app and a fixed port, unlike the audited Cloud Run launcher.
# Canonical candidate image path: dashboard/backend/Dockerfile (repo-root context).
# Cloud build/deploy still requires separate explicit owner authorization.
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    SYSTEM3_REAL_ONLY=1 \
    LIVE_TRADING_ENABLED=0 \
    SYSTEM3_LIVE_TRADING_ALLOWED=0

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "dashboard.backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
