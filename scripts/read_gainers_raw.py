with open('state/market_top_ce_pe.json', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

print('File length:', len(text))
print('First 500 chars:')
print(text[:500])
