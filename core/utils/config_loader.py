import json
import os

CONFIG_FILE = "config/system3_config.json"

DEFAULT_CONFIG = {
    "market": "NSE",
    "live_mode": False,
    "log_level": "INFO",
    "data_folder": "storage/history",
    "live_data_folder": "storage/live",
    "update_interval_sec": 5,
}


def ensure_config():
    os.makedirs("config", exist_ok=True)
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG
    else:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)


def update_config(key, value):
    cfg = ensure_config()
    cfg[key] = value
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=4)
