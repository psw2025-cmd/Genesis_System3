import os
from pathlib import Path

root = Path("c:/Genesis_System3_clean")
for p in [
    root / "outputs" / "paper_pnl.csv",
    root / "outputs" / "paper_pnl_summary.json",
    root / "outputs" / "paper_trades_live.csv",
    root / "outputs" / "pnl_summary.json",
    root / "outputs" / "pnl_live.json",
    root / "state" / "pnl_summary.json",
]:
    print(f"File {p.name}: exists={p.exists()}, size={p.stat().st_size if p.exists() else 0}")
    if p.exists() and p.stat().st_size < 1000:
        print(p.read_text(encoding="utf-8")[:500])
        print("---")
