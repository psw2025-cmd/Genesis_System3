with open('dashboard/frontend/src/App.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r"activeTab\s*===\s*['\"]([^'\"]+)['\"]", text)
print('Tabs rendered in App.tsx:', len(matches), matches)
