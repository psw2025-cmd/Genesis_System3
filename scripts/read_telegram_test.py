with open('tests/test_telegram_downstream.py', 'r', encoding='utf-8') as f:
    text = f.read()

print('Length of file:', len(text))
for line in text.splitlines()[:50]:
    print(line)
