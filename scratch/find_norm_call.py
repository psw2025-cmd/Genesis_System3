with open('dashboard/backend/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'normalize_index_chain_exchange' in l:
        print(f"Line {i+1}:")
        print(''.join(lines[max(0, i-25):min(len(lines), i+25)]))
