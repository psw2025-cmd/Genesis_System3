with open(r'content/app/templates/premium.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(330, 385):
    if i < len(lines):
        line = lines[i].rstrip().encode('ascii', errors='replace').decode('ascii')
        print(f'{i+1}: {line}')
