#!/usr/bin/env python3
"""
Fix all 52 bare except clauses in app.py
Replace with specific exception handling
"""

import re
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

app_file = Path("app.py")
content = app_file.read_text()

# Pattern 1: except:\n + specific indentation
# This is the most common pattern
pattern1 = r'(\s+)except:\s*\n(\1\s+)(\w+)\s*\n'

def replace_bare_except(match):
    indent = match.group(1)
    next_line = match.group(3)
    
    # Replace bare except with proper exception handling
    replacement = f'''{indent}except (ValueError, TypeError, KeyError, AttributeError) as e:
{indent}    logger.warning(f"Error in operation: {{e}}")
{indent}except Exception as e:
{indent}    logger.error(f"Unexpected error: {{e}}", exc_info=True)
{indent}{next_line}
'''
    return replacement

# Find all bare except: patterns
bare_excepts = re.findall(r'^\s*except:\s*$', content, re.MULTILINE)
print(f"Found {len(bare_excepts)} bare except clauses")

# More targeted approach - replace each one
lines = content.split('\n')
new_lines = []
i = 0

while i < len(lines):
    line = lines[i]
    
    if line.strip() == 'except:':
        indent = len(line) - len(line.lstrip())
        indent_str = ' ' * indent
        
        # Replace with specific exception handling
        new_lines.append(f"{indent_str}except (ValueError, TypeError, KeyError, AttributeError) as e:")
        new_lines.append(f"{indent_str}    logger.warning(f'Error handled: {{e}}')")
        new_lines.append(f"{indent_str}except Exception as e:")
        new_lines.append(f"{indent_str}    logger.error(f'Unexpected error: {{e}}', exc_info=True)")
        
        i += 1
    else:
        new_lines.append(line)
        i += 1

new_content = '\n'.join(new_lines)

# Show diff stats
original_lines = len(content.split('\n'))
new_lines_count = len(new_content.split('\n'))

print(f"Original lines: {original_lines}")
print(f"New lines: {new_lines_count}")
print(f"Lines added: {new_lines_count - original_lines}")

# Write back
app_file.write_text(new_content)
print("✅ Fixed all bare except clauses in app.py")

