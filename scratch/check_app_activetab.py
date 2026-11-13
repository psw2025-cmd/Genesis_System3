with open('dashboard/frontend/src/App.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.splitlines()
print('Total lines in App.tsx:', len(lines))
for i, l in enumerate(lines):
    if 'activeTab' in l:
        print(f"Line {i+1}: {l.strip()[:80]}")
