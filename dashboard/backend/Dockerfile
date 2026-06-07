FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
  && rm -rf /var/lib/apt/lists/*

# Copy the repository so dashboard/backend/app.py can import project modules from /app.
COPY . /app/

RUN if [ -f /app/dashboard/backend/requirements.txt ]; then \
      python -m pip install --upgrade pip && \
      pip install --no-cache-dir -r /app/dashboard/backend/requirements.txt ; \
    else \
      echo "No dashboard/backend/requirements.txt found; skipping pip install"; \
    fi

WORKDIR /app

EXPOSE 8000

CMD ["uvicorn", "dashboard.backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
