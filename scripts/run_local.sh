#!/bin/bash
# ====================================================================
# GENESIS SYSTEM3 - ONE-CLICK RUN SCRIPT (Linux/Mac)
# ====================================================================
# This script starts the complete system with all checks and fixes
# ====================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.."
cd "$SCRIPT_DIR"

echo ""
echo "===================================================================="
echo "  GENESIS SYSTEM3 - ONE-CLICK STARTUP"
echo "===================================================================="
echo ""

# Step 1: Run doctor check
echo "[1/4] Running system health check..."
python3 scripts/doctor.py || echo "[WARNING] Some checks failed. Continuing anyway..."

# Step 2: Install/verify dependencies
echo ""
echo "[2/4] Verifying dependencies..."
if [ ! -d "venv" ]; then
    echo "  Creating virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt
pip install -q uvicorn[standard] fastapi

# Step 3: Check and clear ports
echo ""
echo "[3/4] Checking ports..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
sleep 2

# Step 4: Start services
echo ""
echo "[4/4] Starting services..."
echo ""

# Start backend
echo "  Starting backend (port 8000)..."
cd dashboard/backend
source ../../venv/bin/activate
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload > ../../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ../..
sleep 8

# Start frontend
echo "  Starting frontend (port 3000)..."
cd dashboard/frontend
if [ ! -d "node_modules" ]; then
    echo "    Installing frontend dependencies..."
    npm install --quiet
fi
npm run dev -- --host 0.0.0.0 > ../../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ../..
sleep 12

# Verify
echo ""
echo "  Verifying services..."
sleep 3
curl -s http://localhost:8000/api/health > /dev/null && echo "  [OK] Backend: RUNNING" || echo "  [WARN] Backend: Starting..."
curl -s http://localhost:3000 > /dev/null && echo "  [OK] Frontend: RUNNING" || echo "  [WARN] Frontend: Starting..."

echo ""
echo "===================================================================="
echo "  SYSTEM STARTED"
echo "===================================================================="
echo ""
echo "  Dashboard: http://localhost:3000"
echo "  Backend API: http://localhost:8000"
echo ""
echo "  Backend PID: $BACKEND_PID"
echo "  Frontend PID: $FRONTEND_PID"
echo ""
echo "  Logs:"
echo "    Backend: logs/backend.log"
echo "    Frontend: logs/frontend.log"
echo ""
echo "  Press Ctrl+C to stop all services..."
echo ""

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
