with open('dashboard/backend/chain_adapter.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'OWNER-AUTONOMOUS' in l or 'Evidence Integrity Policy' in l:
        print(f"Line {i+1}: {l.strip()[:60]}")
