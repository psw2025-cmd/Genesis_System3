from pathlib import Path

root = Path(r"c:\Genesis_System3_clean\dashboard\frontend\src")
for p in root.rglob("*.tsx"):
    txt = p.read_text(encoding="utf-8", errors="ignore")
    if "0 DAY HISTORY" in txt or "ML ACCURACY (SPEARMAN" in txt or "No ρ history" in txt:
        print(f"Match in {p.name}")
        for i, l in enumerate(txt.splitlines()):
            if "spearman" in l.lower() or "accuracy" in l.lower() or "equity" in l.lower():
                print(f"  L{i+1}: {l.strip()[:100]}")
