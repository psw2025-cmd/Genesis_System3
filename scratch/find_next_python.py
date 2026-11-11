with open('dashboard/backend/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('Searching for python code after line 5465...')
for i in range(5465, len(lines)):
    line = lines[i].strip()
    if line.startswith('def ') or line.startswith('@app.') or line.startswith('async def '):
        print(f"Found code at line {i+1}: {line}")
        break
