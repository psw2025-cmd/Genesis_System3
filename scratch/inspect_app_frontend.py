with open('c:/Genesis_System3_clean/dashboard/frontend/src/App.tsx', 'r', encoding='utf-8') as f:
    lines = [f.readline() for _ in range(120)]

for i, line in enumerate(lines):
    print(f"{i+1}: {line}", end="")
