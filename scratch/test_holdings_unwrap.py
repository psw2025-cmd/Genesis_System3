import os, sys
from pathlib import Path
WORKSPACE_ROOT = Path(r"C:\Genesis_System3_clean")
sys.path.insert(0, str(WORKSPACE_ROOT))

from core.brokers.dhan import dhan_readonly
from content.app.dhan_account_router import _unwrap_dhan_data, _normalize_holding, get_dhan_holdings

raw = dhan_readonly.get_holdings()
print("Raw type:", type(raw))
print("Raw keys:", raw.keys() if isinstance(raw, dict) else None)
items = _unwrap_dhan_data(raw, [])
print("Unwrapped items type:", type(items), "len:", len(items) if isinstance(items, list) else None)
holdings_res = get_dhan_holdings()
print("get_dhan_holdings result:", holdings_res)
