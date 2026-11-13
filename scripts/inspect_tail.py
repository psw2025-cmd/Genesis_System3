with open('tests/test_telegram_downstream.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(140, len(lines)):
    print(f'{i+1}: {lines[i].rstrip()[:100]}')
