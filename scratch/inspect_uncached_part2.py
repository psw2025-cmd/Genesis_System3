with open('dashboard/backend/app.py', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('async def _get_chain_uncached')
if idx != -1:
    print(text[idx+500:idx+3000])
