import os, sys
from pathlib import Path

WORKSPACE_ROOT = Path(r"C:\Genesis_System3_clean")
sys.path.insert(0, str(WORKSPACE_ROOT))

# Force reload env
from core.brokers.dhan import dhan_readonly

# Reset any cached credentials
dhan_readonly._CLIENT_ID = None
dhan_readonly._ACCESS_TOKEN = None

profile = dhan_readonly.get_profile()
print("Direct dhan_readonly Profile result:")
print(profile)

funds = dhan_readonly.get_funds()
print("Direct dhan_readonly Funds result:")
print(funds)

holdings = dhan_readonly.get_holdings()
print("Direct dhan_readonly Holdings result:")
print("Count:", len(holdings.get("data", [])) if isinstance(holdings.get("data"), list) else holdings)
