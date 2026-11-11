with open('dashboard/backend/chain_adapter.py', 'r', encoding='utf-8') as f:
    text = f.read()

print('Length of chain_adapter.py:', len(text))
print('Last 500 chars:')
print(text[-500:])
