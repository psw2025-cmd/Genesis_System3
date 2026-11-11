from pathlib import Path

p = Path("content/app/verified_market.py")
text = p.read_text(encoding="utf-8")
for i, line in enumerate(text.splitlines()[:60]):
    print(f"{i+1}: {line}")
