from pathlib import Path

p = Path("content/app/templates/premium.html")
text = p.read_text(encoding="utf-8")
old = '<div class="card-title">AUTO-FOUND API ROUTES'
new = '<div class="card-title">AUTO-FOUND @app.get API ROUTES'
if old in text:
    p.write_text(text.replace(old, new, 1), encoding="utf-8")
    print("Updated premium.html with AUTO-FOUND @app.get API ROUTES")
else:
    print("Pattern not found in premium.html")
