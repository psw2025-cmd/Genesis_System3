import os, re

matches = []
for root, dirs, files in os.walk('dashboard/frontend/src'):
    for f in files:
        if f.endswith('.tsx') or f.endswith('.ts'):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8') as fh:
                txt = fh.read()
                if 'system-readiness' in txt:
                    matches.append((p, [m.start() for m in re.finditer(r'system-readiness', txt)]))

for p, m in matches:
    print(p, len(m))
