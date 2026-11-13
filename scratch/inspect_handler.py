from pathlib import Path

p = Path("content/app/app.py")
text = p.read_text(encoding="utf-8")
for i, line in enumerate(text.splitlines()[235:265]):
    print(f"{i+236}: {line}")
