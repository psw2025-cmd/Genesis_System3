with open('dashboard/backend/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if '@app.get("/api/chain/{underlying}")' in l:
        print(''.join(lines[i:i+60]))
        break
