from pathlib import Path

p = Path("content/app/app.py")
text = p.read_text(encoding="utf-8")
lines = text.splitlines()
for i, line in enumerate(lines):
    if '@app.get("/api/market"' in line:
        for j in range(i, min(i+40, len(lines))):
            print(f"{j+1}: {lines[j]}")
        break
