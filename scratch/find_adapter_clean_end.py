with open('dashboard/backend/chain_adapter.py', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('<!-- OWNER-AUTONOMOUS-COMPLETION-v2 BEGIN -->')
if idx != -1:
    print('Found markdown at index:', idx)
    print('Clean python code ends around:')
    print(text[idx-200:idx])
else:
    print('Markdown not found in chain_adapter.py')
