import os
import subprocess
import sys

env = os.environ.copy()
env["BACKEND_URL"] = "https://genesis-system3-web-802404398783.asia-south1.run.app"
env["DASHBOARD_URL"] = "https://genesis-system3-web-802404398783.asia-south1.run.app/ui"

res = subprocess.run([sys.executable, "tools/qc_runtime_anomaly_audit.py"], env=env, capture_output=True, text=True)
print("STDOUT:", res.stdout)
print("STDERR:", res.stderr)
print("EXIT CODE:", res.returncode)
