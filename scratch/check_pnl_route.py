with open('c:/Genesis_System3_clean/dashboard/backend/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'def get_pnl(' in line or '"/api/pnl"' in line:
        print(f"Line {i+1}: {line}")
        for j in range(max(0, i-5), min(len(lines), i+40)):
            print(f"{j+1}: {lines[j]}", end="")
        print("\n" + "="*50 + "\n")
