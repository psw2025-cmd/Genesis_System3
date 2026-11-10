#!/usr/bin/env bash
# Genesis System3 Codespace startup.
#
# Dhan token minting is intentionally NOT performed here. Google Cloud Run Job
# `genesis-system3-dhan-token-rotate` is the single token-generation authority.
# Local/Codespace token daemons previously created a split-brain condition where
# a newly minted local token invalidated the token stored in Google Secret
# Manager, leaving the production dashboard disconnected.

set -euo pipefail

PROJ="/workspaces/Genesis_System3"
PY=$(which python3 2>/dev/null || which python 2>/dev/null || echo "")
LOG="$PROJ/logs/codespace_startup.log"

mkdir -p "$PROJ/logs"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Codespace postStartCommand: GCP is sole Dhan token authority" >> "$LOG"

if [ -z "$PY" ] || [ ! -d "$PROJ" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: python or project not found" >> "$LOG"
    exit 0
fi

# Permanently stop legacy local token writers if a resumed Codespace still has
# processes from an older revision. These processes are not required for
# analyzer jobs and must never mint/renew the production Dhan token.
pkill -f "dhan_token_auto_refresh.py" >/dev/null 2>&1 || true
pkill -f "dhan_watchdog_runner.py" >/dev/null 2>&1 || true
pkill -f "core.brokers.dhan.token_watchdog" >/dev/null 2>&1 || true

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Legacy Dhan token daemons stopped; no local token generation allowed" >> "$LOG"

# Keep the unrelated analyzer scheduler available for developer work.
if ! pgrep -f "system3_phase82_job_scheduler.*--daemon" > /dev/null 2>&1; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting analyzer job scheduler daemon" >> "$LOG"
    nohup "$PY" -u "$PROJ/core/engine/system3_phase82_job_scheduler.py" --daemon \
        >> "$PROJ/logs/job_scheduler.log" 2>&1 &
    disown $!
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] postStartCommand complete — LIVE remains external/locked" >> "$LOG"
