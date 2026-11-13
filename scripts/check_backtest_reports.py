from pathlib import Path
import json

root = Path(r"c:\Genesis_System3_clean")
reports_dir = root / "reports" / "latest"

print("--- Listing reports/latest subdirectories ---")
for p in reports_dir.iterdir():
    if p.is_dir():
        print(f"Directory: {p.name}")
        for f in p.glob("*.json"):
            print(f"  {f.name} ({f.stat().st_size} bytes)")
    elif p.is_file():
        print(f"File: {p.name} ({p.stat().st_size} bytes)")
