with open('dashboard/backend/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('Total lines in app.py:', len(lines))
print('Lines 5410 to 5440:')
for idx in range(5410, min(len(lines), 5450)):
    print(f"{idx+1}: {repr(lines[idx])}")
