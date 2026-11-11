from pathlib import Path
import re

app_py = Path(r"c:\Genesis_System3_clean\dashboard\backend\app.py")
txt = app_py.read_text(encoding="utf-8", errors="ignore")

matches = [m.start() for m in re.finditer(r'@app\.get\("/api/backtest/results"\)', txt)]
print(f"Found {len(matches)} matches for @app.get('/api/backtest/results')")
for idx in matches:
    print(txt[idx:idx+1000])
    print("="*60)
