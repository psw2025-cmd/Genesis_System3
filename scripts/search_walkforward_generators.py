from pathlib import Path

root = Path(r"c:\Genesis_System3_clean")
for p in root.rglob("*.py"):
    if ".venv" in str(p) or ".git" in str(p):
        continue
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
        if "costed_walkforward" in txt or "recent_backtest_walkforward_proof" in txt:
            print(f"Match in {p.relative_to(root)}")
            for i, l in enumerate(txt.splitlines()):
                if "costed_walkforward" in l or "recent_backtest_walkforward_proof" in l:
                    print(f"  L{i+1}: {l.strip()[:100]}")
    except Exception:
        pass
