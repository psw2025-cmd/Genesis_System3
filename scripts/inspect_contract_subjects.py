import json

with open('.agy-proof/contract.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print('subject_files:', d.get('subject_files'))
print('artifacts:', d.get('artifacts'))
print('checks:', len(d.get('checks', [])))
for c in d.get('checks', []):
    print('Check ID:', c.get('id'), 'Command:', c.get('command'))
