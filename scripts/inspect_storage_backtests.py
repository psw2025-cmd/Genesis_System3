from pathlib import Path

root = Path(r"c:\Genesis_System3_clean")
bt_dir = root / "storage" / "backtests"
if bt_dir.exists():
    for p in bt_dir.iterdir():
        print(f"{p.name} (is_dir={p.is_dir()}, size={p.stat().st_size if p.is_file() else 'dir'})")
