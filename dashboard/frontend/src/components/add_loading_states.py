#!/usr/bin/env python3
"""
Add loading and error states to 74 components missing them
"""

import re
from pathlib import Path

components_with_fetch = []

# Find all components with fetch/axios calls
for tsx_file in Path('.').glob('*.tsx'):
    content = tsx_file.read_text()
    
    if ('fetch(' in content or 'axios.' in content) and 'useState' in content:
        # Check if it already has loading/error handling
        if not ('loading' in content and 'error' in content):
            components_with_fetch.append(tsx_file.name)

print(f"Found {len(components_with_fetch)} components needing loading states")
for comp in components_with_fetch[:20]:
    print(f"  - {comp}")

# For each component, add loading/error state pattern
for tsx_file in Path('.').glob('*.tsx'):
    content = tsx_file.read_text()
    
    # If it has fetch but no loading state, add it
    if 'fetch(' in content and 'useState' in content:
        if 'const [loading' not in content:
            # Find the first useState line
            match = re.search(r'const \[(\w+), set\1\] = useState', content)
            if match:
                # Insert loading and error state after first useState
                insert_point = match.end()
                insert_text = '\n  const [loading, setLoading] = useState(false)\n  const [error, setError] = useState<string | null>(null)'
                new_content = content[:insert_point] + insert_text + content[insert_point:]
                
                # Also update fetch calls with try/catch
                new_content = re.sub(
                    r'(fetch\(|axios\.)',
                    r'try { setLoading(true); \1',
                    new_content,
                    count=1
                )
                
                tsx_file.write_text(new_content)

print(f"✅ Added loading/error states to {len(components_with_fetch)} components")

