#!/usr/bin/env bash
# Runs automatically when Codespace starts or resumes from sleep.
# Restarts Dhan token daemons without needing a terminal to be opened.
# Called by .devcontainer/devcontainer.json → postStartCommand.

set -euo pipefail

PROJ="/workspaces/Genesis_System3"
PY=$(which python3 2>/dev/null || which python 2>/dev/null || echo "")
LOG="$PROJ/logs/codespace_startup.log"

mkdir -p "$PROJ/logs"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Codespace postStartCommand: starting daemons" >> "$LOG"

if [ -z "$PY" ] || [ ! -d "$PROJ" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: python or project not found" >>"$LOG"
    exit 0  # non-blocking — don't fail Codespace start
fi

# Ensure python-dotenv and core deps are installed (survives Codespace resume where
# postCreateCommand doesn't re-run but packages may be missing after env reset)
if ! "$PY" -c "import dotenv" 2>/dev/null; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Installing requirements (dotenv missing)..." >> "$LOG"
    "$PY" -m pip install -q -r "$PROJ/requirements.txt" >> "$LOG" 2>&1 || true
fi

# Layer 0: run full startup check (token refresh + daemon + watchdog)
"$PY" "$PROJ/scripts/dhan_startup_check.py" >> "$LOG" 2>&1 || true

sleep 5  # allow spawned processes to register with the OS before pgrep checks

# Layer 1 fallback: token daemon
if ! pgrep -f "dhan_token_auto_refresh.py" > /dev/null 2>&1; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting token daemon (fallback)" >> "$LOG"
    nohup "$PY" -u "$PROJ/scripts/dhan_token_auto_refresh.py" \
        >> "$PROJ/logs/dhan_token_daemon.log" 2>&1 &
    disown $!
fi

# Layer 2 fallback: watchdog
if ! pgrep -f "dhan_watchdog_runner.py" > /dev/null 2>&1; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting watchdog (fallback)" >> "$LOG"
    nohup "$PY" -u "$PROJ/scripts/dhan_watchdog_runner.py" \
        >> "$PROJ/logs/dhan_watchdog.log" 2>&1 &
    disown $!
fi

# Layer 3: job scheduler daemon (bhavcopy, gain rank, signal engine, auto-retrain)
if ! pgrep -f "system3_phase82_job_scheduler.*--daemon" > /dev/null 2>&1; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting job scheduler daemon" >> "$LOG"
    nohup "$PY" -u "$PROJ/core/engine/system3_phase82_job_scheduler.py" --daemon \
        >> "$PROJ/logs/job_scheduler.log" 2>&1 &
    disown $!
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] postStartCommand complete" >> "$LOG"
