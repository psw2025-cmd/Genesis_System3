with open('dashboard/frontend/src/components/Sidebar.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r"id:\s*['\"]([^'\"]+)['\"]", text)
print('Count of tabs in Sidebar.tsx:', len(matches))
print('List of tabs:', matches)
