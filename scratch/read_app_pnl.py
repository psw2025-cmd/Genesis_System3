with open('c:/Genesis_System3_clean/dashboard/backend/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(6177, min(len(lines), 6300)):
    print(f"{i+1}: {lines[i]}", end="")
