from pathlib import Path

root = Path(r"c:\Genesis_System3_clean")
mv_dir = root / "state" / "market_validations"
print("mv_dir exists:", mv_dir.exists())
if mv_dir.exists():
    for p in mv_dir.glob("*.json"):
        print(f"File: {p.name} ({p.stat().st_size} bytes)")
else:
    print("Does not exist!")
