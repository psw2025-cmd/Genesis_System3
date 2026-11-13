from pathlib import Path

p = Path("content/app/app.py")
text = p.read_text(encoding="utf-8")
for i, line in enumerate(text.splitlines()[:50]):
    print(f"{i+1}: {line}")
