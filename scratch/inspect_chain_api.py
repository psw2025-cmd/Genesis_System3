import os

with open('dashboard/backend/app.py', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if '@app.get("/api/chain/{symbol}")' in l:
        print(f"Found /api/chain/{{symbol}} at line {i+1}")
        for j in range(i, min(i+150, len(lines))):
            line = lines[j]
            if any(k in line for k in ["iv_percentile", "oi_change", "return {", "result =", "pcr"]):
                print(f"Line {j+1}: {line.strip()[:100]}")
