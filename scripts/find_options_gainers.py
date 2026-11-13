with open(r'content/app/app.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = re.search(r'@app\.get\("/api/options/gainers".*?return\s+envelope', text, re.DOTALL)
if m:
    print('Found /api/options/gainers:')
    for line in m.group(0).splitlines()[:50]:
        print('  ', line[:120])
else:
    print('Not found!')
