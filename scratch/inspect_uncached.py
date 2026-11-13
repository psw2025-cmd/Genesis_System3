with open('dashboard/backend/app.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
match = re.search(r'_CHAIN_LIVE_TIMEOUT_CLOSED_S\s*=\s*([^\n]+)', text)
if match:
    print('_CHAIN_LIVE_TIMEOUT_CLOSED_S =', match.group(0))

idx = text.find('async def _get_chain_uncached')
if idx != -1:
    print(text[idx:idx+2000])
