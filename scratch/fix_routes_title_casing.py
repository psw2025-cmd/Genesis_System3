import shutil
from pathlib import Path

p = Path("content/app/templates/premium.html")
text = p.read_text(encoding="utf-8")
old = '<div class="card-title">AUTO-FOUND @app.get API ROUTES'
new = '<div class="card-title">Auto-Found @app.get API ROUTES'
if old in text:
    text = text.replace(old, new, 1)
    p.write_text(text, encoding="utf-8")
    print("Updated premium.html with Auto-Found @app.get API ROUTES")
else:
    print("Pattern not found in premium.html")

dest = Path("C:/content/app/templates/premium.html")
if dest.parent.exists():
    shutil.copy2(p, dest)
    print("Synced to C:/content/app/templates/premium.html")
