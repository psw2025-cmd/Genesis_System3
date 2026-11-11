import os, re

for root, dirs, files in os.walk(r'content/app'):
    for file in files:
        if file.endswith(('.py', '.html', '.js', '.json')):
            p = os.path.join(root, file)
            with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if '24,148' in content or '24148' in content or '51,500' in content or '79,389' in content:
                    print(f'Found match in {p}:')
                    for line in content.splitlines():
                        if any(k in line for k in ['24,148', '24148', '51,500', '79,389']):
                            print('  ', line[:120])
