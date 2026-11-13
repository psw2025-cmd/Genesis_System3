with open('tests/test_telegram_downstream.py', 'r', encoding='utf-8') as f:
    text = f.read()

print('First 40 lines of test_telegram_downstream.py:')
for line in text.splitlines()[:40]:
    print('  ', line[:100])
