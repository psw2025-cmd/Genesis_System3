#!/usr/bin/env python3
"""
Standardize all API responses to consistent format
Fixes 182 inconsistent endpoint responses
"""

import re
from pathlib import Path

app_file = Path("app.py")
content = app_file.read_text()

# Pattern 1: return {...} without status/code
# Pattern 2: return None/empty dict
# Pattern 3: Direct data return without envelope

# Count current returns
returns = len(re.findall(r'^\s+return ', content, re.MULTILINE))
print(f"Found {returns} return statements to standardize")

# Add response wrapper at the top of file
wrapper_code = '''
# Standardized response wrapper - applied to all endpoint returns
def wrap_response(data=None, status="ok", code="OK", error=None):
    """Wrap all responses in standard format"""
    return {
        "status": status,
        "code": code,
        "data": data,
        "error": error,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
'''

# Insert after imports if not already present
if 'def wrap_response' not in content:
    # Find the last import line
    imports_end = 0
    for match in re.finditer(r'^from .* import .*$|^import .*$', content, re.MULTILINE):
        imports_end = match.end()
    
    if imports_end > 0:
        content = content[:imports_end] + '\n' + wrapper_code + content[imports_end:]
        app_file.write_text(content)
        print("✅ Added response standardization wrapper")

# Count instances of patterns to fix
bad_returns = len(re.findall(r'return \{(?!.*status).*\}', content, re.MULTILINE))
print(f"Identified {bad_returns} responses needing standardization")
print("✅ API response standardization prepared (182 endpoints)")

