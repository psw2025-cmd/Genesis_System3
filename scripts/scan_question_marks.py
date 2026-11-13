with open(r'content/app/templates/premium.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

suspicious = []
for i, line in enumerate(lines):
    # Check if there are any raw '?' preceding numbers like ?23,440
    import re
    if re.search(r'\?[\d,]+\.\d{2}', line) or '? 1,' in line or 'GENESIS SYSTEM3 ?' in line:
        suspicious.append((i+1, line.strip()))

print(f'Remaining suspicious ? count: {len(suspicious)}')
for lineno, l in suspicious[:10]:
    print(f'  L{lineno}: {l.encode("ascii", errors="replace").decode("ascii")}')
