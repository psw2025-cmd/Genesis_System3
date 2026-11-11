import urllib.request
import json

TOKEN = "8779214909:AAGR2ibZRpX3gakAZ9H56RySZKlUodLycwI"
url = f"https://api.telegram.org/bot{TOKEN}/setMyCommands"

payload = {
    "commands": [
        {"command": "status", "description": "System health, uptime & feed status"},
        {"command": "risk", "description": "RMS limits, daily stop-loss & margin"},
        {"command": "pnl", "description": "Paper trading P&L & filled ledger"},
        {"command": "chains", "description": "Live ATM strikes, PCR & options chain"},
        {"command": "help", "description": "Genesis manual & full command menu"}
    ]
}

req = urllib.request.Request(
    url,
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)

try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        print("Telegram setMyCommands response:", res)
except Exception as e:
    print("Error setting commands:", e)
