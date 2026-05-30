FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
  && rm -rf /var/lib/apt/lists/*

COPY dashboard/backend/ /app/dashboard/backend/

RUN if [ -f /app/dashboard/backend/requirements.txt ]; then \
      python -m pip install --upgrade pip && \
      pip install --no-cache-dir -r /app/dashboard/backend/requirements.txt ; \
    else \
      echo "No dashboard/backend/requirements.txt found; skipping pip install"; \
    fi

WORKDIR /app/dashboard/backend

EXPOSE 8000

CMD ["python", "-m", "http.server", "8000"]
