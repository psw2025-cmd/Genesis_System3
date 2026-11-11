from pathlib import Path

p = Path("content/app/app.py")
text = p.read_text(encoding="utf-8")
lines = text.splitlines()
for i, line in enumerate(lines):
    if "/ui" in line and ("@app" in line or "def " in line):
        print(f"Match line {i+1}: {line}")
        for j in range(i, min(i+40, len(lines))):
            print(f"{j+1}: {lines[j]}")
