from pathlib import Path
import re

app_py = Path(r"c:\Genesis_System3_clean\dashboard\backend\app.py")
txt = app_py.read_text(encoding="utf-8", errors="ignore")

for endpoint in ["/api/pnl/equity-curve", "/api/accuracy_trend", "/api/ml/performance", "/api/paper/trades"]:
    matches = [m.start() for m in re.finditer(re.escape(endpoint), txt)]
    print(f"Endpoint {endpoint}: {len(matches)} matches")
    for idx in matches[:2]:
        print(txt[idx-50:idx+400])
        print("="*60)
