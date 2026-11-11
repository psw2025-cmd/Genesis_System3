import subprocess
import time
import urllib.request
import os
import signal

# 1. Find process listening on port 8008 using netstat
cmd = "netstat -ano | findstr :8008 | findstr LISTENING"
output = subprocess.getoutput(cmd)
print("Listening processes on 8008:\n", output)

for line in output.strip().splitlines():
    parts = line.strip().split()
    if len(parts) >= 5 and "LISTENING" in parts:
        pid = int(parts[-1])
        print(f"Killing PID {pid}...")
        try:
            os.kill(pid, signal.SIGTERM)
        except Exception as e:
            subprocess.run(f"taskkill /F /PID {pid}", shell=True)

time.sleep(1)
print("Port 8008 cleared.")
