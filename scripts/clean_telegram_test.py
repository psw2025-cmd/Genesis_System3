with open('tests/test_telegram_downstream.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

valid_lines = []
for line in lines:
    if '<!--' in line or 'Evidence Integrity Policy' in line:
        break
    valid_lines.append(line)

print(f'Preserving {len(valid_lines)} valid python lines (out of {len(lines)} total).')
with open('tests/test_telegram_downstream.py', 'w', encoding='utf-8') as f:
    f.writelines(valid_lines)

print('Cleaned tests/test_telegram_downstream.py successfully.')
