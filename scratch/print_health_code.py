with open('c:/Genesis_System3_clean/dashboard/backend/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if '@app.get("/api/health")' in l:
        print(f"Health route starts at {i+1}")
        for j in range(i, min(len(lines), i+100)):
            print(f"{j+1}: {lines[j]}", end="")
        break
