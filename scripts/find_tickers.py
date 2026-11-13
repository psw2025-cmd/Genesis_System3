import re

with open(r'content/app/templates/premium.html', 'r', encoding='utf-8') as f:
    text = f.read()

print('Searching for ticker sections:')
for m in re.finditer(r'<div[^>]*ticker[^>]*>.*?(?=</div>\s*</div>)', text, re.DOTALL | re.IGNORECASE):
    block = m.group(0)[:600]
    print('--- TICKER BLOCK ---')
    print(block.encode('ascii', errors='replace').decode('ascii'))

print('\nSearching for nifty references in template:')
for i, line in enumerate(text.splitlines()):
    if any(k in line.lower() for k in ['nifty 50', '24,148', '23,440', 't-nifty']):
        print(f'Line {i+1}: {line.strip()[:100].encode("ascii", errors="replace").decode("ascii")}')
