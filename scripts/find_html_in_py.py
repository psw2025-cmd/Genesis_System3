with open('tests/test_telegram_downstream.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('Total lines in file:', len(lines))
for i, line in enumerate(lines):
    if '<!--' in line:
        print(f'HTML comment starts at line {i+1}')
        break
