from pathlib import Path

app_py = Path(r"c:\Genesis_System3_clean\dashboard\backend\app.py")
txt = app_py.read_text(encoding="utf-8", errors="ignore")

lines = txt.splitlines()
for i, l in enumerate(lines):
    if "_synthesize_operational_alerts" in l:
        print(f"Line {i+1}: {l}")
        for j in range(i, min(len(lines), i + 80)):
            print(f"  {j+1}: {lines[j]}")
        break
