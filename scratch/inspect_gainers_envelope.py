from pathlib import Path

p = Path("content/app/app.py")
lines = p.read_text(encoding="utf-8").splitlines()
for i in range(790, min(840, len(lines))):
    print(f"{i+1}: {lines[i]}")
