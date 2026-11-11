import os
import sys
import time
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.environ["BROKER_SELF_HEAL_TOKEN_REFRESH"] = "0"
os.environ["SYSTEM3_MODE"] = "analyze"
os.environ["PAPER_MODE"] = "1"
os.environ["LIVE_TRADING_ENABLED"] = "0"

while True:
    print("[persistent_backend] Starting uvicorn...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "dashboard.backend.app:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=str(ROOT)
    )
    proc.wait()
    print("[persistent_backend] Uvicorn exited, restarting in 1s...")
    time.sleep(1)
