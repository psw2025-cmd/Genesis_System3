import os
import json
from datetime import datetime
from core.utils.helpers import ensure_folder


HISTORY_ROOT = "storage/history"
LIVE_ROOT = "storage/live"


def _timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def save_json_snapshot(data: dict, symbol: str, folder: str = HISTORY_ROOT) -> str:
    """
    Save a JSON snapshot for a given symbol and return the file path.
    """
    ensure_folder(folder)
    fname = f"{symbol}_{_timestamp()}.json"
    fpath = os.path.join(folder, fname)
    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return fpath


def list_files(symbol: str, folder: str = HISTORY_ROOT):
    """
    List all stored files for a symbol.
    """
    ensure_folder(folder)
    return [os.path.join(folder, f) for f in os.listdir(folder) if f.startswith(symbol + "_") and f.endswith(".json")]
