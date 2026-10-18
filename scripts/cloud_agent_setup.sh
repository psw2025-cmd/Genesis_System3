#!/usr/bin/env bash
# Genesis System3 — Cloud Agent environment install (idempotent).
#
# Prepares the dashboard development experience:
#   - Python 3.11 (matches CI and the production python:3.11-slim backend)
#   - .venv with the FastAPI backend + CI/test dependencies
#   - Frontend (Vite/React) node_modules + production dist so the backend
#     can serve /ui immediately
#
# Safe to run repeatedly. Does NOT start any long-running process
# (servers live in the environment `terminals`).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "[setup] repo root: $REPO_ROOT"

# 1. Python 3.11 toolchain (deadsnakes on Ubuntu when the distro lacks it).
if ! command -v python3.11 >/dev/null 2>&1; then
  echo "[setup] python3.11 not found — installing via apt/deadsnakes"
  sudo apt-get update -qq
  sudo apt-get install -y -qq software-properties-common
  sudo add-apt-repository -y ppa:deadsnakes/ppa
  sudo apt-get update -qq
  sudo apt-get install -y -qq python3.11 python3.11-venv python3.11-dev
fi
echo "[setup] $(python3.11 --version)"

# 2. Python virtual environment + backend/CI dependencies.
if [ ! -x ".venv/bin/python" ]; then
  echo "[setup] creating .venv"
  python3.11 -m venv .venv
fi
# shellcheck disable=SC1091
. .venv/bin/activate
python -m pip install --upgrade pip --quiet
# Install order mirrors CI (.github/workflows/ci.yml): CI/test pins first, then
# the backend runtime requirements so the backend's google-cloud transitive
# requirement (requests>=2.33) resolves last and wins cleanly.
echo "[setup] installing CI/test requirements"
pip install --no-cache-dir -r requirements-ci.txt
echo "[setup] installing backend runtime requirements"
pip install --no-cache-dir -r dashboard/backend/requirements.txt

# 3. Frontend dependencies + production build (served by backend at /ui).
if [ -f dashboard/frontend/package-lock.json ]; then
  echo "[setup] installing frontend dependencies (npm ci)"
  ( cd dashboard/frontend && npm ci --no-audit --no-fund )
  echo "[setup] building frontend (vite build)"
  ( cd dashboard/frontend && npm run build )
fi

echo "[setup] DONE — activate with: source .venv/bin/activate"
