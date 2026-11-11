import json

with open('.agy-proof/contract.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print('Contract scope:', d.get('scope'))
print('Requirements count:', len(d.get('requirements', [])))
for req in d.get('requirements', []):
    print(f"  {req.get('id')}: {req.get('description')}")
