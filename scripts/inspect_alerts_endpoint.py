from pathlib import Path
import re

app_py = Path(r"c:\Genesis_System3_clean\dashboard\backend\app.py")
txt = app_py.read_text(encoding="utf-8", errors="ignore")

matches = [m.start() for m in re.finditer(r'@app\.get\("/api/alerts', txt)]
print(f"Found {len(matches)} matches for @app.get('/api/alerts')")
for idx in matches:
    print(txt[idx:idx+800])
    print("="*60)
