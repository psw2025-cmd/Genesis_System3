from pathlib import Path
import json

root = Path(r"c:\Genesis_System3_clean")
val_dir = root / "state" / "paper_validations"
if val_dir.exists():
    for p in val_dir.glob("*.json"):
        print(f"File: {p.name}")
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            print(f"  keys: {list(d.keys())[:8]}")
            if "costed_walk_forward" in d or "walk_forward" in d:
                print(f"  walk_forward: {d.get('costed_walk_forward') or d.get('walk_forward')}")
            if "trades" in d or "trade_count" in d:
                print(f"  trades: {d.get('trades') or d.get('trade_count')}")
        except Exception as e:
            print(f"  error: {e}")
