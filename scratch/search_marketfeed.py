import os
from pathlib import Path

root = Path(".")
for p in root.rglob("*.py"):
    if any(part in p.parts for part in [".git", ".pytest_cache", ".venv", "__pycache__"]):
        continue
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
        if "marketfeed" in txt:
            print(f"Found marketfeed in: {p}")
    except Exception:
        pass
