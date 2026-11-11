import json

with open('.agy-proof/contract.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print('Checks in contract.json:')
for c in d.get('checks', []):
    print(f"  ID: {c.get('id')}")
    print(f"  Command: {c.get('command')}")
    print(f"  Expected exit: {c.get('expected_exit_code')}")
