from pathlib import Path
import re

app_py = Path(r"c:\Genesis_System3_clean\dashboard\backend\app.py")
txt = app_py.read_text(encoding="utf-8", errors="ignore")

matches = [m.start() for m in re.finditer(r'cycle_count', txt, re.IGNORECASE)]
print(f"Found {len(matches)} matches for cycle_count in app.py")
for idx in matches[:10]:
    start = max(0, idx - 100)
    end = min(len(txt), idx + 300)
    print(txt[start:end])
    print("="*60)
