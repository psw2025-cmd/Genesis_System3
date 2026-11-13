with open('dashboard/backend/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(5455, min(len(lines), 5540)):
    print(f"{i+1}: {repr(lines[i][:60])}")
