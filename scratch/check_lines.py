with open('dashboard/backend/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('Line 5445 to 5460:')
for idx in range(5445, min(len(lines), 5465)):
    print(f"{idx+1}: {repr(lines[idx])}")
