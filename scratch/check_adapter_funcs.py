with open('dashboard/backend/chain_adapter.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
funcs = re.findall(r'def\s+([a-zA-Z0-9_]+)', text)
print('Functions in chain_adapter.py:', funcs)
