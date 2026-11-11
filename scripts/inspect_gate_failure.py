import json

with open('.agy-proof/contract.json', 'r', encoding='utf-8') as f:
    c = json.load(f)

print('Checks in contract.json:')
print(json.dumps(c.get('checks'), indent=2))

with open('.agy-proof/receipt.json', 'r', encoding='utf-8') as f:
    r = json.load(f)

print('Receipt summary:')
print('overall:', r.get('overall'))
print('checks:', json.dumps(r.get('checks'), indent=2))
