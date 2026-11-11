"""
Restart port 8008 ASGI server with Dhan credentials loaded into the process environment.
Spawns as a fully detached Windows process so it persists indefinitely.
"""
import os
import subprocess
import time
import urllib.request
import json
from pathlib import Path

ROOT = Path("c:/Genesis_System3_clean")
APP_DIR = ROOT / "content" / "app"
if not APP_DIR.exists():
    APP_DIR = Path("c:/content/app")
SECRETS_FILE = ROOT / ".secrets" / "dhan.env"

# 1. Load credentials
env_vars = dict(os.environ)
env_vars["PYTHONPATH"] = str(ROOT)
if SECRETS_FILE.is_file():
    for line in SECRETS_FILE.read_text(encoding="utf-8-sig").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        env_vars[k.strip()] = v.strip().strip('"').strip("'")

# 2. Kill existing on 8008
cmd = "netstat -ano | findstr :8008 | findstr LISTENING"
output = subprocess.getoutput(cmd)
for line in output.strip().splitlines():
    parts = line.strip().split()
    if len(parts) >= 5 and "LISTENING" in parts:
        pid = int(parts[-1])
        print(f"Killing PID {pid} on port 8008...")
        subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True)

time.sleep(2)

# 3. Launch uvicorn as fully detached subprocess with dedicated log
DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200

log_out = open(APP_DIR / "uvicorn_detached.log", "a", encoding="utf-8")

proc = subprocess.Popen(
    [r"C:\Genesis_System3_clean\.venv\Scripts\python.exe", "-m", "uvicorn", "app:app", "--port", "8008", "--host", "127.0.0.1"],
    cwd=str(APP_DIR),
    env=env_vars,
    creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
    close_fds=True,
    stdout=log_out,
    stderr=log_out
)
print(f"Launched detached uvicorn process PID: {proc.pid}")

# 4. Wait for server to bind and verify
url = "http://127.0.0.1:8008/api/verified-market"
for attempt in range(10):
    time.sleep(1)
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read())
            print(f"Verification successful at attempt {attempt+1}:")
            print("  State:", data.get("state"))
            print("  Exchange Quotes Verified:", data.get("exchange_quotes_verified"))
            break
    except Exception as e:
        if attempt == 9:
            print("Verification request failed:", e)
