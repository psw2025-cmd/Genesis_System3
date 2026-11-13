path = "content/app/templates/premium.html"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

target = '<script src="https://cdn.jsdelivr.net/npm/chart.js" defer>'
replacement = '<script src="https://cdn.jsdelivr.net/npm/chart.js" defer></script>\n  <script>'

if target in text:
    text = text.replace(target, replacement, 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print("Fixed unclosed script tag on line 7!")
else:
    print("Target not found or already closed.")
