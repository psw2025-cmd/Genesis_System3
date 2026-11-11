import json
from pathlib import Path
import hashlib

def digest(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

with open('.agy-proof/receipt.json', 'r', encoding='utf-8') as f:
    receipt = json.load(f)

root = Path(receipt['workspace']).resolve()
items = receipt.get('artifacts', []) + receipt.get('subjects', []) + [receipt['contract']]

for item in items:
    p = Path(item['path'])
    cur_hash = digest(p) if p.is_file() else 'MISSING'
    rec_hash = item.get('sha256')
    matches = (cur_hash == rec_hash)
    print(f"{item['path']}: matches={matches}")
    if not matches:
        print(f"  current: {cur_hash}")
        print(f"  receipt: {rec_hash}")
