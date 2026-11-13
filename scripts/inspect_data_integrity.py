from pathlib import Path

root = Path(r"c:\Genesis_System3_clean\dashboard\frontend\src")
for p in root.rglob("*.tsx"):
    txt = p.read_text(encoding="utf-8", errors="ignore")
    if "Costed walk-forward" in txt or "costed_walk_forward" in txt or "walk-forward" in txt.lower():
        print(f"Match in {p.name}")
        for i, l in enumerate(txt.splitlines()):
            if "walk-forward" in l.lower() or "costed" in l.lower():
                print(f"  L{i+1}: {l.strip()[:100]}")
