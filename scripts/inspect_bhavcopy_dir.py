from pathlib import Path

root = Path(r"c:\Genesis_System3_clean")
bhav_dir = root / "storage" / "bhavcopy"
print("bhav_dir exists:", bhav_dir.exists())
if bhav_dir.exists():
    files = list(bhav_dir.iterdir())
    print(f"Total files in {bhav_dir}: {len(files)}")
    for f in files[:20]:
        print(f"  {f.name} ({f.stat().st_size} bytes)")
else:
    print("Does not exist. Let us check storage/ overall:")
    storage_dir = root / "storage"
    if storage_dir.exists():
        for p in storage_dir.iterdir():
            print(f"  {p.name} (is_dir={p.is_dir()})")
