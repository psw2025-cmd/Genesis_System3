with open('content/app/app.py', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f, 1):
        if '/api/ml' in line or '/api/paper' in line:
            if '@app.get' in line or '@app.post' in line:
                print(f'{idx}: {line.strip()}')
