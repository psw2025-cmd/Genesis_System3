FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Kolkata
ENV SYSTEM3_REAL_ONLY=1
ENV PORT=8000

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install backend dependencies first for Docker layer caching.
COPY dashboard/backend/requirements.txt dashboard/backend/requirements.txt

RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r dashboard/backend/requirements.txt \
    && python -m pip install --no-cache-dir pytz numpy

# Full repo context is required because dashboard/backend/app.py imports root/core/src modules.
COPY . .

EXPOSE 8000

CMD ["uvicorn", "dashboard.backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
