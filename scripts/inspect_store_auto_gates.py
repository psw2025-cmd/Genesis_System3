from pathlib import Path

root = Path(r"c:\Genesis_System3_clean\dashboard\frontend\src")
for p in root.rglob("*.ts*"):
    txt = p.read_text(encoding="utf-8", errors="ignore")
    if "/api/auto_gates" in txt or "autoGates:" in txt:
        print(f"Match in {p.name}")
        for i, l in enumerate(txt.splitlines()):
            if "/api/auto_gates" in l or "autogates" in l.lower() or "stale" in l.lower():
                print(f"  L{i+1}: {l.strip()[:110]}")
