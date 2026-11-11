import os
from pathlib import Path

root = Path(r"c:\Genesis_System3_clean")
frontend_src = root / "dashboard" / "frontend" / "src"

print("--- Searching for autoGates in frontend src ---")
for p in frontend_src.rglob("*.tsx"):
    txt = p.read_text(encoding="utf-8", errors="ignore")
    if "autoGates" in txt or "auto_gates" in txt:
        print(f"Match in {p.relative_to(root)}")
        for i, line in enumerate(txt.splitlines()):
            if "autogates" in line.lower():
                print(f"  L{i+1}: {line.strip()[:100]}")

print("\n--- Searching for STALE banner logic ---")
for p in frontend_src.rglob("*.tsx"):
    txt = p.read_text(encoding="utf-8", errors="ignore")
    if "STALE" in txt or "gates" in txt.lower():
        if "AutonomousLoopBanner" in p.name or "TruthStrip" in p.name or "TopBar" in p.name:
            print(f"Banner match in {p.relative_to(root)}")
            for i, line in enumerate(txt.splitlines()):
                if "stale" in line.lower() or "gates" in line.lower():
                    print(f"  L{i+1}: {line.strip()[:100]}")
