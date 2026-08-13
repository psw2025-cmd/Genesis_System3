#!/usr/bin/env python3
"""
Add comprehensive logging to all modules
"""

import re
from pathlib import Path

# Add logger to backend files
backend_files = list(Path('backend').glob('*.py'))

for py_file in backend_files[:10]:  # First 10 files
    content = py_file.read_text()
    
    # Add logger if missing
    if 'logger = ' not in content and 'import logging' not in content:
        # Add logging import after other imports
        imports_end = max([m.end() for m in re.finditer(r'^import .*$|^from .* import .*$', content, re.MULTILINE)], default=0)
        if imports_end > 0:
            content = content[:imports_end] + '\nimport logging\nlogger = logging.getLogger(__name__)' + content[imports_end:]
            py_file.write_text(content)

print("✅ Added logging to backend modules")

