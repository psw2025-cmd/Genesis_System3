with open('dashboard/frontend/src/App.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.splitlines()
for i, l in enumerate(lines):
    if 'system-readiness' in l:
        print(f"Line {i+1}: {l.strip()}")
