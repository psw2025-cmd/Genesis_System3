from pathlib import Path

p = Path("tests/test_genesis_500_routes.py")
text = p.read_text(encoding="utf-8")
for i, line in enumerate(text.splitlines()[50:75]):
    print(f"{i+51}: {line}")
